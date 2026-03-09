# TODO: 경쟁사 리서치 에이전트 개발 체크리스트

> 각 Phase마다 **바이브코딩 프롬프트**가 포함되어 있습니다.
> 프롬프트를 AI에게 그대로 입력하면 해당 단계의 코드가 생성됩니다.
> 참고 문서: `PRD.md` | `n8n_to_code.md`

---

## Phase 1: 프로젝트 초기화

- [x] uv 프로젝트 생성
- [x] 의존성 패키지 설치
- [x] `.env` 파일 생성
- [x] `src/config.py` 작성

### 바이브코딩 프롬프트

```
Final_Project/ 폴더에서 uv로 Python 프로젝트를 초기화해줘.

1. `uv init`으로 프로젝트를 생성하고
2. 아래 패키지들을 설치해줘:
   - langchain-google-genai
   - langchain-community
   - langgraph
   - langchain-text-splitters
   - python-dotenv
   - pydantic
   - tavily-python
   - requests
   - weasyprint
3. `.env` 파일을 만들어줘. 아래 키들이 필요해:
   - GOOGLE_API_KEY
   - EXA_API_KEY
   - TAVILY_API_KEY
   - PERPLEXITY_API_KEY
4. `src/config.py`를 만들어줘:
   - python-dotenv로 `.env` 로딩
   - 4개 API 키를 환경 변수에서 가져오기
   - ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)로 LLM 초기화
   - LLM 인스턴스를 다른 모듈에서 import할 수 있게 export

프로젝트 구조는 PRD.md의 "6. 프로젝트 구조" 섹션을 따라줘.
```

---

## Phase 2: 도구 & 스키마

- [x] `src/schemas.py` — Pydantic 출력 스키마 3종
- [x] `src/tools.py` — Perplexity, Tavily 검색 도구

### 바이브코딩 프롬프트 — schemas.py

```
`src/schemas.py`를 만들어줘.
n8n 워크플로우의 Structured Output Parser에 대응하는 Pydantic 스키마 3개를 정의해야 해.

1. CompanyAnalysis — 기업 분석 에이전트 출력
   - analysis_target: 기업명(name), 도메인(domain), 지역(region: KR/Global)
   - corporate_identity: 설립연도(year_founded), 본사(hq_location), CEO(current_ceo: dict)
   - financial_performance: 총투자액(total_funding_amount), 매출(annual_revenue_latest), 기업가치(valuation)
   - operational_metrics: dict (직원 수, MAU 등)
   - market_intelligence: dict (최신 뉴스, 고객사)

2. ProductOffering — 제품 오퍼링 에이전트 출력
   - features: list, pricing_plans: list, technology_stack: list, sources: list

3. ProductReview — 제품 평가 에이전트 출력
   - review_summary: dict, top_pros: list, top_cons: list, notable_feedbacks: list, sources: list

모든 필드에 Field(default=..., description="...")을 넣어줘.
각 스키마에 대한 PydanticOutputParser도 함께 생성해서 export해줘.

참고: n8n_to_code.md의 "출력 스키마 정의" 섹션에 자세한 스키마가 있어.
```

### 바이브코딩 프롬프트 — tools.py

```
`src/tools.py`를 만들어줘.
n8n 워크플로우에서 각 에이전트가 사용하는 2개의 검색 도구를 LangChain @tool로 구현해야 해.

1. tavily_search(query: str) -> str
   - TavilySearchResults(max_results=5)를 사용
   - 결과를 json.dumps(ensure_ascii=False)로 반환
   - docstring: "웹에서 최신 정보를 검색합니다. 기업 정보, 재무 데이터, 뉴스 등을 찾을 때 사용하세요."

2. perplexity_search(query: str) -> str
   - requests.post로 Perplexity API 호출 (https://api.perplexity.ai/chat/completions)
   - model: "sonar"
   - system message: "기업 정보를 정확하게 조사하여 JSON으로 반환하세요."
   - docstring: "Perplexity AI로 기업 정보를 실시간 검색합니다."

API 키는 src/config.py에서 import해서 사용해줘.
참고: n8n_to_code.md의 "도구 정의" 섹션
```

---

## Phase 3: 에이전트

- [x] `src/agents.py` — 에이전트 팩토리 함수
- [x] 3개 전문 에이전트 인스턴스 생성

### 바이브코딩 프롬프트

