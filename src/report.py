import json
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from src.config import llm


REPORT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
    background: #fff;
}

@page {
    size: A4;
    margin: 25mm 20mm;
}

.report-header {
    text-align: center;
    padding: 40px 0 30px;
    border-bottom: 3px solid #2563eb;
    margin-bottom: 30px;
}

.report-header h1 {
    font-size: 24pt;
    font-weight: 700;
    color: #1e3a5f;
    margin-bottom: 8px;
}

.report-header .subtitle {
    font-size: 11pt;
    color: #64748b;
}

h2 {
    font-size: 16pt;
    font-weight: 700;
    color: #1e3a5f;
    margin: 30px 0 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

h3 {
    font-size: 13pt;
    font-weight: 600;
    color: #334155;
    margin: 20px 0 10px;
}

h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #475569;
    margin: 15px 0 8px;
}

p { margin-bottom: 10px; }

ul, ol {
    margin: 8px 0 15px 20px;
}

li { margin-bottom: 4px; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
}

th {
    background: #1e3a5f;
    color: #fff;
    font-weight: 600;
    padding: 10px 12px;
    text-align: left;
}

td {
    padding: 8px 12px;
    border-bottom: 1px solid #e2e8f0;
}

tr:nth-child(even) td {
    background: #f8fafc;
}

.company-section {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 20px;
    margin: 15px 0;
    page-break-inside: avoid;
}

.badge {
    display: inline-block;
    background: #2563eb;
    color: #fff;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 9pt;
    font-weight: 500;
    margin-right: 5px;
}

.pros { color: #16a34a; }
.cons { color: #dc2626; }

.footer {
    margin-top: 40px;
    padding-top: 15px;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    font-size: 9pt;
    color: #94a3b8;
}

strong { font-weight: 600; }
"""


def generate_final_report(company_name: str, analyses: list) -> str:
    """수집된 분석 데이터를 종합하여 최종 보고서 작성"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 경쟁사 분석 전문가입니다. 수집된 데이터를 종합하여 전문적인 비즈니스 보고서를 작성하세요."),
        ("human", "기업명: {company}\n분석 날짜: {date}\n---\n{data}"),
    ])

    chain = prompt | llm
    result = chain.invoke({
        "company": company_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "data": json.dumps(analyses, ensure_ascii=False),
    })
    return result.content


def render_to_html(report_text: str) -> dict:
    """비즈니스 보고서를 HTML로 변환 (CSS는 고정 템플릿 사용)"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """비즈니스 리포트 텍스트를 HTML <body> 내부 콘텐츠로 변환하세요.

## 규칙
- <html>, <head>, <body>, <style> 태그는 절대 포함하지 마세요. 본문 콘텐츠만 반환하세요.
- 반드시 아래 구조로 시작하세요:
  <div class="report-header">
    <h1>보고서 제목</h1>
    <div class="subtitle">분석 날짜 등</div>
  </div>
- 각 경쟁사 분석은 <div class="company-section">으로 감싸세요.
- 데이터 비교에는 반드시 <table>을 사용하세요.
- 장점은 <span class="pros">✔</span>, 단점은 <span class="cons">✘</span>를 붙이세요.
- 기술 스택, 카테고리 등은 <span class="badge">태그</span>로 감싸세요.
- 마지막에 <div class="footer">자동 생성 보고서</div>를 추가하세요.
- 코드블록(```)으로 감싸지 마세요. 순수 HTML만 반환하세요."""),
        ("human", "{text}"),
    ])

    chain = prompt | llm
    result = chain.invoke({"text": report_text})
    html = result.content.strip()

    # LLM이 코드블록으로 감싼 경우 제거
    if html.startswith("```html"):
        html = html.split("```html", 1)[1]
    if html.startswith("```"):
        html = html.split("```", 1)[1]
    if html.endswith("```"):
        html = html.rsplit("```", 1)[0]
    html = html.strip()

    return {"html": html, "css": REPORT_CSS}


def convert_to_pdf(html_content: str, css_content: str, output_path: str) -> str:
    """HTML + CSS를 PDF로 변환"""
    from weasyprint import HTML

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>{css_content}</style>
</head>
<body>
{html_content}
</body>
</html>"""

    HTML(string=full_html).write_pdf(output_path)
    return output_path
