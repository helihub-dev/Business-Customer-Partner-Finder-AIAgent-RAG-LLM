# Prompt Tracing & Performance Monitoring

**Version:** 1.0  
**Last Updated:** October 23, 2025

---

## Overview

Prompt tracing enables performance monitoring, cost analysis, and optimization of LLM calls across the AxleWave Discovery system.

**Key Capabilities**:
- Automatic logging of every LLM call
- Real-time monitoring via JSON log file
- Performance metrics (latency, tokens, cost)
- Success/failure tracking
- UI dashboard with downloadable traces

---

## Architecture

```
Agent → LLM Client → start_trace() → API Call → end_trace() → logs/prompt_traces.json
```

**Components**:
- `PromptTracer` class (`utils/prompt_tracer.py`)
- LLM client wrappers (`utils/llm_client.py`)
- JSON log storage (rolling 1000 traces)
- Streamlit UI integration

---

## Implementation

### Tracer Methods

```python
class PromptTracer:
    def start_trace(prompt_name, prompt_text, input_vars) -> trace_id
    def end_trace(trace_id, success, output, tokens_used, error)
    def get_recent_traces(limit=50) -> list
    def get_stats() -> dict
```

### LLM Client Integration

```python
# Automatic tracing wrapper
result = self.llm.generate_json_with_trace(
    prompt,
    prompt_name="ENRICHMENT_EXTRACT_COMPANY_INFO",
    input_vars={"title": title, "url": url}
)
```

**Used in**:
- Enrichment Agent: Company data extraction
- Scoring Agent: Fit score calculation
- RAG System: Search query generation

---

## Trace Data Structure

```json
{
  "trace_id": "ENRICHMENT_EXTRACT_COMPANY_INFO_1729641234567",
  "prompt_name": "ENRICHMENT_EXTRACT_COMPANY_INFO",
  "timestamp": "2025-10-23T00:34:23.130Z",
  "input_vars": {"title": "Sonic Automotive...", "url": "..."},
  "latency_seconds": 2.67,
  "tokens_used": 425,
  "estimated_cost": 0.00085,
  "success": true,
  "error": null
}
```

**Key Fields**:
- `latency_seconds`: LLM call duration
- `tokens_used`: Estimated tokens 
- `estimated_cost`: $0.002 per 1K tokens
- `success`: true/false status

---

## Performance Metrics

### Token Estimation
`tokens ≈ (prompt_length + output_length)`

### Cost Estimation
`cost = tokens × $0.000002`

### Aggregate Statistics

```python
{
  "total_traces": 150,
  "success_rate": 96.7,
  "avg_latency": 2.34,
  "total_tokens": 52450,
  "total_cost": 0.1049,
  "by_prompt": {
    "ENRICHMENT_EXTRACT_COMPANY_INFO": {
      "count": 80,
      "success_rate": 97.5,
      "avg_latency": 2.67,
      "avg_tokens": 425
    }
  }
}
```

---

## Usage

### Real-Time Monitoring

```bash
tail -f logs/prompt_traces.json
```

### Programmatic Access

```python
from utils.prompt_tracer import get_tracer

tracer = get_tracer()
stats = tracer.get_stats()
print(f"Success rate: {stats['success_rate']}%")
print(f"Total cost: ${stats['total_cost']}")
```

### UI Dashboard

Streamlit sidebar displays:
- Total traces
- Success rate
- Average latency
- Total cost
- Per-prompt breakdown
- Download traces (CSV/JSON)

---

## Best Practices

1. **Naming**: Use descriptive prompt names (`ENRICHMENT_EXTRACT_COMPANY_INFO`)
2. **Truncation**: Limit input_vars to 50-100 chars for logging
3. **Error Handling**: Wrap traced calls in try-except
4. **Log Rotation**: Automatic (last 1000 traces), backup periodically
5. **Monitoring**: Alert if success_rate < 95% or avg_latency > 5s

---

## Sample Analysis

**Discovery Session** (10 companies):
```
Total Traces: 151
Success Rate: 97.4%
Duration: 8m 32s
Cost: $0.0294

Breakdown:
- RAG_GENERATE_SEARCH_QUERIES: 1 call, 1.2s, $0.0006
- ENRICHMENT_EXTRACT_COMPANY_INFO: 100 calls, 267s, $0.017
- SCORING_EVALUATE_COMPANY: 50 calls, 106s, $0.0116
```

**Insights**:
- Enrichment is bottleneck (2.67s avg)
- High success rate (97.4%)
- Opportunity: Parallel enrichment → 267s to 67s

---

## References

- Tracer: `/utils/prompt_tracer.py`
- LLM Client: `/utils/llm_client.py`
- Log File: `/logs/prompt_traces.json`
- UI: `/app.py`
