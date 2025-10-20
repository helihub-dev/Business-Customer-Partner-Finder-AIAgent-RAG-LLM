"""Prompt tracing utility for logging and analyzing prompt performance."""
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import os


class PromptTracer:
    """Traces prompt executions for performance monitoring."""
    
    def __init__(self, log_file: str = "logs/prompt_traces.json"):
        """Initialize tracer."""
        self.log_file = log_file
        self.current_traces = []
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Create logs directory if it doesn't exist."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def start_trace(self, prompt_name: str, prompt_text: str, 
                   input_vars: Dict[str, Any]) -> str:
        """Start tracing a prompt execution."""
        trace_id = f"{prompt_name}_{int(time.time() * 1000)}"
        
        trace = {
            "trace_id": trace_id,
            "prompt_name": prompt_name,
            "timestamp": datetime.utcnow().isoformat(),
            "input_vars": {k: str(v)[:100] for k, v in input_vars.items()},  # Truncate
            "prompt_length": len(prompt_text),
            "start_time": time.time()
        }
        
        self.current_traces.append(trace)
        return trace_id
    
    def end_trace(self, trace_id: str, success: bool, 
                 output: Optional[str] = None, 
                 tokens_used: Optional[int] = None,
                 error: Optional[str] = None):
        """End tracing and log results."""
        trace = next((t for t in self.current_traces if t["trace_id"] == trace_id), None)
        if not trace:
            return
        
        end_time = time.time()
        trace["end_time"] = end_time
        trace["latency_seconds"] = round(end_time - trace["start_time"], 2)
        trace["success"] = success
        trace["tokens_used"] = tokens_used or 0
        trace["output_length"] = len(output) if output else 0
        trace["error"] = error
        
        # Estimate cost (rough estimate: $0.002 per 1K tokens)
        if tokens_used:
            trace["estimated_cost"] = round(tokens_used * 0.000002, 6)
        
        # Save to file
        self._save_trace(trace)
        
        # Remove from current traces
        self.current_traces = [t for t in self.current_traces if t["trace_id"] != trace_id]
    
    def _save_trace(self, trace: Dict):
        """Append trace to log file."""
        try:
            # Read existing traces
            traces = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    try:
                        traces = json.load(f)
                    except:
                        traces = []
            
            # Append new trace
            traces.append(trace)
            
            # Keep only last 1000 traces
            traces = traces[-1000:]
            
            # Write back
            with open(self.log_file, 'w') as f:
                json.dump(traces, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save trace: {e}")
    
    def get_recent_traces(self, limit: int = 50) -> list:
        """Get recent traces."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    traces = json.load(f)
                    return traces[-limit:]
            return []
        except:
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics."""
        traces = self.get_recent_traces(limit=1000)
        
        if not traces:
            return {
                "total_traces": 0,
                "success_rate": 0,
                "avg_latency": 0,
                "total_tokens": 0,
                "total_cost": 0
            }
        
        successful = [t for t in traces if t.get("success")]
        
        return {
            "total_traces": len(traces),
            "success_rate": round(len(successful) / len(traces) * 100, 1),
            "avg_latency": round(sum(t.get("latency_seconds", 0) for t in traces) / len(traces), 2),
            "total_tokens": sum(t.get("tokens_used", 0) for t in traces),
            "total_cost": round(sum(t.get("estimated_cost", 0) for t in traces), 4),
            "by_prompt": self._stats_by_prompt(traces)
        }
    
    def _stats_by_prompt(self, traces: list) -> Dict[str, Dict]:
        """Get stats grouped by prompt name."""
        by_prompt = {}
        
        for trace in traces:
            name = trace.get("prompt_name", "unknown")
            if name not in by_prompt:
                by_prompt[name] = {
                    "count": 0,
                    "success": 0,
                    "total_latency": 0,
                    "total_tokens": 0
                }
            
            by_prompt[name]["count"] += 1
            if trace.get("success"):
                by_prompt[name]["success"] += 1
            by_prompt[name]["total_latency"] += trace.get("latency_seconds", 0)
            by_prompt[name]["total_tokens"] += trace.get("tokens_used", 0)
        
        # Calculate averages
        for name, stats in by_prompt.items():
            count = stats["count"]
            stats["success_rate"] = round(stats["success"] / count * 100, 1)
            stats["avg_latency"] = round(stats["total_latency"] / count, 2)
            stats["avg_tokens"] = round(stats["total_tokens"] / count, 0)
        
        return by_prompt


# Global tracer instance
_tracer = None

def get_tracer() -> PromptTracer:
    """Get global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = PromptTracer()
    return _tracer
