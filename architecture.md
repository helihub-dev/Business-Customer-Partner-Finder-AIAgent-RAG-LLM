# AxleWave Discovery - System Architecture

## High-Level Architecture
For seeing the high-level architecture go to /diagrams/system_architecture.mmd or click here: https://github.com/helihub-dev/Business-Customer-Partner-Finder-AIAgent-RAG-LLM/blob/main/diagrams/system_architecture.mmd

## Workflow Sequence
For seeing the sequence diagram go to /diagrams/workflow_sequence.mmd or click here: https://github.com/helihub-dev/Business-Customer-Partner-Finder-AIAgent-RAG-LLM/blob/main/diagrams/workflow_sequence.mmd

## Component Details

### 1. Research Agent
- **Purpose**: Discover companies via web search
- **Technology**: Tavily API (free tier)
- **Input**: Search queries
- **Output**: Raw search results with URLs and content
- **Key Features**: 
  - Multi-query search
  - Deduplication
  - Advanced search depth

### 2. Enrichment Agent
- **Purpose**: Extract structured company data + validate criteria
- **Technology**: LLM (GPT-4o-mini or Perplexity Sonar)
- **Input**: Search results + additional criteria
- **Output**: Structured company info (name, website, locations, size) + criteria match
- **Key Features**:
  - JSON extraction with criteria validation
  - URL cleaning (extracts actual company domains, not LinkedIn/Crunchbase)
  - Location extraction with regex pattern matching fallback
  - Pattern matching: Searches content for "based in [City, State]" patterns
  - Returns "Location not specified" if no location found (filtered by validation)
  - Integrated criteria filtering (no extra LLM calls)
  - Match reasoning for transparency

### 3. Scoring Agent
- **Purpose**: Rank companies by fit
- **Technology**: RAG + LLM
- **Input**: Enriched companies + AxleWave context
- **Output**: Scored companies (0-100) with rationale
- **Key Features**:
  - Customer vs Partner criteria
  - Context-aware evaluation
  - Rationale generation

### 4. Validation Agent
- **Purpose**: Ensure data quality and filter incomplete data
- **Technology**: Rule-based validation
- **Input**: Scored companies
- **Output**: Top N validated companies
- **Key Features**:
  - Required field checks (including 'locations')
  - Location quality validation (rejects "Location not specified")
  - Score threshold (20+ for inclusivity, configurable)
  - URL format validation
  - Final deduplication by URL and company name
  - Similarity matching for company names

### 5. RAG System
- **Purpose**: Provide AxleWave context to agents
- **Technology**: ChromaDB + LLM
- **Components**:
  - Vector Store (ChromaDB with persistence)
  - Document embeddings (sentence-transformers)
  - Semantic search
  - Context retrieval
  - Query generation with criteria integration

### 6. Prompt Tracing System
- **Purpose**: Monitor and analyze LLM prompt performance
- **Technology**: Custom PromptTracer utility
- **Features**:
  - Automatic trace logging (last 1000 traces)
  - Cost calculation: `tokens × $0.0002` (Perplexity pricing) or `tokens × $0.000002` (OpenAI pricing)
  - Latency tracking: `end_time - start_time` in seconds
  - Success rate monitoring
  - Organized by agent type (Research, Enrichment, Scoring, Validation)
  - Export to CSV/JSON
  - Usage count per prompt
- **Storage**: `logs/prompt_traces.json`
- **UI**: Streamlit sidebar with expandable trace viewer

## Data Flow

```
AxleWave Docs → Vector Store → RAG System
                                    ↓
User Query + Criteria → Orchestrator → Generate Queries (RAG + Criteria)
                ↓
         Research Agent (Tavily) - 5 queries × 5-10 results = 25-50 companies
                ↓
         [Raw Search Results]
                ↓
         Enrichment Agent (LLM) - Extract + Validate Criteria + Pattern Match Locations
                ↓
         [Structured Companies with criteria_match + locations field]
                ↓
         Filter by criteria_match → [Matching] + [Filtered Out (criteria)]
                ↓
         Deduplication (by URL and company name)
                ↓
         Scoring Agent (RAG + LLM) - Score only matching companies
                ↓
         [Scored & Ranked]
                ↓
         Validation Agent - Quality checks + location validation (rejects "Location not specified")
                ↓
         [Top 10 Valid Results] + [Filtered Companies List with Reasons]
                ↓
         User (CSV/JSON) + Prompt Traces + Filtered Report
```

## Technology Stack

| Layer | Technology | Cost |
|-------|-----------|------|
| Vector Store | ChromaDB (persistent) | Free (local) |
| Embeddings | sentence-transformers | Free (local) |
| LLM (Primary) | Perplexity Sonar | $1.00/1M tokens (input & output) |
| LLM (Alternative) | OpenAI gpt-4o-mini | $0.15-$0.60/1M tokens |
| Search | Tavily API | Free (1000/month) |
| UI | Streamlit | Free |
| Orchestration | Python + Custom | Free |
| Storage | Local filesystem | Free |
| Tracing | Custom PromptTracer | Free |

**Total Cost**: ~$0.16-0.20 per discovery



## Deployment Architecture

```
Local Python Environment
├── Python 3.9+ Runtime
├── Virtual Environment (venv/)
├── ChromaDB (local storage: ./data/vector_store/)
├── Streamlit Server (port 8501)
├── Prompt Tracer (logs/prompt_traces.json)
└── API Connections
    ├── Perplexity/ OpenAI API (HTTPS)
    └── Tavily API (HTTPS)

File Structure:
├── Application Files:
│   ├── app.py, orchestrator.py, config.py
│   ├── agents/, utils/, prompts/
│   └── data/axlewave_docs (documents)
├── Persistent Storage:
│   ├── ./data/vector_store (ChromaDB)
│   └── ./logs (traces)
└── Configuration:
    └── .env (Environment Variables)
```

**Benefits:**
- Consistent across all machines
- Easy deployment and sharing
- Persistent data across restarts
- One-command setup

## Security & Privacy

- **API Keys**: Stored in `.env` (not committed)
- **Data Storage**: Local only (ChromaDB)
- **No PII**: Only public company information
- **No Scraping**: Uses approved APIs only
