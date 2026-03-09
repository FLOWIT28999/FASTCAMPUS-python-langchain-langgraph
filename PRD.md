# PRD: 경쟁사 리서치 에이전트

## 1. 개요

### 프로젝트명
**실시간 글로벌 시장 분석 및 경쟁사 리서치 에이전트**

### 한 줄 요약
기업 URL을 입력하면 Exa.ai로 경쟁사를 자동 탐색하고, 3개의 전문 AI 에이전트가 각 경쟁사를 심층 분석하여 PDF 보고서를 생성하는 멀티 에이전트 시스템

### 배경
- n8n(노코드)으로 이미 검증된 워크플로우를 Python 코드로 전환
- 강의에서 배운 Python, LangChain, LangGraph 기술을 실전 적용
- 참고 문서: `Final_Project/n8n_to_code.md`

---

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.11+ |
| 패키지 관리 | uv |
| LLM | Google Gemini (gemini-2.5-flash) |
| 프레임워크 | LangChain + LangGraph |
| 검색 도구 | Perplexity API, Tavily API |
| 경쟁사 탐색 | Exa.ai API |
| 출력 파싱 | Pydantic + PydanticOutputParser |
| PDF 변환 | weasyprint |
| 환경 변수 | python-dotenv (.env) |

---

## 3. 시스템 아키텍처

```
[입력: 기업 URL]
       ↓
[1단계] Exa.ai 경쟁사 탐색 (neural search)
       ↓
[2단계] 데이터 정제 (추출 → 중복 제거 → 상위 3개)
       ↓
[3단계] 경쟁사별 순차 분석 루프 ─────────────────────┐
       │                                               │
       │  ┌─ 기업_분석_에이전트 (기본 정보/재무/뉴스)   │
       │  ├─ 제품_오퍼링_에이전트 (기능/가격/기술)      │
       │  └─ 제품_평가_에이전트 (리뷰/장단점/평판)      │
       │                                               │
       │  → Wait(2초) → 다음 경쟁사 ──────────────────┘
       ↓
[4단계] 결과 집계 → 최종 보고서 생성 → HTML 렌더링 → PDF 변환
       ↓
[출력: report.pdf]
```

---

## 4. 기능 명세

### 4.1 입력 처리
| 항목 | 설명 |
|------|------|
| 입력 | 기업 URL (예: `https://www.demodev.io/`) |
| 처리 | Exa.ai `findSimilar` API로 유사 기업 검색 |
| 출력 | 경쟁사 리스트 (title, url) |

### 4.2 데이터 정제
| 항목 | 설명 |
|------|------|
| 입력 | Exa.ai 검색 결과 (raw results) |
| 처리 | title/url 추출 → URL 기준 중복 제거 → 상위 3개 선택 |
| 출력 | 정제된 경쟁사 리스트 (최대 3개) |

### 4.3 경쟁사 분석 (3개 에이전트)

#### 에이전트 1: 기업 분석
| 항목 | 설명 |
|------|------|
| 역할 | 기업 기본 정보 및 재무 데이터 수집 |
| 조사 항목 | 설립일, CEO, 투자/재무, 직원 수, 최신 뉴스 |
| 도구 | Perplexity API, Tavily Search |
| 출력 | `CompanyAnalysis` (Pydantic JSON) |

#### 에이전트 2: 제품 오퍼링 분석
| 항목 | 설명 |
|------|------|
| 역할 | 제품 기능 및 가격 구조 분석 |
| 조사 항목 | 주요 기능, 요금제, 기술 스택, 프로모션 |
| 도구 | Perplexity API, Tavily Search |
| 출력 | `ProductOffering` (Pydantic JSON) |

#### 에이전트 3: 제품 평가 분석
| 항목 | 설명 |
|------|------|
| 역할 | 온라인 리뷰 및 평판 분석 |
| 조사 항목 | 리뷰 요약, 장단점, 사용자층, 평판 |
| 도구 | Perplexity API, Tavily Search |
| 출력 | `ProductReview` (Pydantic JSON) |

### 4.4 보고서 생성
| 항목 | 설명 |
|------|------|
| 입력 | 모든 경쟁사의 3개 에이전트 분석 결과 |
| 처리 | LLM이 종합 보고서 작성 → HTML/CSS 렌더링 → PDF 변환 |
| 출력 | `report.pdf` 파일 |

---

## 5. 데이터 모델 (Pydantic 스키마)

### CompanyAnalysis
```
├── analysis_target
│   ├── name: str              # 기업명
│   ├── domain: str            # 공식 홈페이지
│   └── region: str            # KR / Global
├── corporate_identity
│   ├── year_founded: str      # 설립 연도
│   ├── hq_location: str       # 본사 소재지
│   └── current_ceo: dict      # CEO 정보
├── financial_performance
│   ├── total_funding_amount: str
│   ├── annual_revenue_latest: str
│   └── valuation: str
├── operational_metrics: dict   # 직원 수, MAU 등
└── market_intelligence: dict   # 최신 뉴스, 고객사
```

