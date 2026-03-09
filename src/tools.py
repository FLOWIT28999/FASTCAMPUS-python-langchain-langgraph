import json
import requests
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from src.config import PERPLEXITY_API_KEY


@tool
def tavily_search(query: str) -> str:
    """웹에서 최신 정보를 검색합니다. 기업 정보, 재무 데이터, 뉴스 등을 찾을 때 사용하세요."""
    search = TavilySearchResults(max_results=5)
    results = search.invoke(query)
    return json.dumps(results, ensure_ascii=False)


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
