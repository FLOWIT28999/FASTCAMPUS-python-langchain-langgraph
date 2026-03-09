# n8n 경쟁사 리서치 에이전트 → Python 코드 변환 가이드

> n8n으로 구현한 **"실시간 글로벌 시장 분석 및 경쟁사 리서치 에이전트"** 를
> LangChain + LangGraph 코드로 어떻게 구현할 수 있는지 정리한 문서입니다.

---

## 1. n8n 워크플로우 전체 구조

이 워크플로우는 기업 URL을 입력받으면, **Exa.ai로 경쟁사를 탐색**하고,
**3개의 전문 에이전트**가 각 경쟁사를 순차 분석한 뒤, **PDF 보고서**를 생성합니다.

워크플로우는 **2개의 동일한 파이프라인**(경쟁사 분석 / 자사 분석)으로 구성되어 있습니다.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  1단계: 입력 처리                                                               │
│  기업 URL 입력 → Exa.ai (유사 경쟁사 탐색)                                     │
│                                                                                 │
│  2단계: 데이터 정제                                                             │
│  경쟁사_나누기 → 도메인_추출 → 중복_제거 → Limit(상위 3개)                     │
│                                                                                 │
│  3단계: 경쟁사별 순차 분석 루프 (Loop Over Items)                               │
│  ┌─────────────────────────────────────────────────────────────────────┐        │
│  │  각 경쟁사 URL에 대해:                                              │        │
│  │                                                                     │        │
│  │  [기업_분석_에이전트]  →  [기업_제품_오퍼링_에이전트]  →  [제품_평가_에이전트] │
│  │   ├── Gemini LLM            ├── Gemini LLM               ├── Gemini LLM     │
│  │   ├── Perplexity 도구       ├── Perplexity 도구           ├── Perplexity 도구│
│  │   ├── Tavily 도구           ├── Tavily 도구               ├── Tavily 도구    │
│  │   └── JSON 출력 파서        └── JSON 출력 파서            └── JSON 출력 파서 │
│  │                                                                     │        │
│  │  → Wait(2초) → 다음 경쟁사로 반복                                  │        │
│  └─────────────────────────────────────────────────────────────────────┘        │
│                                                                                 │
│  4단계: 보고서 생성                                                             │
│  Aggregate(집계) → 최종_보고서(Agent) → 렌더링(HTML/CSS 추출) → PDF 변환       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3개의 전문 에이전트 역할

| 에이전트 | 조사 내용 | 도구 |
|----------|----------|------|
| **기업_분석_에이전트** | 설립일, CEO, 투자/재무, 직원 수, 최신 뉴스 | Perplexity_finder + Tavily_finder |
| **기업_제품_오퍼링_에이전트** | 제품 기능, 가격 플랜, 기술 스택, 프로모션 | Perplexity_product + Tavily_product |
| **제품_평가_에이전트** | 리뷰 요약, 장단점, 사용자층, 평판 분석 | Perplexity_evaluator + Tavily_evaluator |

---

## 2. n8n 노드 ↔ 코드 매핑 테이블

### 1단계: 입력 처리

| n8n 노드 | 역할 | 배운 모듈 | Python 코드 |
|----------|------|----------|-------------|
| Exa.ai HTTP Request | 유사 경쟁사 탐색 (neural search) | **Python 챕터 08** (입출력) | `requests.post()` |

### 2단계: 데이터 정제

| n8n 노드 | 역할 | 배운 모듈 | Python 코드 |
|----------|------|----------|-------------|
| SplitOut (경쟁사_나누기) | results 배열을 개별 항목으로 분리 | **Python 챕터 04** (자료구조) | 리스트 순회 |
| Edit Fields (도메인_추출) | title, url 필드만 추출 | **Python 챕터 04** (딕셔너리) | `{"title": r["title"], "url": r["url"]}` |
| RemoveDuplicates (중복_제거) | URL 기준 중복 제거 | **Python 챕터 04** (집합/딕셔너리) | `{r["url"]: r for r in results}` |
| Limit | 상위 3개만 선택 | **Python 챕터 05** (제어 흐름) | 슬라이싱 `[:3]` |

### 3단계: 에이전트 루프