### ProductOffering
```
├── features: list             # 주요 기능
├── pricing_plans: list        # 요금제
├── technology_stack: list     # 기술 스택
└── sources: list              # 출처 URL
```

### ProductReview
```
├── review_summary: dict       # 평점, 리뷰 수
├── top_pros: list             # 주요 장점
├── top_cons: list             # 주요 단점
├── notable_feedbacks: list    # 주목할 피드백
└── sources: list              # 출처 URL
```

---

## 6. 프로젝트 구조

```
Final_Project/
├── .env                       # API 키 (git 제외)
├── pyproject.toml             # uv 프로젝트 설정
├── PRD.md                     # 이 문서
├── n8n_to_code.md             # n8n ↔ 코드 매핑 가이드
├── n8n.json                   # 원본 n8n 워크플로우
│
├── src/
│   ├── config.py              # 환경 변수 로딩, LLM 초기화
│   ├── tools.py               # @tool: Perplexity, Tavily
│   ├── schemas.py             # Pydantic 출력 스키마
│   ├── agents.py              # 3개 에이전트 생성
│   ├── pipeline.py            # Exa.ai 탐색 + 데이터 정제
│   ├── report.py              # 최종 보고서 + HTML + PDF
│   └── graph.py               # LangGraph 그래프 정의
│
└── main.py                    # 엔트리포인트
```

---

## 7. API 키 (.env)

```env
GOOGLE_API_KEY=               # Gemini LLM
EXA_API_KEY=                  # 경쟁사 탐색
TAVILY_API_KEY=               # 웹 검색 도구
PERPLEXITY_API_KEY=           # 실시간 검색 도구
```

---

## 8. 구현 단계 (바이브코딩 순서)

### Phase 1: 프로젝트 초기화
- [x] `uv init` 프로젝트 생성
- [x] 의존성 패키지 설치
- [x] `.env` 파일 생성 (API 키 템플릿)
- [x] `src/config.py` — 환경 변수 로딩 + LLM 초기화

### Phase 2: 도구 & 스키마
- [x] `src/schemas.py` — Pydantic 출력 스키마 3개
- [x] `src/tools.py` — Perplexity, Tavily 도구 (@tool)

### Phase 3: 에이전트
- [x] `src/agents.py` — 3개 전문 에이전트 생성 (create_tool_calling_agent)

### Phase 4: 파이프라인
- [x] `src/pipeline.py` — Exa.ai 경쟁사 탐색 + 데이터 정제 + 순차 분석 루프

### Phase 5: 보고서
- [x] `src/report.py` — 최종 보고서 생성 + HTML 렌더링 + PDF 변환

### Phase 6: LangGraph 통합
- [x] `src/graph.py` — StateGraph로 전체 파이프라인 그래프화
- [x] `main.py` — 엔트리포인트 (CLI 실행)

### Phase 7: 테스트 & 검증
- [x] 단일 기업 URL로 E2E 테스트
- [x] PDF 출력 확인
- [x] 에러 핸들링 점검

---

## 9. 비기능 요구사항

| 항목 | 요구사항 |
|------|---------|
| API 속도 제한 | 경쟁사 간 2초 딜레이 (`time.sleep(2)`) |
| 에러 처리 | API 실패 시 빈 값 반환, 파이프라인 중단 방지 |
| 로깅 | 각 에이전트 실행 상태 콘솔 출력 (`verbose=True`) |
| PDF 품질 | A4 크기, Nanum Gothic 폰트, 한글 지원 |
| 확장성 | 에이전트 추가 시 함수 1개 + 그래프 노드 1개만 추가 |

---

## 10. 제약 사항 및 고려 사항

- **Exa.ai 무료 티어**: 월 1,000건 제한 — 테스트 시 `max_count` 줄여서 사용
- **Perplexity API**: sonar 모델 사용, 응답 시간 3~5초 예상
- **weasyprint 시스템 의존성**:
  - macOS: `brew install pango` + `src/config.py`에서 `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` 자동 설정
  - Windows: GTK3 런타임 설치 필요 (https://github.com/nicothin/weasyprint-windows-guide) 또는 MSYS2에서 `pacman -S mingw-w64-x86_64-pango`
  - weasyprint는 lazy import 사용 (PDF 변환 시점에만 로드)
- **PydanticOutputParser 주의**: `get_format_instructions()`의 JSON 중괄호가 `ChatPromptTemplate` 변수로 해석되므로 `{{`/`}}`로 이스케이프 필요
- **PDF 보고서 품질**: LLM이 HTML+CSS를 동시에 생성하면 매번 결과가 달라지고 한글이 깨질 수 있음 → CSS는 `REPORT_CSS` 고정 템플릿 사용, LLM은 HTML 본문만 생성, `Noto Sans KR` 웹폰트로 한글 지원
- **LLM 토큰 비용**: 경쟁사 3개 × 에이전트 3개 = 최소 9회 LLM 호출 + 보고서 2회 = 약 11회
