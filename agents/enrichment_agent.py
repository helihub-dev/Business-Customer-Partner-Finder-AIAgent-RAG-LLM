"""Enrichment Agent - Extracts company data from search results."""
from typing import Dict, Optional, List
import re
from urllib.parse import urlparse
from prompts.prompts import ENRICHMENT_EXTRACT_COMPANY_INFO


def safe_print(msg):
    """Print with error handling for broken pipes."""
    try:
        print(msg)
    except:
        pass


class EnrichmentAgent:
    """Agent that enriches company data from search results."""
    
    def __init__(self, llm_client):
        """Initialize enrichment agent."""
        self.llm = llm_client
    
    def extract_company_info(self, search_result: Dict[str, str], additional_criteria: str = "") -> Optional[Dict[str, str]]:
        """Extract structured company info from search result."""
        
        # Use centralized prompt template
        prompt = ENRICHMENT_EXTRACT_COMPANY_INFO.format(
            title=search_result['title'],
            url=search_result['url'],
            content=search_result['content'],
            additional_criteria=additional_criteria or "None"
        )

        try:
            result = self.llm.generate_json_with_trace(
                prompt,
                prompt_name="ENRICHMENT_EXTRACT_COMPANY_INFO",
                input_vars={
                    "title": search_result['title'][:50],
                    "url": search_result['url']
                }
            )
            
            # Skip if not a company
            if not result.get('company_name'):
                return None
            
            # Ensure criteria_match fields exist (backward compatibility)
            if 'criteria_match' not in result:
                result['criteria_match'] = True
            if 'match_reason' not in result:
                result['match_reason'] = "No criteria specified"
            
            # Clean up website URL - prioritize actual company website
            result['website_url'] = self._get_company_website(
                result.get('website_url'),
                search_result['url'],
                search_result['content']
            )
            
            # Improve location extraction
            result['locations'] = self._extract_locations(
                result.get('locations', []),
                search_result['content']
            )
            
            return result
        except Exception as e:
            safe_print(f"  ⚠️  Extraction error: {e}")
            return None
    
    def enrich_companies(self, search_results: list, additional_criteria: str = "", progress_callback=None) -> list:
        """Enrich all search results."""
        enriched = []
        
        safe_print(f"\n🔬 Enriching {len(search_results)} results...")
        
        for i, result in enumerate(search_results, 1):
            safe_print(f"  [{i}/{len(search_results)}] Processing...")
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i, len(search_results), result.get('title', 'Unknown'))
            
            company_info = self.extract_company_info(result, additional_criteria)
            if company_info:
                enriched.append(company_info)
                safe_print(f"    ✓ {company_info['company_name']}")
            else:
                safe_print(f"    ✗ Skipped (not a company)")
        
        safe_print(f"\n✓ Enriched {len(enriched)} companies")
        return enriched
    
    def _get_company_website(self, extracted_url: str, source_url: str, content: str) -> str:
        """Get actual company website, avoiding LinkedIn/Crunchbase."""
        
        # Check if extracted URL is valid and not a profile site
        if extracted_url and self._is_valid_company_url(extracted_url):
            return self._clean_url(extracted_url)
        
        # Try to extract from content
        website = self._extract_website_from_content(content)
        if website and self._is_valid_company_url(website):
            return self._clean_url(website)
        
        # Fallback to source URL if it's not a profile site
        if self._is_valid_company_url(source_url):
            return self._extract_domain(source_url)
        
        # Last resort - return cleaned source
        return self._extract_domain(source_url)
    
    def _is_valid_company_url(self, url: str) -> bool:
        """Check if URL is a real company website (not LinkedIn, etc)."""
        if not url:
            return False
        
        url_lower = url.lower()
        profile_sites = ['linkedin.com', 'crunchbase.com', 'bloomberg.com', 
                        'facebook.com', 'twitter.com', 'instagram.com']
        
        return not any(site in url_lower for site in profile_sites)
    
    def _extract_website_from_content(self, content: str) -> Optional[str]:
        """Extract company website from content text."""
        # Look for common patterns
        patterns = [
            r'(?:website|site|homepage):\s*(https?://[^\s]+)',
            r'(?:visit|see)\s+(?:us\s+at\s+)?(https?://[^\s]+)',
            r'(https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_company_url(match):
                    return match
        
        return None
    
    def _extract_locations(self, extracted_locations: List[str], content: str) -> List[str]:
        """Extract and improve location information."""
        locations = set()
        
        # Add extracted locations
        if extracted_locations:
            locations.update([loc for loc in extracted_locations if loc])
        
        # Extract from content using patterns
        location_patterns = [
            r'(?:based in|located in|headquarters in|hq in)\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2})?)',
            r'([A-Z][a-zA-Z\s]+,\s*(?:CA|TX|FL|NY|IL|OH|PA|MI|GA|NC|NJ|VA|WA|AZ|MA|TN|IN|MO|MD|WI|CO|MN|SC|AL|LA|KY|OR|OK|CT|UT|IA|NV|AR|MS|KS|NM|NE|WV|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY))',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, content)
            locations.update([m.strip() for m in matches if m])
        
        # Return list, or indicate no location if empty
        result = list(locations)[:5]  # Limit to 5 locations
        return result if result else ["Location not specified"]
    
    @staticmethod
    def _clean_url(url: str) -> str:
        """Clean and normalize URL."""
        url = url.strip()
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
            # Remove path
            domain = domain.split('/')[0]
            return f"https://{domain}"
        except:
            return url
