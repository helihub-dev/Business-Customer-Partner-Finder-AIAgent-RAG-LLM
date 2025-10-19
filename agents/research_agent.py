"""Research Agent - Discovers companies using web search."""
import os
from typing import List, Dict
from tavily import Client as TavilyClient


class ResearchAgent:
    """Agent that discovers companies using Tavily search."""
    
    def __init__(self):
        """Initialize research agent."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment")
        self.client = TavilyClient(api_key=api_key)
    
    def search_companies(self, 
                        query: str, 
                        max_results: int = 5) -> List[Dict[str, str]]:
        """Search for companies using Tavily."""
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_domains=["linkedin.com", "crunchbase.com", "bloomberg.com"],
                exclude_domains=[]
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def discover_companies(self, 
                          search_queries: List[str], 
                          max_per_query: int = 5) -> List[Dict[str, str]]:
        """Run multiple searches and aggregate results."""
        all_results = []
        seen_urls = set()
        
        for query in search_queries:
            print(f"🔍 Searching: {query}")
            results = self.search_companies(query, max_results=max_per_query)
            
            for result in results:
                url = result['url']
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)
            
            print(f"  ✓ Found {len(results)} results")
        
        print(f"\n📊 Total unique results: {len(all_results)}")
        return all_results
