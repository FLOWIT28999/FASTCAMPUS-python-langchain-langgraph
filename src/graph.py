import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.pipeline import find_similar_companies, refine_competitors, analyze_single_company
from src.report import generate_final_report, render_to_html, convert_to_pdf


class ResearchState(TypedDict):
    company_url: str
    competitors: list
    current_index: int
    analyses: Annotated[list, operator.add]
    final_report: str
    pdf_path: str


# --- 노드 함수 ---

def find_competitors_node(state: ResearchState) -> dict:
    """Exa.ai 경쟁사 탐색 + 정제"""
    raw = find_similar_companies(state["company_url"])
    competitors = refine_competitors(raw, max_count=3)
    print(f"발견된 경쟁사: {len(competitors)}개")
    return {"competitors": competitors, "current_index": 0}


def analyze_company_node(state: ResearchState) -> dict:
    """현재 인덱스의 경쟁사를 3개 에이전트로 분석"""
    idx = state["current_index"]
    company = state["competitors"][idx]
    print(f"\n[{idx + 1}/{len(state['competitors'])}] 분석 중: {company['title']} ({company['url']})")
    result = analyze_single_company(company["url"])
    return {
        "analyses": [result],
        "current_index": idx + 1,
    }


def generate_report_node(state: ResearchState) -> dict:
    """최종 보고서 생성 + HTML 렌더링 + PDF 변환"""
    report = generate_final_report("경쟁사 분석", state["analyses"])
    html_data = render_to_html(report)
    pdf_path = convert_to_pdf(html_data["html"], html_data["css"], "report.pdf")
    print(f"\n보고서 생성 완료: {pdf_path}")
    return {"final_report": report, "pdf_path": pdf_path}


# --- 라우터 ---

def loop_router(state: ResearchState) -> str:
    if state["current_index"] < len(state["competitors"]):
        return "continue"
    return "done"


# --- 그래프 조립 ---

graph = StateGraph(ResearchState)

graph.add_node("find_competitors", find_competitors_node)
graph.add_node("analyze_company", analyze_company_node)
graph.add_node("generate_report", generate_report_node)

graph.set_entry_point("find_competitors")
graph.add_edge("find_competitors", "analyze_company")
graph.add_conditional_edges(
    "analyze_company",
    loop_router,
    {"continue": "analyze_company", "done": "generate_report"},
)
graph.add_edge("generate_report", END)

app = graph.compile()