```
`src/agents.py`를 만들어줘.
n8n 워크플로우의 3개 전문 리서치 에이전트를 LangChain으로 구현해야 해.

1. create_research_agent(system_prompt, tools, parser) -> AgentExecutor 팩토리 함수:
   - 시스템 프롬프트에 parser.get_format_instructions()를 추가
   - ChatPromptTemplate.from_messages([system, human, agent_scratchpad])
   - create_tool_calling_agent(llm, tools, prompt)
   - AgentExecutor(agent, tools, verbose=True, max_iterations=10, handle_parsing_errors=True)

2. 3개 에이전트 인스턴스 생성:
   - company_agent: 기업 기본정보/재무/뉴스 조사 (한국: THE VC, DART / 글로벌: Crunchbase, TechCrunch)
   - product_agent: 제품 기능/가격/기술스택 조사 (한국 원화 가격 우선)
   - review_agent: 리뷰/장단점/평판 분석 (글로벌: G2, Trustpilot / 한국: 잡플래닛, 블라인드)

각 에이전트의 시스템 프롬프트는 n8n_to_code.md의 COMPANY_ANALYSIS_PROMPT,
PRODUCT_OFFERING_PROMPT, PRODUCT_REVIEW_PROMPT를 그대로 사용해줘.

도구는 src/tools.py에서, 스키마 파서는 src/schemas.py에서, LLM은 src/config.py에서 import해줘.
```

---

## Phase 4: 파이프라인

- [x] `src/pipeline.py` — Exa.ai 경쟁사 탐색 함수
- [x] 데이터 정제 함수 (추출, 중복제거, 제한)
- [x] 단일 기업 분석 함수 (3개 에이전트 순차 실행)
- [x] 전체 분석 루프 함수

### 바이브코딩 프롬프트

```
`src/pipeline.py`를 만들어줘.
n8n 워크플로우의 전체 분석 파이프라인을 구현해야 해.

1. find_similar_companies(company_url: str) -> list
   - Exa.ai API POST 호출 (https://api.exa.ai/findSimilar)
   - 헤더: x-api-key, Content-Type: application/json
   - 바디: url, type="neural", useAutoprompt=True, contents={"text": False}
   - excludeDomains: [company_url, "github.com", "linkedin.com"]

2. refine_competitors(results: list, max_count: int = 3) -> list
   - title, url만 추출 (리스트 컴프리헨션)
   - URL 기준 중복 제거
   - 상위 max_count개만 반환 (슬라이싱)

3. analyze_single_company(company_url: str) -> dict
   - company_agent, product_agent, review_agent 순차 실행
   - 각 결과를 dict로 묶어서 반환
   - time.sleep(2)로 API 속도 제한 방지

4. run_competitor_analysis(company_url: str) -> list
   - find_similar_companies → refine_competitors → for 루프로 analyze_single_company
   - 진행 상태 print 출력

에이전트는 src/agents.py에서, API 키는 src/config.py에서 import.
참고: n8n_to_code.md의 "3.3~3.6" 섹션
```

---

## Phase 5: 보고서

- [x] `src/report.py` — 최종 보고서 생성 함수
- [x] HTML 렌더링 함수
- [x] PDF 변환 함수

### 바이브코딩 프롬프트

```
`src/report.py`를 만들어줘.
n8n 워크플로우의 보고서 생성 파이프라인(Aggregate → 최종_보고서 → 렌더링 → PDF)을 구현해야 해.

1. generate_final_report(company_name: str, analyses: list) -> str
   - ChatPromptTemplate으로 시스템 프롬프트 설정
   - "경쟁사 분석 전문가" 역할, 수집된 데이터 종합 보고서 작성
   - prompt | llm 체인으로 실행
   - 기업명, 분석 날짜(datetime.now), 분석 데이터(JSON)를 입력

2. render_to_html(report_text: str) -> dict
   - LLM에게 비즈니스 보고서를 HTML + CSS로 변환 요청
   - HTML: 시각화 요소(표, 차트), 시맨틱 태그
   - CSS: Nanum Gothic 폰트, A4 인쇄 최적화
   - {"html": ..., "css": ...} 딕셔너리 반환

3. convert_to_pdf(html_content: str, css_content: str, output_path: str) -> str
   - weasyprint의 HTML 클래스 사용
   - <style>CSS</style> + HTML 합치고 write_pdf()
   - 저장된 파일 경로 반환

LLM은 src/config.py에서 import.
참고: n8n_to_code.md의 "3.7 4단계" 섹션
```

---

## Phase 6: LangGraph 통합

- [x] `src/graph.py` — ResearchState 정의
- [x] 노드 함수 3개 (find_competitors, analyze_company, generate_report)
- [x] 루프 라우터 함수
- [x] StateGraph 조립 + 컴파일
- [x] `main.py` — CLI 엔트리포인트

### 바이브코딩 프롬프트 — graph.py

