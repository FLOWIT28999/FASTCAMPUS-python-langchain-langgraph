# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LangChain 강의 실습 코드. Google Gemini를 LLM으로 사용하며, 각 모듈은 독립적인 Jupyter 노트북으로 구성된다.

## Commands

```bash
# 의존성 설치
uv sync

# Jupyter 실행
uv run jupyter lab

# 특정 노트북 실행
uv run jupyter nbconvert --to notebook --execute 00_setup/모듈00_환경설정.ipynb
```

## Environment Setup

`.env.example`을 복사해 `.env`를 만들고 Gemini API 키를 설정:

```
GOOGLE_API_KEY=your_api_key_here
```

API 키 발급: https://aistudio.google.com/

## Architecture

각 모듈은 `XX_name/모듈XX_이름.ipynb` 형태의 Jupyter 노트북으로 구성된다. 모든 노트북은 독립 실행 가능하며, `.env`에서 `load_dotenv()`로 API 키를 로드한다.

### 모듈 진행 순서

| 모듈 | 디렉토리 | 핵심 개념 |
|------|----------|-----------|
| 00 | `00_setup/` | uv 환경, `.env`, API 키 검증 |
| 01 | `01_hello/` | `ChatGoogleGenerativeAI`, `invoke()`, `stream()`, 메시지 타입 |
| 02 | `02_prompts/` | `ChatPromptTemplate`, `partial()`, `FewShotChatMessagePromptTemplate` |
| 03 | `03_lcel/` | LCEL `|` 파이프, `RunnableLambda`, `RunnableParallel` |
| 04 | `04_output_parsers/` | `StrOutputParser`, `PydanticOutputParser`, `JsonOutputParser` |
| 05 | `05_memory/` | `ChatMessageHistory`, `RunnableWithMessageHistory`, 세션 관리 |
| 06 | `06_document_loaders/` | `TextLoader`, `PyPDFLoader`, `WebBaseLoader`, `RecursiveCharacterTextSplitter` |
| 07 | `07_embeddings/` | `GoogleGenerativeAIEmbeddings`, FAISS, Chroma 벡터 저장소 |
| 08 | `08_rag/` | RAG 파이프라인, `create_retrieval_chain`, Conversational RAG |
| 09 | `09_agents/` | `@tool` 데코레이터, `create_tool_calling_agent`, `AgentExecutor` |

### 핵심 패턴

**기본 LLM 호출:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
```

**LCEL 체인:**
```python
chain = prompt | llm | output_parser
result = chain.invoke({"input": "..."})
```

**RAG 파이프라인:** 문서 로드 → `RecursiveCharacterTextSplitter` → `GoogleGenerativeAIEmbeddings` → FAISS/Chroma → `create_retrieval_chain`

**에이전트:** `@tool` 데코레이터 (docstring이 LLM에게 전달되는 도구 설명) → `create_tool_calling_agent` → `AgentExecutor(verbose=True)`

### 로컬 저장 데이터

- `07_embeddings/chroma_db/`, `07_embeddings/pipeline_db/`: Chroma 벡터 DB 파일
- `08_rag/rag_db/`: RAG용 벡터 DB 파일
- `06_document_loaders/data/`, `08_rag/data/`: 실습용 문서 데이터
