"""LLM client wrapper - supports multiple providers."""
import os
import requests
import json
from typing import Optional, Dict, Any
from .prompt_tracer import get_tracer


class LLMClient:
    """Unified LLM client for multiple providers."""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """Initialize LLM client."""
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "perplexity":
            self.api_key = os.getenv("PERPLEXITY_API_KEY")
            self.model = model or "sonar"
            if not self.api_key:
                raise ValueError("PERPLEXITY_API_KEY not set")
        elif self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.model = model or "claude-3-5-haiku-20241022"
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4o-mini"
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not set")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_with_trace(self,
                           prompt: str,
                           prompt_name: str = "unknown",
                           input_vars: Optional[Dict[str, Any]] = None,
                           **kwargs) -> str:
        """Generate with automatic tracing."""
        tracer = get_tracer()
        trace_id = tracer.start_trace(prompt_name, prompt, input_vars or {})
        
        try:
            result = self.generate(prompt, **kwargs)
            # Estimate tokens (rough: ~4 chars per token)
            tokens = (len(prompt) + len(result)) // 4
            tracer.end_trace(trace_id, success=True, output=result, tokens_used=tokens)
            return result
        except Exception as e:
            tracer.end_trace(trace_id, success=False, error=str(e))
            raise
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.1,
                 max_tokens: int = 2000,
                 json_mode: bool = False) -> str:
        """Generate text using LLM."""
        
        if self.provider == "perplexity":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        if self.provider == "anthropic":
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            messages = [{"role": "user", "content": prompt}]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["content"][0]["text"]
        
        elif self.provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        raise ValueError(f"Provider {self.provider} not implemented")
    
    def generate_json(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.1) -> Dict[str, Any]:
        """Generate JSON response."""
        
        if self.provider in ["anthropic", "perplexity"]:
            json_prompt = f"{prompt}\n\nRespond with valid JSON only, no other text."
            response = self.generate(
                prompt=json_prompt,
                system_prompt=system_prompt,
                temperature=temperature
            )
        else:
            response = self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                json_mode=True
            )
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)
    
    def generate_json_with_trace(self,
                                 prompt: str,
                                 prompt_name: str = "unknown",
                                 input_vars: Optional[Dict[str, Any]] = None,
                                 **kwargs) -> Dict[str, Any]:
        """Generate JSON with automatic tracing."""
        tracer = get_tracer()
        trace_id = tracer.start_trace(prompt_name, prompt, input_vars or {})
        
        try:
            result = self.generate_json(prompt, **kwargs)
            result_str = json.dumps(result)
            tokens = (len(prompt) + len(result_str)) // 4
            tracer.end_trace(trace_id, success=True, output=result_str, tokens_used=tokens)
            return result
        except Exception as e:
            tracer.end_trace(trace_id, success=False, error=str(e))
            raise
