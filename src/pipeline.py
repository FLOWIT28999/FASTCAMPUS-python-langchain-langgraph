import time
import requests
from src.config import EXA_API_KEY
from src.agents import company_agent, product_agent, review_agent


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


def refine_competitors(results: list, max_count: int = 3) -> list:
    """경쟁사 목록 정제: title/url 추출 → 중복 제거 → 상위 N개"""
    extracted = [{"title": r["title"], "url": r["url"]} for r in results]

    seen = {}
    unique = []
    for item in extracted:
        if item["url"] not in seen:
            seen[item["url"]] = True
            unique.append(item)

    return unique[:max_count]


def analyze_single_company(company_url: str) -> dict:
    """단일 경쟁사를 3개 에이전트로 순차 분석"""
    corp_result = company_agent.invoke({"input": company_url})
    product_result = product_agent.invoke({"input": company_url})
    review_result = review_agent.invoke({"input": company_url})

    time.sleep(2)

    return {
        "url": company_url,
        "company_analysis": corp_result["output"],
        "product_offering": product_result["output"],
        "product_review": review_result["output"],
    }


def run_competitor_analysis(company_url: str) -> list:
    """전체 파이프라인: 경쟁사 탐색 → 정제 → 순차 분석"""
    raw_results = find_similar_companies(company_url)
    competitors = refine_competitors(raw_results, max_count=3)

    print(f"발견된 경쟁사: {len(competitors)}개")

    all_analyses = []
    for i, competitor in enumerate(competitors, 1):
        print(f"\n[{i}/{len(competitors)}] 분석 중: {competitor['title']} ({competitor['url']})")
        result = analyze_single_company(competitor["url"])
        all_analyses.append(result)

    return all_analyses
