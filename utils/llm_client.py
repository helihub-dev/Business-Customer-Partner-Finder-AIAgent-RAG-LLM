"""LLM client wrapper - supports multiple providers including free options."""
import os
import requests
import json
from typing import Optional, Dict, Any


class LLMClient:
    """Unified LLM client with fallback to demo mode."""
    
    def __init__(self, provider: str = "demo", model: Optional[str] = None):
        """Initialize LLM client."""
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "demo":
            print("⚠️  Running in DEMO mode - using simulated responses")
            self.api_key = "demo"
        elif self.provider == "perplexity":
            self.api_key = os.getenv("PERPLEXITY_API_KEY")
            self.model = model or "sonar"  # Perplexity's default model
            if not self.api_key:
                raise ValueError("PERPLEXITY_API_KEY not set")
        elif self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.model = model or "claude-3-5-haiku-20241022"
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4o-mini"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.1,
                 max_tokens: int = 2000,
                 json_mode: bool = False) -> str:
        """Generate text using LLM."""
        
        if self.provider == "demo":
            return self._demo_response(prompt, json_mode)
        
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
    
    def _demo_response(self, prompt: str, json_mode: bool = False) -> str:
        """Generate demo responses for testing."""
        prompt_lower = prompt.lower()
        
        if "search queries" in prompt_lower or "generate queries" in prompt_lower:
            return json.dumps({
                "queries": [
                    "automotive dealership management software",
                    "car dealer inventory system",
                    "dealership CRM platform"
                ]
            })
        
        if "extract" in prompt_lower and "company" in prompt_lower:
            return json.dumps({
                "name": "Demo Auto Solutions",
                "website": "https://demo-auto.example.com",
                "locations": ["United States"],
                "size": "50-200 employees",
                "description": "Automotive software provider"
            })
        
        if "score" in prompt_lower or "fit score" in prompt_lower:
            return json.dumps({
                "fit_score": 75,
                "rationale": "Good potential customer based on industry alignment and company size."
            })
        
        if json_mode:
            return json.dumps({"response": "Demo mode active"})
        return "This is a demo response. Please configure API keys for full functionality."
    
    def generate_json(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.1) -> Dict[str, Any]:
        """Generate JSON response."""
        if self.provider == "demo":
            response = self._demo_response(prompt, json_mode=True)
            return json.loads(response)
        
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