```
`src/graph.py`를 만들어줘.
지금까지 만든 파이프라인을 LangGraph StateGraph로 통합해야 해.

1. ResearchState(TypedDict) 상태 정의:
   - company_url: str
   - competitors: list
   - current_index: int
   - analyses: Annotated[list, operator.add]  ← 리듀서로 결과 누적
   - final_report: str
   - pdf_path: str

2. 노드 함수 3개:
   - find_competitors_node: Exa.ai 탐색 + 정제 → competitors, current_index=0
   - analyze_company_node: current_index번째 경쟁사를 3개 에이전트로 분석 → analyses에 추가, current_index+1
   - generate_report_node: 최종 보고서 생성 + HTML 렌더링 + PDF 변환

3. loop_router(state) -> str:
   - current_index < len(competitors) → "continue"
   - 그 외 → "done"

4. 그래프 조립:
   - set_entry_point("find_competitors")
   - find_competitors → analyze_company
   - analyze_company → add_conditional_edges(loop_router, {"continue": "analyze_company", "done": "generate_report"})
   - generate_report → END
   - graph.compile()하여 app으로 export

기존 함수들은 src/pipeline.py, src/report.py에서 import.
참고: n8n_to_code.md의 "4. LangGraph로 구현하기" 섹션
```

### 바이브코딩 프롬프트 — main.py

```
`main.py`를 만들어줘. 프로젝트의 엔트리포인트야.

1. 사용자에게 기업 URL을 입력받아 (input() 또는 argparse)
2. src/graph.py의 app.invoke()로 LangGraph 파이프라인 실행
3. 초기 상태: company_url=입력값, competitors=[], current_index=0, analyses=[], final_report="", pdf_path=""
4. 실행 결과에서 pdf_path와 분석된 경쟁사 수를 출력
5. 에러 발생 시 적절한 메시지 출력

실행 방법: `uv run python main.py`
```

---

## Phase 7: 테스트 & 검증

- [x] 단일 기업 URL로 E2E 테스트 실행
- [x] PDF 파일 정상 생성 확인
- [x] 에러 핸들링 점검 (잘못된 URL, API 실패 등)
- [x] 최종 코드 정리

### 바이브코딩 프롬프트

```
전체 프로젝트를 테스트해줘.

1. `uv run python main.py`를 실행해서 "https://www.demodev.io/" URL로 테스트해줘.
2. 만약 에러가 발생하면 원인을 분석하고 수정해줘.
3. 다음 항목들을 점검해줘:
   - .env 파일의 API 키가 올바르게 로딩되는지
   - Exa.ai API 호출이 정상 작동하는지
   - 3개 에이전트가 순차적으로 실행되는지
   - PDF 파일이 정상 생성되는지
   - 한글이 깨지지 않는지
4. 에러 핸들링을 추가해줘:
   - API 호출 실패 시 빈 값 반환하고 파이프라인 계속 진행
   - LLM 응답 파싱 실패 시 handle_parsing_errors로 처리
```

---

## 진행 상황 요약

| Phase | 상태 | 생성 파일 |
|-------|------|----------|
| 1. 프로젝트 초기화 | ✅ 완료 | pyproject.toml, .env, src/config.py |
| 2. 도구 & 스키마 | ✅ 완료 | src/schemas.py, src/tools.py |
| 3. 에이전트 | ✅ 완료 | src/agents.py |
| 4. 파이프라인 | ✅ 완료 | src/pipeline.py |
| 5. 보고서 | ✅ 완료 | src/report.py |
| 6. LangGraph 통합 | ✅ 완료 | src/graph.py, main.py |
| 7. 테스트 & 검증 | ✅ 완료 | report.pdf 생성 확인 |

---

## 구현 중 해결한 이슈

| 이슈 | 원인 | 해결 |
|------|------|------|
| 프롬프트 변수 충돌 | `PydanticOutputParser.get_format_instructions()`의 JSON 중괄호가 프롬프트 변수로 해석됨 | `format_instructions.replace("{", "{{").replace("}", "}}")` 이스케이프 |
| weasyprint macOS 로딩 실패 | Homebrew 라이브러리 경로를 weasyprint가 자동으로 찾지 못함 | `src/config.py`에서 `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` 설정 |
| weasyprint import 시 크래시 | 모듈 로딩 시점에 시스템 라이브러리 로드 시도 | `convert_to_pdf()` 내부에서 lazy import로 변경 |
| PDF 한글 깨짐 + 레이아웃 불안정 | LLM이 생성한 HTML/CSS 품질이 매번 달라지고, 웹폰트 미적용 | CSS를 고정 템플릿(`REPORT_CSS`)으로 분리, LLM은 HTML 본문만 생성하도록 변경 |

## 크로스플랫폼 설정 (macOS / Windows)

### macOS
```bash
brew install pango
```

### Windows
```
1. https://github.com/nicothin/weasyprint-windows-guide 참고
2. GTK3 런타임 설치: https://github.com/nicothin/weasyprint-windows-guide#install-gtk3
3. 또는 MSYS2: pacman -S mingw-w64-x86_64-pango
```