| n8n 노드 | 역할 | 배운 모듈 | Python 코드 |
|----------|------|----------|-------------|
| Loop Over Items | 경쟁사별 순차 반복 | **Python 챕터 05** (for 루프) / **LangGraph 모듈 03** | `for company in companies:` |
| Agent (3개) | 전문 리서치 에이전트 | **LangChain 모듈 09** / **LangGraph 모듈 05** | `create_tool_calling_agent` 또는 `ToolNode` |
| Perplexity Tool | 웹 검색 도구 (실시간) | **LangChain 모듈 09** (`@tool`) | `@tool` + Perplexity API |
| Tavily Tool | 웹 검색 도구 (보조) | **LangChain 모듈 09** (`@tool`) | `@tool` + `TavilySearchResults` |
| Structured Output Parser | JSON 스키마 강제 출력 | **LangChain 모듈 04** (출력 파서) | `PydanticOutputParser` |
| Wait (2초) | API 속도 제한 방지 | **Python 챕터 10** (모듈) | `time.sleep(2)` |

### 4단계: 보고서 생성

| n8n 노드 | 역할 | 배운 모듈 | Python 코드 |
|----------|------|----------|-------------|
| Aggregate | 모든 경쟁사 분석 결과 집계 | **Python 챕터 04** (리스트) | `all_results.append(result)` |
| 최종_보고서 (Agent) | 종합 분석 보고서 생성 | **LangChain 모듈 09** | Agent + 시스템 프롬프트 |
| 렌더링 (Information Extractor) | HTML + CSS 코드 추출 | **LangChain 모듈 04** | `PydanticOutputParser` |
| Convert HTML to PDF | HTML → PDF 변환 | - | `weasyprint` 또는 외부 API |

---

## 3. 파이프라인 구현: 코드로 변환

### 3.1 필요한 패키지

```python
# uv add langchain-google-genai langchain-community langgraph
# uv add langchain-text-splitters python-dotenv pydantic
# uv add tavily-python requests weasyprint
```

### 3.2 환경 설정 (모듈 00)

```python
import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv('.env')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
EXA_API_KEY = os.getenv('EXA_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
```

### 3.3 1단계: 입력 처리 — 경쟁사 탐색

**n8n의 Exa.ai_경쟁사_탐색 노드**는 HTTP POST로 유사 기업을 검색합니다.
Python 챕터 08(입출력)에서 배운 네트워크 요청 패턴을 활용합니다.

```python
# n8n의 Exa.ai HTTP Request 노드와 동일
def find_similar_companies(company_url: str) -> list:
    """Exa.ai API로 유사 경쟁사 탐색 (neural search)"""
    response = requests.post(
        "https://api.exa.ai/findSimilar",
        headers={
            "x-api-key": EXA_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "url": company_url,
            "type": "neural",
            "useAutoprompt": True,
            "contents": {"text": False},
            "excludeDomains": [company_url, "github.com", "linkedin.com"],
        },
    )
    return response.json().get("results", [])
```

### 3.4 2단계: 데이터 정제 — 분리, 추출, 중복 제거, 제한

n8n의 SplitOut → Edit Fields → RemoveDuplicates → Limit 노드 체인을
Python 챕터 04(자료구조)와 챕터 05(제어 흐름)에서 배운 패턴으로 구현합니다.

```python
def refine_competitors(results: list, max_count: int = 3) -> list:
    """n8n의 경쟁사_나누기 → 도메인_추출 → 중복_제거 → Limit 역할"""

    # 도메인_추출: title, url만 추출 (챕터 04: 딕셔너리)
    extracted = [{"title": r["title"], "url": r["url"]} for r in results]

    # 중복_제거: URL 기준 (챕터 04: 딕셔너리 활용)
    seen = {}
    unique = []
    for item in extracted:
        if item["url"] not in seen:
            seen[item["url"]] = True
            unique.append(item)

    # Limit: 상위 N개 (챕터 05: 슬라이싱)
    return unique[:max_count]
```

### 3.5 3단계: 3개 전문 에이전트 구현

#### 도구 정의 (모듈 09: `@tool` 데코레이터)

n8n에서는 Perplexity와 Tavily 노드를 에이전트에 연결했습니다.
코드에서는 모듈 09에서 배운 `@tool` 데코레이터로 동일한 도구를 만듭니다.

