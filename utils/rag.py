"""RAG (Retrieval Augmented Generation) utilities."""
from typing import Optional, List, Dict, Any
from .vector_store import VectorStore
from .llm_client import LLMClient


class RAGSystem:
    """RAG system combining vector store and LLM."""
    
    def __init__(self, vector_store: VectorStore, llm_client: LLMClient):
        """Initialize RAG system."""
        self.vector_store = vector_store
        self.llm = llm_client
    
    def query_with_context(self, 
                          query: str, 
                          system_prompt: Optional[str] = None,
                          n_context_chunks: int = 5) -> str:
        """Query LLM with relevant context from vector store."""
        
        # Retrieve relevant context
        context_chunks = self.vector_store.query(query, n_results=n_context_chunks)
        context = "\n\n".join(context_chunks)
        
        # Build prompt with context
        prompt = f"""Context about AxleWave Technologies:

{context}

Question: {query}

Answer based on the context provided:"""
        
        return self.llm.generate(prompt, system_prompt=system_prompt)
    
    def get_company_profile(self) -> str:
        """Get comprehensive company profile."""
        queries = [
            "company overview and product",
            "target customers and market",
            "key features and capabilities"
        ]
        
        all_context = []
        for q in queries:
            chunks = self.vector_store.query(q, n_results=3)
            all_context.extend([c['document'] for c in chunks])
        
        # Deduplicate and join
        unique_context = list(dict.fromkeys(all_context))
        return "\n\n".join(unique_context[:10])  # Top 10 chunks
    
    def generate_search_queries(self, query_type: str) -> List[str]:
        """Generate search queries for customer/partner discovery."""
        
        company_context = self.get_company_profile()
        
        prompt = f"""Based on this company profile:

{company_context}

Generate 5 specific web search queries to find potential {query_type}s.

For CUSTOMERS: Find companies that would buy this product (dealerships, dealer groups, OEMs)
For PARTNERS: Find companies that would integrate/partner (payment processors, CRM vendors, analytics providers)

Return ONLY a JSON array of search query strings, no explanation:
{{"queries": ["query1", "query2", ...]}}"""

        response = self.llm.generate_json(prompt)
        return response.get("queries", [])
