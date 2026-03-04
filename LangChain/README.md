## 목차

1. [모듈 00: 환경 설정](#모듈-00-환경-설정)
2. [모듈 01: Hello LangChain](#모듈-01-hello-langchain)
3. [모듈 02: 프롬프트 템플릿](#모듈-02-프롬프트-템플릿)
4. [모듈 03: LCEL - 파이프 연산자](#모듈-03-lcel---파이프-연산자)
5. [모듈 04: 출력 파서](#모듈-04-출력-파서)
6. [모듈 05: 메모리와 대화 관리](#모듈-05-메모리와-대화-관리)
7. [모듈 06: 문서 로딩과 텍스트 분할](#모듈-06-문서-로딩과-텍스트-분할)
8. [모듈 07: 임베딩과 벡터 저장소](#모듈-07-임베딩과-벡터-저장소)
9. [모듈 08: RAG](#모듈-08-rag)
10. [모듈 09: 에이전트와 도구](#모듈-09-에이전트와-도구)

---

## 모듈 00: 환경 설정

> **학습 목표:** UV 패키지 매니저로 의존성을 설치하고, Gemini API 키를 발급받아 `.env` 파일에 안전하게 저장한다.

- [ ] UV 패키지 매니저 이해 및 설치 확인
  - [ ] UV vs pip 비교 (속도, 프로젝트 관리 방식)
  - [ ] `!uv pip install` 로 Jupyter에서 패키지 설치하기
- [ ] 필수 패키지 설치 및 버전 확인
  - [ ] `langchain`, `langchain-core`, `langchain-community`
  - [ ] `langchain-google-genai`, `python-dotenv`
- [ ] Gemini API 키 발급 (Google AI Studio)
  - [ ] `getpass.getpass()` 로 화면 노출 없이 안전하게 입력
- [ ] `.env` 파일 생성 및 API 키 저장
  - [ ] 코드에 직접 키를 쓰면 안 되는 이유 이해
  - [ ] `.gitignore` 로 `.env` 파일 보호
  - [ ] `load_dotenv()` + `os.getenv()` 패턴 익히기
- [ ] 종합 환경 검증 (`python-version`, 패키지, API 키 모두 [OK] 확인)

---

## 모듈 01: Hello LangChain

> **학습 목표:** ChatGoogleGenerativeAI로 Gemini 모델에 연결하고, 두 가지 호출 방식과 메시지 타입을 이해한다.

- [ ] `ChatGoogleGenerativeAI` 초기화
  - [ ] `model` 파라미터: `gemini-2.0-flash` vs `gemini-1.5-pro`
  - [ ] `temperature` 파라미터: 0.0(일관성) ~ 2.0(창의성)
  - [ ] LLM vs ChatModel 차이 이해 (문자열 입력 vs 메시지 리스트 입력)
- [ ] 방법 1: 문자열로 `invoke()` 호출
  - [ ] `response.content` 로 텍스트 추출
  - [ ] `AIMessage` 객체 구조 탐색 (`id`, `response_metadata`, `usage_metadata`)
- [ ] 3가지 메시지 타입 이해
  - [ ] `HumanMessage`: 사용자 메시지
  - [ ] `AIMessage`: AI 응답 메시지
  - [ ] `SystemMessage`: AI에게 주는 역할 지시 (무대 감독)
- [ ] 방법 2: 메시지 리스트로 `invoke()` 호출
  - [ ] `SystemMessage` 로 AI 역할 설정하기
  - [ ] 같은 질문에 `SystemMessage` 만 바꿔 다른 응답 비교
- [ ] `invoke()` vs `stream()` 차이
  - [ ] `stream()` 으로 텍스트가 조각(chunk)별로 실시간 출력되는 것 확인
  - [ ] `end=""`, `flush=True` 옵션으로 스트리밍 출력 구현

---

## 모듈 02: 프롬프트 템플릿

> **학습 목표:** 재사용 가능한 프롬프트 템플릿을 만들고, partial()로 변수를 미리 고정하며, Few-shot으로 AI에게 패턴을 보여준다.

- [ ] `ChatPromptTemplate` 기초
  - [ ] `from_messages()` 로 템플릿 생성
  - [ ] `{변수명}` 문법으로 변수 자리 만들기
  - [ ] `invoke({'변수명': '값'})` 로 변수 채우기
  - [ ] `input_variables` 로 사용 중인 변수 목록 확인
- [ ] 같은 템플릿 다른 변수로 재사용
  - [ ] Python / JavaScript / Java 예시로 반복 재사용 체험
- [ ] `partial()` 로 변수 일부 미리 고정
  - [ ] 자주 고정되는 변수를 미리 채워 남은 변수만 입력받기
  - [ ] 실전: `target_language` 를 고정한 번역기 만들기
- [ ] `FewShotChatMessagePromptTemplate`
  - [ ] `examples` 리스트 정의 (딕셔너리 형태)
  - [ ] `example_prompt` 로 예시 하나를 메시지로 변환
  - [ ] `FewShotChatMessagePromptTemplate` 으로 예시 전체를 프롬프트에 삽입
  - [ ] 실전: 감정 분류기 (긍정 / 부정 / 중립) 만들기

---

## 모듈 03: LCEL - 파이프 연산자

> **학습 목표:** `|` 파이프 연산자로 컴포넌트를 체이닝하고, LCEL의 공통 인터페이스와 병렬 실행을 이해한다.

- [ ] LCEL (LangChain Expression Language) 개념
  - [ ] 기존 방식(`filled = prompt.invoke(...); llm.invoke(filled)`) vs LCEL(`chain = prompt | llm`)
  - [ ] `|` 파이프 연산자의 의미 (Unix 파이프와 동일한 개념)
- [ ] 기본 체인 구성
  - [ ] `prompt | llm` 2단계 체인
  - [ ] `prompt | llm | output_parser` 3단계 체인
- [ ] `Runnable` 공통 인터페이스
  - [ ] `invoke()`: 단일 입력 처리
  - [ ] `batch()`: 여러 입력 한 번에 처리
  - [ ] `stream()`: 실시간 스트리밍 출력
- [ ] `RunnableLambda` 로 일반 함수를 체인에 연결
- [ ] `RunnableParallel` 로 여러 체인 동시 실행
  - [ ] 같은 입력을 여러 체인에 병렬로 전달하고 결과 합치기

---

## 모듈 04: 출력 파서

> **학습 목표:** AI의 텍스트 응답을 원하는 형태로 변환하고, Pydantic으로 구조화된 데이터를 추출한다.

- [ ] `StrOutputParser`
  - [ ] `AIMessage` 에서 텍스트(`content`)만 자동 추출
  - [ ] `prompt | llm | StrOutputParser()` 체인 패턴
- [ ] `CommaSeparatedListOutputParser`
  - [ ] 쉼표로 구분된 문자열을 Python 리스트로 변환
- [ ] `PydanticOutputParser`
  - [ ] `BaseModel` 로 원하는 출력 스키마 정의
  - [ ] `get_format_instructions()` 로 AI에게 형식 지시사항 전달
  - [ ] AI 응답을 Pydantic 객체로 자동 파싱
- [ ] `JsonOutputParser`
  - [ ] AI 응답을 Python 딕셔너리로 변환
- [ ] 파서 실패 시 처리 (`OutputFixingParser`)

---

## 모듈 05: 메모리와 대화 관리

> **학습 목표:** 대화 기록을 저장하고 관리하여 맥락을 이어가는 멀티턴 챗봇을 만든다.

- [ ] 메모리가 필요한 이유
  - [ ] LLM은 기본적으로 무상태(stateless): 이전 대화를 기억하지 못함
  - [ ] `chat_history` 를 직접 관리하는 방식 이해
- [ ] `ChatMessageHistory` 로 대화 기록 저장
  - [ ] `add_user_message()`, `add_ai_message()` 로 메시지 추가
  - [ ] 기록된 메시지를 프롬프트에 삽입하여 맥락 유지
- [ ] `MessagesPlaceholder` 로 대화 기록을 프롬프트에 동적 삽입
- [ ] `RunnableWithMessageHistory` 로 자동 히스토리 관리
  - [ ] `session_id` 로 여러 사용자/세션 분리 관리
- [ ] 메모리 전략 비교
  - [ ] 전체 기록 유지 (`ConversationBufferMemory`): 단순, 토큰 증가
  - [ ] 요약 방식 (`ConversationSummaryMemory`): 토큰 절약, 요약 비용 발생
  - [ ] 최근 N개만 유지 (`ConversationBufferWindowMemory`): 균형적

---

## 모듈 06: 문서 로딩과 텍스트 분할

> **학습 목표:** 다양한 형식의 문서를 불러오고, RAG를 위해 적절한 크기로 분할하는 방법을 익힌다.

- [ ] `Document` 객체 구조 이해
  - [ ] `page_content`: 실제 텍스트
  - [ ] `metadata`: 출처, 페이지 번호 등 부가 정보
- [ ] 문서 로더 (Document Loaders)
  - [ ] `TextLoader`: `.txt` 파일 로드
  - [ ] `PyPDFLoader`: PDF 파일 로드 (페이지별 분리)
  - [ ] `WebBaseLoader`: 웹 페이지 로드 (BeautifulSoup 활용)
  - [ ] `CSVLoader`: CSV 파일 로드
- [ ] 텍스트 분할 (Text Splitters)
  - [ ] `RecursiveCharacterTextSplitter`: 가장 범용적인 분할기
    - [ ] `chunk_size`: 청크 최대 글자 수
    - [ ] `chunk_overlap`: 청크 간 겹치는 글자 수 (맥락 보존)
  - [ ] `CharacterTextSplitter`: 특정 구분자로 분할
  - [ ] 청크 크기와 오버랩이 RAG 성능에 미치는 영향 이해

---

## 모듈 07: 임베딩과 벡터 저장소

> **학습 목표:** 텍스트를 벡터로 변환하고, 의미 기반 유사도 검색을 벡터 저장소로 구현한다.

- [ ] 임베딩(Embedding) 개념
  - [ ] 텍스트를 숫자 벡터로 변환하는 이유 (의미를 수치로 표현)
  - [ ] 의미가 비슷한 텍스트는 벡터 공간에서 가깝게 위치
- [ ] `GoogleGenerativeAIEmbeddings`
  - [ ] `embed_query()`: 단일 텍스트 임베딩
  - [ ] `embed_documents()`: 여러 텍스트 일괄 임베딩
  - [ ] 코사인 유사도로 벡터 간 거리 직접 계산해보기
- [ ] 벡터 저장소 (Vector Store)
  - [ ] `FAISS` (Facebook AI Similarity Search): 로컬 인메모리 저장소
    - [ ] `from_documents()` 로 문서 일괄 저장
    - [ ] `similarity_search()` 로 유사 문서 검색
    - [ ] `save_local()` / `load_local()` 로 로컬 저장 및 불러오기
  - [ ] `Chroma`: 영구 저장 지원 벡터 DB
    - [ ] `persist_directory` 로 디스크에 저장
- [ ] 리트리버 (Retriever)
  - [ ] `as_retriever()` 로 벡터 저장소를 리트리버로 변환
  - [ ] `k` 파라미터: 상위 k개 유사 문서 반환

---

## 모듈 08: RAG

> **학습 목표:** 검색 증강 생성(RAG) 파이프라인을 구축하여 외부 문서 기반의 정확한 AI 답변 시스템을 만든다.

- [ ] RAG (Retrieval-Augmented Generation) 개념
  - [ ] 일반 LLM의 한계: 학습 데이터 외 최신 정보 없음, 환각(Hallucination) 발생
  - [ ] RAG 흐름: 질문 → 벡터 검색 → 관련 문서 → LLM → 답변
- [ ] RAG 파이프라인 직접 구축
  - [ ] 문서 로드 → 분할 → 임베딩 → 벡터 저장소 저장
  - [ ] 질문 입력 → 유사 문서 검색 → 프롬프트에 삽입 → LLM 호출
- [ ] `create_retrieval_chain` 으로 체인 자동화
  - [ ] `create_stuff_documents_chain`: 검색된 문서를 LLM에 전달
  - [ ] `create_retrieval_chain`: 리트리버와 문서 체인 연결
- [ ] 대화형 RAG (Conversational RAG)
  - [ ] `create_history_aware_retriever`: 대화 기록을 고려한 검색어 재작성
  - [ ] 이전 대화 맥락을 반영한 후속 질문 처리
- [ ] RAG 성능 개선 포인트
  - [ ] 청크 크기 / 오버랩 조정
  - [ ] 검색 결과 수 (`k`) 조정
  - [ ] 프롬프트에 "모르면 모른다고 답하라" 지시 추가

---

## 모듈 09: 에이전트와 도구

> **학습 목표:** `@tool` 데코레이터로 커스텀 도구를 만들고, 에이전트가 스스로 도구를 선택·실행하는 자율 시스템을 구현한다.

- [ ] 에이전트 개념
  - [ ] 일반 LLM / RAG vs 에이전트 차이
  - [ ] ReAct (Reason + Act) 사이클: Thought → Action → Observation → 반복
  - [ ] 탐정 + 도구 상자 비유로 에이전트 동작 이해
- [ ] `@tool` 데코레이터로 커스텀 도구 정의
  - [ ] Docstring이 LLM에게 전달되는 도구 설명(description)이 됨
  - [ ] 타입 힌트로 입력 스키마 자동 생성
  - [ ] `tool.name`, `tool.description`, `tool.args` 속성 확인
  - [ ] 도구 직접 호출 테스트 (`tool.invoke(...)`)
- [ ] `create_tool_calling_agent` + `AgentExecutor` 구성
  - [ ] Gemini 네이티브 함수 호출 방식 (JSON 구조화 출력)
  - [ ] `MessagesPlaceholder('agent_scratchpad')` 를 프롬프트에 필수 추가
  - [ ] `verbose=True` 로 도구 호출 과정 관찰
  - [ ] `max_iterations` 로 무한루프 방지
  - [ ] `handle_parsing_errors=True` 로 파싱 오류 자동 복구
- [ ] 내장 도구 활용
  - [ ] `DuckDuckGoSearchRun` 으로 실시간 웹 검색 추가
- [ ] Pydantic `args_schema` 로 복잡한 입력 구조화
  - [ ] `BaseModel` + `Field` 로 다중 인자 도구 정의
  - [ ] `Optional` 타입으로 선택 인자 처리
- [ ] `create_tool_calling_agent` vs `create_react_agent` 비교
  - [ ] 네이티브 JSON 함수 호출 vs 텍스트 파싱 방식 차이

---