```python
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# n8n의 Tavily Tool 노드와 동일
@tool
def tavily_search(query: str) -> str:
    """웹에서 최신 정보를 검색합니다. 기업 정보, 재무 데이터, 뉴스 등을 찾을 때 사용하세요."""
    search = TavilySearchResults(max_results=5)
    results = search.invoke(query)
    return json.dumps(results, ensure_ascii=False)

# n8n의 Perplexity Tool 노드와 동일
@tool
def perplexity_search(query: str) -> str:
    """Perplexity AI로 기업 정보를 실시간 검색합니다."""
    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "기업 정보를 정확하게 조사하여 JSON으로 반환하세요."},
                {"role": "user", "content": query},
            ],
        },
    )
    return response.json()["choices"][0]["message"]["content"]
```

#### 출력 스키마 정의 (모듈 04: PydanticOutputParser)

n8n의 **Structured Output Parser** 노드는 JSON 스키마로 출력을 강제합니다.
모듈 04에서 배운 `PydanticOutputParser` + Pydantic `BaseModel`로 동일하게 구현합니다.

```python
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser

# n8n의 Structured Output Parser 스키마와 동일
class AnalysisTarget(BaseModel):
    name: str = Field(default="", description="기업명")
    domain: str = Field(default="", description="공식 홈페이지 주소")
    region: str = Field(default="", description="KR 또는 Global")

class CorporateIdentity(BaseModel):
    year_founded: str = Field(default="", description="설립 연도")
    hq_location: str = Field(default="", description="본사 소재지")
    current_ceo: dict = Field(default_factory=dict, description="CEO 정보")

class FinancialPerformance(BaseModel):
    total_funding_amount: str = Field(default="", description="총 투자 유치 금액")
    annual_revenue_latest: str = Field(default="", description="최근 연 매출액")
    valuation: str = Field(default="", description="기업 가치")

class CompanyAnalysis(BaseModel):
    """기업 분석 에이전트의 출력 스키마"""
    analysis_target: AnalysisTarget = Field(default_factory=AnalysisTarget)
    corporate_identity: CorporateIdentity = Field(default_factory=CorporateIdentity)
    financial_performance: FinancialPerformance = Field(default_factory=FinancialPerformance)
    operational_metrics: dict = Field(default_factory=dict)
    market_intelligence: dict = Field(default_factory=dict)

class ProductOffering(BaseModel):
    """기업 제품 오퍼링 에이전트의 출력 스키마"""
    features: list = Field(default_factory=list)
    pricing_plans: list = Field(default_factory=list)
    technology_stack: list = Field(default_factory=list)
    sources: list = Field(default_factory=list)

class ProductReview(BaseModel):
    """제품 평가 에이전트의 출력 스키마"""
    review_summary: dict = Field(default_factory=dict)
    top_pros: list = Field(default_factory=list)
    top_cons: list = Field(default_factory=list)
    notable_feedbacks: list = Field(default_factory=list)
    sources: list = Field(default_factory=list)

# 모듈 04에서 배운 파서 패턴
company_parser = PydanticOutputParser(pydantic_object=CompanyAnalysis)
product_parser = PydanticOutputParser(pydantic_object=ProductOffering)
review_parser = PydanticOutputParser(pydantic_object=ProductReview)
```

#### 에이전트 생성 (모듈 09: create_tool_calling_agent)

n8n의 3개 에이전트 노드를 모듈 09에서 배운 패턴으로 구현합니다.
각 에이전트는 **고유한 시스템 프롬프트 + 전용 도구 + JSON 출력 파서**를 가집니다.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

def create_research_agent(system_prompt: str, tools: list, parser) -> AgentExecutor:
    """모듈 09에서 배운 에이전트 생성 패턴 재활용"""

    # 파서의 format_instructions를 시스템 프롬프트에 추가 (모듈 04)
    # ⚠️ 주의: JSON 스키마의 중괄호가 ChatPromptTemplate 변수로 해석되므로 이스케이프 필요
    format_instructions = parser.get_format_instructions()
    format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")
    full_prompt = system_prompt + "\n\n" + format_instructions

    prompt = ChatPromptTemplate.from_messages([
        ("system", full_prompt),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),  # 모듈 09 필수 필드
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,           # 디버깅 시 True (모듈 09)
        max_iterations=10,      # 복잡한 검색이므로 여유 있게
        handle_parsing_errors=True,
    )

