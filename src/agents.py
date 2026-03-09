from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import llm
from src.tools import tavily_search, perplexity_search
from src.schemas import company_parser, product_parser, review_parser


def create_research_agent(system_prompt: str, tools: list, parser) -> AgentExecutor:
    """팩토리 함수: 시스템 프롬프트 + 도구 + 파서로 리서치 에이전트 생성"""
    # format_instructions의 중괄호를 이스케이프하여 프롬프트 변수 충돌 방지
    format_instructions = parser.get_format_instructions()
    format_instructions = format_instructions.replace("{", "{{").replace("}", "}}")
    full_prompt = system_prompt + "\n\n" + format_instructions

    prompt = ChatPromptTemplate.from_messages([
        ("system", full_prompt),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )


# --- 시스템 프롬프트 ---

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


# --- 에이전트 인스턴스 ---

tools = [perplexity_search, tavily_search]

company_agent = create_research_agent(COMPANY_ANALYSIS_PROMPT, tools, company_parser)
product_agent = create_research_agent(PRODUCT_OFFERING_PROMPT, tools, product_parser)
review_agent = create_research_agent(PRODUCT_REVIEW_PROMPT, tools, review_parser)
