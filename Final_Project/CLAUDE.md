# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

경쟁사 리서치 에이전트 — 기업 URL을 입력하면 Exa.ai로 경쟁사를 탐색하고, 3개의 전문 AI 에이전트(기업분석, 제품오퍼링, 제품평가)가 각 경쟁사를 분석하여 PDF 보고서를 생성하는 멀티 에이전트 시스템. n8n 노코드 워크플로우(`n8n.json`)를 Python 코드로 전환한 프로젝트.

## Tech Stack

- **Language**: Python 3.11+
- **Package Manager**: uv
- **LLM**: Google Gemini (gemini-2.5-flash) via `langchain-google-genai`
- **Framework**: LangChain + LangGraph
- **Search Tools**: Perplexity API (sonar), Tavily API
- **Competitor Discovery**: Exa.ai (neural search)
- **Output Parsing**: Pydantic + PydanticOutputParser
- **PDF Generation**: weasyprint (requires `brew install pango` on macOS)

## Commands

```bash
# Initialize project
uv init && uv add langchain-google-genai langchain-community langgraph langchain-text-splitters python-dotenv pydantic tavily-python requests weasyprint

# Run the agent
uv run python main.py
```

## Architecture

The system is a LangGraph StateGraph with 3 nodes in a loop:

```
[START] → find_competitors → analyze_company ←→ (loop) → generate_report → [END]
```

1. **find_competitors**: Exa.ai `findSimilar` API → deduplicate → top 3
2. **analyze_company**: Runs 3 agents sequentially per competitor (with 2s delay between companies):
   - `company_agent` — corporate info, financials, news
   - `product_agent` — features, pricing, tech stack
   - `review_agent` — reviews, pros/cons, reputation
3. **generate_report**: LLM synthesizes all results → HTML/CSS rendering → weasyprint PDF

**State** (`ResearchState`): `company_url`, `competitors`, `current_index`, `analyses` (reducer: `operator.add`), `final_report`, `pdf_path`

**Loop router**: `current_index < len(competitors)` → "continue" (back to analyze_company), else → "done" (to generate_report)

## Source Layout

- `src/config.py` — env vars (.env), LLM singleton
- `src/tools.py` — `@tool` wrappers: `tavily_search`, `perplexity_search`
- `src/schemas.py` — Pydantic models: `CompanyAnalysis`, `ProductOffering`, `ProductReview` + their parsers
- `src/agents.py` — `create_research_agent()` factory → 3 AgentExecutor instances
- `src/pipeline.py` — `find_similar_companies()`, `refine_competitors()`, `analyze_single_company()`
- `src/report.py` — `generate_final_report()`, `render_to_html()`, `convert_to_pdf()`
- `src/graph.py` — `ResearchState`, node functions, loop router, compiled `app`
- `main.py` — CLI entrypoint

## Required Environment Variables (.env)

```
GOOGLE_API_KEY=       # Gemini LLM
EXA_API_KEY=          # Competitor discovery
TAVILY_API_KEY=       # Web search tool
PERPLEXITY_API_KEY=   # Real-time search tool
```

## Key Constraints

- Exa.ai free tier: 1,000 requests/month — use small `max_count` during testing
- 2-second delay between competitor analyses for API rate limiting
- PDF output: A4 size, Nanum Gothic font for Korean support
- Agent errors should return empty values, not break the pipeline (`handle_parsing_errors=True`)
- Reference docs: `PRD.md` (full spec), `n8n_to_code.md` (n8n→code mapping), `TODO.md` (implementation phases)