# n8n의 기업_분석_에이전트와 동일한 시스템 프롬프트
COMPANY_ANALYSIS_PROMPT = """당신은 전 세계 및 한국 기업을 조사하는 전문 리서치 에이전트입니다.
연결된 도구를 사용하여 최신 정보를 수집하고 구조화된 리포트를 작성하세요.

## 핵심 임무
1. 기본 정보: 설립일, 설립자, CEO, 본사 위치
2. 투자/재무: 총 투자액, 최근 투자 단계, 연 매출, 영업이익
3. 팀/기술: 직원 수, 핵심 인력 구성, 주요 기술 스택
4. 시장 지표: 주요 고객사, MAU/DAU
5. 최신 동향: 최근 6개월 내 주요 뉴스 3건

## 조사 가이드라인
- 한국 기업: THE VC, 혁신의숲, DART, 네이버 뉴스 우선
- 글로벌 기업: Crunchbase, LinkedIn, TechCrunch 우선
- 찾을 수 없는 데이터는 빈 문자열(""), 빈 배열([])로 표시"""

PRODUCT_OFFERING_PROMPT = """당신은 기업의 제품 및 서비스 오퍼링 전문 분석가입니다.
제품 기능, 가격 구조, 기술 스택을 상세히 조사하여 보고하세요.

## 조사 항목
- 주요 기능 세트, 요금제 플랜, 가격 결정 요인
- 무료 체험/프리미엄 버전, 엔터프라이즈 플랜
- 보조 도구 에코시스템, 기술 스택
- 한국 기업: 원화(KRW) 기준 가격 우선 수집"""

PRODUCT_REVIEW_PROMPT = """당신은 기업 및 제품 평판 분석 전문가입니다.
온라인 고객 리뷰를 수집하여 긍정/부정 비율 및 핵심 피드백을 분석하세요.

## 조사 항목
- 전체 리뷰 수 및 평균 평점, 긍정/부정 비율
- 주요 장점(Top Pros), 주요 단점(Top Cons)
- 주요 사용자층, 활발한 커뮤니티 플랫폼
- 글로벌: Trustpilot, G2, Product Hunt
- 한국: 잡플래닛, 블라인드, 클리앙"""

# 에이전트 3개 생성
company_agent = create_research_agent(
    COMPANY_ANALYSIS_PROMPT,
    [perplexity_search, tavily_search],
    company_parser,
)

product_agent = create_research_agent(
    PRODUCT_OFFERING_PROMPT,
    [perplexity_search, tavily_search],
    product_parser,
)

review_agent = create_research_agent(
    PRODUCT_REVIEW_PROMPT,
    [perplexity_search, tavily_search],
    review_parser,
)
```

### 3.6 3단계: 경쟁사별 순차 분석 루프

n8n의 **Loop Over Items** 노드는 경쟁사 목록을 하나씩 순회하면서
3개 에이전트를 순차 실행합니다. 중간에 **Wait(2초)** 가 있어 API 속도 제한을 방지합니다.

```python
def analyze_single_company(company_url: str) -> dict:
    """n8n의 Loop 내부 흐름: 에이전트 3개 순차 실행"""

    # 1. 기업 분석 (n8n: 기업_분석_에이전트)
    corp_result = company_agent.invoke({"input": company_url})

    # 2. 제품 오퍼링 분석 (n8n: 기업_제품_오퍼링_에이전트)
    product_result = product_agent.invoke({"input": company_url})

    # 3. 제품 평가 분석 (n8n: 제품_평가_에이전트)
    review_result = review_agent.invoke({"input": company_url})

    # n8n의 Wait(2초) 노드: API 속도 제한 방지
    time.sleep(2)

    return {
        "url": company_url,
        "company_analysis": corp_result["output"],
        "product_offering": product_result["output"],
        "product_review": review_result["output"],
    }


