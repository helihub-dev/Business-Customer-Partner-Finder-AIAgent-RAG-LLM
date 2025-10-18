# Business-Customer-Partner-Finder-AIAgent-RAG-LLM

This project is build for a fictitious company "AxleWave" where I have designed a prototype (AI-powered multi-agent) to discover top 10 potential customers and top 10 potential partners for AxleWave Technologies' DealerFlow Cloud platform.

## Overview

This prototype uses multiple AI agents to:
- Discover companies that match ideal customer/partner profiles
- Enrich company data from public sources
- Score and rank companies by fit
- Generate rationale for recommendations

## Architecture

```
┌─────────────────┐
│   Streamlit UI  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Orchestrator │
    └────┬────┘
         │
    ┌────┴────────────────────────┐
    │                             │
┌───▼────┐  ┌──────┐  ┌────────┐ │
│Research│  │Enrich│  │Scoring │ │
│ Agent  │─▶│Agent │─▶│ Agent  │ │
└────────┘  └──────┘  └────┬───┘ │
                           │     │
                      ┌────▼────┐│
                      │Validation││
                      │  Agent  ││
                      └─────────┘│
                                 │
                        ┌────────▼──┐
                        │ Vector DB │
                        │   (RAG)   │
                        └───────────┘
```

## Project Structure
```
axlewave-discovery/
├── agents/              # AI agent implementations
│   ├── research_agent.py
│   ├── enrichment_agent.py
│   ├── scoring_agent.py
│   └── validation_agent.py
├── data/
│   ├── axlewave_docs/   # Company documents
│   └── vector_store/    # Chroma DB
├── prompts/             # Prompt templates
├── utils/               # Helper functions
├── tests/               # Unit tests
├── app.py              # Streamlit UI
├── main.py             # CLI interface
├── config.py           # Configuration
└── requirements.txt
```

## API Keys Required

- **OpenAI** / **Anthropic** / **Perplexity**: For LLM reasoning (Perplexity has free $5 credit)
- **Tavily**: For web search (get free key at tavily.com)
- **LangSmith** (optional): For prompt tracing

