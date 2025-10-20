"""RAG (Retrieval Augmented Generation) utilities."""
from typing import Optional, List, Dict, Any
from .vector_store import VectorStore
from .llm_client import LLMClient
from prompts.prompts import RAG_QUERY_WITH_CONTEXT, RAG_GENERATE_SEARCH_QUERIES


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
        context_results = self.vector_store.query(query, n_results=n_context_chunks)
        
        # Handle both list of strings and list of dicts
        if context_results and isinstance(context_results[0], dict):
            context = "\n\n".join([r['document'] for r in context_results])
        else:
            context = "\n\n".join(context_results)
        
        # Build prompt with context using centralized template
        prompt = RAG_QUERY_WITH_CONTEXT.format(context=context, query=query)
        
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
            results = self.vector_store.query(q, n_results=3)
            
            # Handle both formats
            if results and isinstance(results[0], dict):
                all_context.extend([r['document'] for r in results])
            else:
                all_context.extend(results)
        
        # Deduplicate and join
        unique_context = list(dict.fromkeys(all_context))
        return "\n\n".join(unique_context[:10])  # Top 10 chunks
    
    def generate_search_queries(self, query_type: str, additional_criteria: str = "") -> List[str]:
        """Generate search queries for customer/partner discovery."""
        
        company_context = self.get_company_profile()
        
        # Use centralized prompt template
        prompt = RAG_GENERATE_SEARCH_QUERIES.format(
            company_context=company_context,
            query_type=query_type,
            additional_criteria=additional_criteria or "None"
        )

        response = self.llm.generate_json_with_trace(
            prompt,
            prompt_name="RAG_GENERATE_SEARCH_QUERIES",
            input_vars={"query_type": query_type, "additional_criteria": additional_criteria}
        )
        return response.get("queries", [])