def run_competitor_analysis(company_url: str) -> list:
    """n8n 워크플로우 전체 흐름: 입력 → 경쟁사 탐색 → 순차 분석"""

    # 1단계: Exa.ai로 경쟁사 탐색
    raw_results = find_similar_companies(company_url)

    # 2단계: 데이터 정제 (상위 3개)
    competitors = refine_competitors(raw_results, max_count=3)

    # 3단계: 경쟁사별 순차 분석 (n8n의 Loop Over Items)
    all_analyses = []
    for competitor in competitors:
        print(f"\n분석 중: {competitor['title']} ({competitor['url']})")
        result = analyze_single_company(competitor["url"])
        all_analyses.append(result)

    return all_analyses
```

### 3.7 4단계: 최종 보고서 생성 + PDF 변환

n8n의 **최종_보고서(Agent)** → **렌더링(Information Extractor)** → **Convert HTML to PDF**
체인을 구현합니다.

```python
from langchain_core.prompts import ChatPromptTemplate

# n8n의 최종_보고서 에이전트: 모든 분석 결과를 종합
def generate_final_report(company_name: str, analyses: list) -> str:
    """n8n의 최종_보고서 노드 역할"""
    from datetime import datetime

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


# n8n의 렌더링 노드: HTML + CSS 추출
def render_to_html(report_text: str) -> dict:
    """n8n의 렌더링(Information Extractor) 노드 역할"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", """비즈니스 리포트를 HTML과 CSS로 변환하세요.
