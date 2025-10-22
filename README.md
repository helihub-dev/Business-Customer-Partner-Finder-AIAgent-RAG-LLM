# Business-Customer-Partner-Finder-AIAgent-RAG-LLM

This project is build for a fictitious company "AxleWave" where I have designed a prototype (AI-powered multi-agent) to discover top 10 potential customers and top 10 potential partners for AxleWave Technologies' DealerFlow Cloud platform.

## Overview

This prototype uses multiple AI agents to:
- Discover companies that match ideal customer/partner profiles
- Enrich company data from public sources
- Validate against user-specified criteria
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
## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.9+ |
| Vector Store | ChromaDB | 0.4.22 |
| Embeddings | Sentence Transformers | 2.7.0 |
| LLM (Primary) | Perplexity Sonar | Latest |
| LLM (Alternative) | OpenAI GPT-4o-mini | Latest |
| Search | Tavily API | Latest |
| UI | Streamlit | 1.28.0 |

## Features

✅ **Multi-Format Document Support**
- Word documents (.docx)
- PDF files (.pdf)
- Excel spreadsheets (.xlsx)
- PowerPoint presentations (.pptx)

✅ **ChromaDB Vector Store**
- Semantic embeddings with sentence-transformers
- Persistent storage across restarts
- Excellent search quality

✅ **Intelligent Criteria Filtering**
- LLM-based validation during enrichment
- Filters by location, size, category, technology
- Shows filtered companies with reasons
- No extra LLM calls (integrated into enrichment)

✅ **Multi-Agent Architecture**
- Research Agent: Web search via Tavily API
- Enrichment Agent: Extract structured data + validate criteria + pattern matching for locations
- Scoring Agent: Rank by fit with RAG context
- Validation Agent: Deduplication, quality checks, and location validation (rejects incomplete data)

✅ **Enhanced Prompt Tracing**
- Organized by agent type
- Cost and latency calculation explanations
- Show all traces (up to 1000)
- Download traces (CSV/JSON)
- Usage count per prompt


## Project Structure

```
axlewave-discovery/
├── agents/              # AI agent implementations
│   ├── research_agent.py
│   ├── enrichment_agent.py    # Now includes criteria validation
│   ├── scoring_agent.py
│   └── validation_agent.py
├── data/
│   ├── axlewave_docs/   # Company documents (9 files)
│   └── vector_store/    # ChromaDB storage
├── prompts/             # Prompt templates
├── utils/               # Helper functions
│   ├── vector_store.py      # ChromaDB vector store
│   ├── rag.py               # RAG system
│   ├── llm_client.py        # LLM interface
│   ├── document_loader.py   # Multi-format loader
│   └── prompt_tracer.py     # Prompt tracing
├── app.py              # Streamlit UI
├── orchestrator.py     # Agent coordinator
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
└── setup_vectorstore.py # Vector store initialization
```

## API Keys Required

- **OpenAI** / **Anthropic** / **Perplexity**: For LLM reasoning (Perplexity has free $5 credit)
- **Tavily**: For web search (get free key at tavily.com)
- **LangSmith** (optional): For prompt tracing

## API Keys & Costs

| Service | Purpose | Cost | Free Tier |
|---------|---------|------|-----------|
| Tavily | Web search | $0.01/discovery | 1000 searches/month |
| OpenAI/Perplexity | LLM | ~$0.15/discovery | Varies |
| ChromaDB | Vector store | $0 | Local/free |

**Estimated cost per discovery:** ~$0.16-0.20


## Quick Start

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required:
- `TAVILY_API_KEY` - Free at [tavily.com](https://tavily.com)
- `PERPLEXITY_API_KEY` (Primary) - For Perplexity Sonar LLM
- `OPENAI_API_KEY` (Alternative) - For OpenAI GPT-4o-mini

### 4. Initialize Vector Store (One-time)

```bash
python setup_vectorstore.py
```

### 5. Run the Application

```bash
streamlit run app.py
# Access at http://localhost:8501
```

### 6. View logs
```bash
tail -f logs/prompt_traces.json
```

## Configuration

### Search Settings

Adjust in `orchestrator.py`:
```python
max_per_query = 20  # Results per search query
min_score = 20      # Minimum fit score (0-100)
```

## Troubleshooting

### Q. Discovery Taking Too Long?

**Expected timing:**
- 5 results: 3-4 mins
- 10 results: 7-8 minutes
- 20 results: more than 8 mins

**If slower than expected:**

1. **Check what's happening:**
   ```bash
   tail -f logs/prompt_traces.json
   ```

2. **Check API keys and environment:**
   ```bash
   cat .env | grep API_KEY
   python -c "from utils.vector_store import get_vector_store; print(get_vector_store())"
   ```

3. **View progress in UI:**
   - Progress bar shows enrichment status
   - Status text shows current company

### Q. Port already in use?

If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8502
# Access at http://localhost:8502
```
### Q. Only getting few results?

If you request 10 but get 5-7:
1. Criteria too strict - Try broader criteria
2. Increase search: Edit `orchestrator.py`, set `max_per_query = 30`
3. Lower threshold: Set `min_score = 10`

### Q. Missing dependencies?

If you get import errors:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Known Limitations

1. **Python 3.9+ Required:** Requires local Python installation
2. **API Rate Limits:** Tavily free tier limited to 1000 searches/month
3. **RAG Failures:** ~17% failure rate due to API quota limits
4. **Search Depth:** 100 companies per discovery (5 queries × 20 results)

## Future Enhancements

1. **Parallel Processing:** Concurrent agent execution
2. **Batch Processing:** Multiple discovery runs
4. **Advanced Filtering:** Maybe more sophisticated validation rules can benefit











