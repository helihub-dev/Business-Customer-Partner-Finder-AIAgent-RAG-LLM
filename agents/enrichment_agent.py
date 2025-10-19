"""Enrichment Agent - Extracts company data from search results."""
from typing import Dict, Optional
import re
from urllib.parse import urlparse


class EnrichmentAgent:
    """Agent that enriches company data from search results."""
    
    def __init__(self, llm_client):
        """Initialize enrichment agent."""
        self.llm = llm_client
    
    def extract_company_info(self, search_result: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Extract structured company info from search result."""
        
        prompt = f"""Extract company information from this search result:

Title: {search_result['title']}
URL: {search_result['url']}
Content: {search_result['content']}

Extract and return JSON with:
- company_name: Official company name (or null if not a company)
- website_url: Main company website (not LinkedIn/Crunchbase)
- locations: Array of cities/regions mentioned
- size_indicators: Array of size clues (employee count, revenue, "enterprise", "startup", etc)
- business_description: 1-sentence what they do

Return ONLY valid JSON. If this is not about a real company, return {{"company_name": null}}"""

        try:
            result = self.llm.generate_json(prompt)
            
            # Skip if not a company
            if not result.get('company_name'):
                return None
            
            # Clean up website URL
            if result.get('website_url'):
                result['website_url'] = self._clean_url(result['website_url'])
            else:
                result['website_url'] = self._extract_domain(search_result['url'])
            
            return result
        except Exception as e:
            print(f"  ⚠️  Extraction error: {e}")
            return None
    
    def enrich_companies(self, search_results: list) -> list:
        """Enrich all search results."""
        enriched = []
        
        print(f"\n🔬 Enriching {len(search_results)} results...")
        
        for i, result in enumerate(search_results, 1):
            print(f"  [{i}/{len(search_results)}] Processing...")
            
            company_info = self.extract_company_info(result)
            if company_info:
                enriched.append(company_info)
                print(f"    ✓ {company_info['company_name']}")
            else:
                print(f"    ✗ Skipped (not a company)")
        
        print(f"\n✓ Enriched {len(enriched)} companies")
        return enriched
    
    @staticmethod
    def _clean_url(url: str) -> str:
        """Clean and normalize URL."""
        url = url.strip().lower()
        if not url.startswith('http'):
            url = 'https://' + url
        return url
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www.
            domain = re.sub(r'^www\.', '', domain)
            return f"https://{domain}"
        except:
            return url