HTML_Content: 시각화 요소(표, 차트) 포함, 시맨틱 태그 사용
CSS_Content: Nanum Gothic 폰트, A4 인쇄 최적화 스타일"""),
        ("human", "{text}"),
    ])

    chain = prompt | llm
    result = chain.invoke({"text": report_text})
    # 실제로는 PydanticOutputParser로 HTML/CSS를 분리 추출
    return {"html": result.content, "css": ""}


# n8n의 Convert HTML to PDF 노드
def convert_to_pdf(html_content: str, css_content: str, output_path: str):
    """HTML → PDF 변환 (weasyprint 사용)"""
    from weasyprint import HTML
    full_html = f"<style>{css_content}</style>{html_content}"
    HTML(string=full_html).write_pdf(output_path)
    return output_path
```

### 3.8 전체 파이프라인 실행

```python
def main(company_url: str):
    """n8n 워크플로우 전체를 하나의 함수로 실행"""
    print(f"분석 대상: {company_url}")

    # 1. 경쟁사 분석 (n8n: 전체 루프)
    analyses = run_competitor_analysis(company_url)

    # 2. 최종 보고서 (n8n: Aggregate → 최종_보고서)
    report = generate_final_report("대모산개발단 경쟁업체", analyses)

    # 3. PDF 변환 (n8n: 렌더링 → Convert HTML to PDF)
    html_data = render_to_html(report)
    pdf_path = convert_to_pdf(html_data["html"], html_data["css"], "report.pdf")

    print(f"보고서 생성 완료: {pdf_path}")
    return pdf_path


# 실행 예시
main("https://www.demodev.io/")
```

---

## 4. LangGraph로 구현하기 (고급)

위의 LangChain 방식을 **LangGraph 그래프**로 전환하면
n8n의 워크플로우 구조를 더 직관적으로 표현할 수 있습니다.

### 4.1 상태 정의 (모듈 02: TypedDict)

```python
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END

class ResearchState(TypedDict):
    company_url: str                                    # 입력 URL
    competitors: list                                   # 경쟁사 목록
    current_index: int                                  # 현재 분석 중인 인덱스
    analyses: Annotated[list, operator.add]             # 분석 결과 누적 (모듈 02 리듀서)
    final_report: str                                   # 최종 보고서
    pdf_path: str                                       # PDF 경로
```

### 4.2 노드 함수 정의

```python
def find_competitors_node(state: ResearchState) -> dict:
    """n8n: Exa.ai_경쟁사_탐색 → 경쟁사_나누기 → 중복_제거 → Limit"""
    raw = find_similar_companies(state["company_url"])
    competitors = refine_competitors(raw, max_count=3)
    return {"competitors": competitors, "current_index": 0}

def analyze_company_node(state: ResearchState) -> dict:
    """n8n: Loop 내부의 3개 에이전트 순차 실행"""
    idx = state["current_index"]
    company = state["competitors"][idx]
    result = analyze_single_company(company["url"])
    return {
        "analyses": [result],        # 리듀서로 자동 누적
        "current_index": idx + 1,
    }

def generate_report_node(state: ResearchState) -> dict:
    """n8n: Aggregate → 최종_보고서 → 렌더링 → PDF"""
    report = generate_final_report("경쟁사 분석", state["analyses"])
    html_data = render_to_html(report)
    pdf_path = convert_to_pdf(html_data["html"], html_data["css"], "report.pdf")
    return {"final_report": report, "pdf_path": pdf_path}
```

### 4.3 라우터 함수 (모듈 03: 조건부 흐름)

n8n의 **Loop Over Items** 노드는 "아직 처리할 항목이 남았으면 계속, 없으면 종료"하는
조건부 루프입니다. 모듈 03에서 배운 **조건부 종료 패턴**과 정확히 동일합니다.

```python
def loop_router(state: ResearchState) -> str:
    """n8n의 Loop Over Items 완료 조건과 동일"""
    if state["current_index"] < len(state["competitors"]):
        return "continue"   # 다음 경쟁사 분석
    return "done"            # 모든 경쟁사 분석 완료 → 보고서 생성
```

### 4.4 그래프 조립 (모듈 01: StateGraph 4단계)

```python
graph = StateGraph(ResearchState)

# 노드 추가
graph.add_node("find_competitors", find_competitors_node)
graph.add_node("analyze_company", analyze_company_node)
graph.add_node("generate_report", generate_report_node)

# 엣지 설정
graph.set_entry_point("find_competitors")
graph.add_edge("find_competitors", "analyze_company")

# 조건부 엣지: 루프 (모듈 03 패턴)
graph.add_conditional_edges(
    "analyze_company",
    loop_router,
    {"continue": "analyze_company", "done": "generate_report"},
)
graph.add_edge("generate_report", END)

app = graph.compile()
```

**그래프 구조 (n8n 워크플로우와 동일한 루프)**:

```
[START]
  ↓
[find_competitors]  ← Exa.ai로 경쟁사 탐색 + 정제
  ↓
[analyze_company]  ← 3개 에이전트 순차 실행
  ↓
  ├── continue → [analyze_company]  (다음 경쟁사)
  └── done → [generate_report]      (모든 경쟁사 완료)
                 ↓
               [END]
```

### 4.5 실행

```python
result = app.invoke({
    "company_url": "https://www.demodev.io/",
    "competitors": [],
    "current_index": 0,
    "analyses": [],
    "final_report": "",
    "pdf_path": "",
})

print(f"PDF 보고서: {result['pdf_path']}")
print(f"분석된 경쟁사 수: {len(result['analyses'])}")
```

---

## 5. 배운 모듈별 적용 요약

| 모듈 | 강의에서 배운 것 | n8n에서의 역할 | 코드에서의 역할 |
|------|-----------------|---------------|----------------|
| **Python 챕터 04** | 리스트, 딕셔너리 | SplitOut, 도메인 추출, 중복 제거 | 리스트 컴프리헨션, `dict` 중복 제거 |
| **Python 챕터 05** | for 루프, 조건문 | Loop Over Items, Limit | `for company in companies:`, `[:3]` |
| **Python 챕터 06** | 함수 정의 | 각 노드의 처리 로직 | `def analyze_single_company()` |
| **Python 챕터 08** | 파일/네트워크 입출력 | Exa.ai HTTP Request | `requests.post()` |
| **Python 챕터 10** | 모듈, time | Wait(2초) 딜레이 | `time.sleep(2)` |
| **Python 챕터 11** | 클래스, OOP | Pydantic 스키마 | `class CompanyAnalysis(BaseModel)` |
| **LangChain 모듈 01** | LLM 호출 | Gemini 모델 호출 | `ChatGoogleGenerativeAI` |
| **LangChain 모듈 02** | 프롬프트 템플릿 | 에이전트 시스템 프롬프트 | `ChatPromptTemplate.from_messages()` |
| **LangChain 모듈 03** | LCEL 파이프라인 | 최종 보고서 체인 | `prompt \| llm` |
| **LangChain 모듈 04** | 출력 파서 | Structured Output Parser (JSON) | `PydanticOutputParser` |
| **LangChain 모듈 09** | 에이전트 + 도구 | 3개 전문 에이전트 + Perplexity/Tavily | `@tool` + `create_tool_calling_agent` |
| **LangGraph 모듈 01** | StateGraph 4단계 | 워크플로우 전체 구조 | `StateGraph` → `add_node` → `compile` |
| **LangGraph 모듈 02** | 상태 관리 + 리듀서 | 분석 결과 누적 | `Annotated[list, operator.add]` |
| **LangGraph 모듈 03** | 조건부 흐름 + 루프 | Loop Over Items (반복/종료 분기) | `add_conditional_edges` + 라우터 |

---

## 6. 핵심 아키텍처 비교: n8n vs 코드

| 항목 | n8n (노코드) | Python 코드 |
|------|-------------|-------------|
| 경쟁사 탐색 | Exa.ai 노드 드래그 | `requests.post()` |
| 3개 에이전트 | Agent 노드 3개 + 도구 연결 | `create_tool_calling_agent()` × 3 |
| 루프 처리 | Loop Over Items 노드 | `for` 루프 또는 LangGraph 조건부 엣지 |
| JSON 출력 강제 | Structured Output Parser 노드 | `PydanticOutputParser` + `BaseModel` |
| PDF 변환 | HTML to PDF 커뮤니티 노드 | `weasyprint` 라이브러리 |
| 디버깅 | 노드별 실행 결과 시각화 | `verbose=True` + 로그 |
| 확장성 | 에이전트 추가 = 노드 드래그 | 함수 추가 + 그래프 노드 등록 |

> **핵심**: 이 워크플로우는 **멀티 에이전트 시스템**입니다.
> n8n으로 빠르게 프로토타입을 만들고 검증한 뒤,
> 프로덕션 배포나 커스터마이징이 필요할 때 Python 코드로 전환하는 전략이 효과적입니다.

---

## 7. 크로스플랫폼 설정 (macOS / Windows)

### weasyprint 시스템 의존성

weasyprint는 PDF 렌더링을 위해 Pango/GTK 시스템 라이브러리가 필요합니다.

| 운영체제 | 설치 명령 |
|----------|----------|
| **macOS (Homebrew)** | `brew install pango` |
| **Windows (MSYS2)** | `pacman -S mingw-w64-x86_64-pango` |
| **Windows (수동)** | GTK3 런타임 설치 후 PATH에 `bin/` 추가 |
| **Ubuntu/Debian** | `apt install libpango-1.0-0 libpangocairo-1.0-0` |

### macOS 추가 설정

macOS에서는 weasyprint가 Homebrew 라이브러리 경로를 자동으로 찾지 못할 수 있습니다.
`src/config.py`에서 다음과 같이 해결합니다:

```python
import os
# weasyprint가 Homebrew 라이브러리를 찾을 수 있도록 경로 설정 (macOS)
if os.path.isdir("/opt/homebrew/lib"):
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib"
```

### 구현 시 주의사항

1. **weasyprint는 lazy import 사용**: 모듈 로딩 시점에 시스템 라이브러리를 로드하므로,
   `convert_to_pdf()` 함수 내부에서 `from weasyprint import HTML`로 지연 임포트
2. **PydanticOutputParser 이스케이프**: `get_format_instructions()`가 반환하는 JSON 스키마의
   `{}`가 `ChatPromptTemplate`의 변수 문법과 충돌하므로 `{{`/`}}`로 이스케이프 필수
3. **PDF 보고서 품질 안정화**: LLM에게 HTML+CSS를 동시에 생성시키면 매번 품질이 달라지고
   한글 폰트가 깨질 수 있음. 해결 방법:
   - CSS는 `REPORT_CSS` 고정 템플릿으로 분리 (Noto Sans KR 웹폰트, A4 인쇄 최적화)
   - LLM은 HTML `<body>` 내부 콘텐츠만 생성하도록 프롬프트 제한
   - `convert_to_pdf()`에서 `<!DOCTYPE html>`, `<meta charset="UTF-8">`, `lang="ko"` 포함한 완전한 HTML 문서로 조립
   - LLM이 코드블록으로 감쌀 경우 자동 제거 로직 포함
