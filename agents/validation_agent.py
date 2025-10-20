"""Validation Agent - Ensures data quality."""
from typing import List, Dict, Tuple
import re


def safe_print(msg):
    """Print with error handling."""
    try:
        print(msg)
    except:
        pass


class ValidationAgent:
    """Agent that validates and filters results."""
    
    def __init__(self, min_score: int = 40):
        """Initialize validation agent."""
        self.min_score = min_score
    
    def validate_company(self, company: Dict) -> Tuple[bool, str]:
        """Validate a single company entry."""
        
        # Check required fields
        required = ['company_name', 'website_url', 'fit_score', 'rationale', 'category']
        for field in required:
            if not company.get(field):
                return False, f"Missing {field}"
        
        # Check score threshold
        if company['fit_score'] < self.min_score:
            return False, f"Score too low: {company['fit_score']}"
        
        # Validate URL format
        if not self._is_valid_url(company['website_url']):
            return False, "Invalid URL"
        
        # Check locations exist
        if not company.get('locations') or len(company['locations']) == 0:
            company['locations'] = ['Location not specified']
        
        # Validate size
        if company.get('estimated_size') not in ['Small', 'Medium', 'Large']:
            company['estimated_size'] = 'Medium'
        
        return True, "Valid"
    
    def validate_and_filter(self, companies: List[Dict], top_n: int = 10) -> List[Dict]:
        """Validate and return top N companies."""
        safe_print(f"\n✅ Validating {len(companies)} companies...")
        
        valid_companies = []
        
        for company in companies:
            is_valid, reason = self.validate_company(company)
            
            if is_valid:
                valid_companies.append(company)
            else:
                safe_print(f"  ✗ {company.get('company_name', 'Unknown')}: {reason}")
        
        safe_print(f"✓ {len(valid_companies)} companies passed validation")
        
        # Return top N
        result = valid_companies[:top_n]
        safe_print(f"✓ Returning top {len(result)} companies")
        
        return result
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        if not url:
            return False
        
        # Basic URL pattern
        pattern = r'^https?://[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,}'
        return bool(re.match(pattern, url))
    
    def deduplicate(self, companies: List[Dict]) -> List[Dict]:
        """Remove duplicate companies based on name similarity and URL."""
        seen_urls = set()
        seen_names = {}
        unique = []
        
        for company in companies:
            # Normalize URL for comparison
            url = self._normalize_url(company.get('website_url', ''))
            
            # Normalize name for comparison
            name = self._normalize_name(company.get('company_name', ''))
            
            # Check if URL already seen
            if url and url in seen_urls:
                safe_print(f"  ℹ️  Duplicate URL: {company['company_name']}")
                continue
            
            # Check if similar name already seen
            is_duplicate = False
            for seen_name in seen_names.keys():
                if self._names_are_similar(name, seen_name):
                    safe_print(f"  ℹ️  Similar name: {company['company_name']} ≈ {seen_names[seen_name]}")
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                if url:
                    seen_urls.add(url)
                seen_names[name] = company['company_name']
                unique.append(company)
        
        if len(unique) < len(companies):
            safe_print(f"  ℹ️  Removed {len(companies) - len(unique)} duplicates")
        
        return unique
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL for comparison."""
        if not url:
            return ''
        # Remove protocol, www, trailing slash
        url = url.lower()
        url = url.replace('https://', '').replace('http://', '')
        url = url.replace('www.', '')
        url = url.rstrip('/')
        return url
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize company name for comparison."""
        if not name:
            return ''
        # Lowercase, remove common suffixes, remove spaces/punctuation
        name = name.lower()
        # Remove common company suffixes
        suffixes = [' inc', ' inc.', ' corp', ' corp.', ' corporation', 
                   ' llc', ' ltd', ' ltd.', ' limited', ' co', ' co.', 
                   ' company', ' group', ' technologies', ' tech']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        # Remove all non-alphanumeric
        name = ''.join(c for c in name if c.isalnum())
        return name
    
    @staticmethod
    def _names_are_similar(name1: str, name2: str) -> bool:
        """Check if two normalized names are similar."""
        if not name1 or not name2:
            return False
        
        # Exact match after normalization
        if name1 == name2:
            return True
        
        # One is substring of the other (e.g., "tekion" in "tekioncorp")
        if name1 in name2 or name2 in name1:
            return True
        
        # Calculate similarity ratio (simple approach)
        # If names are very similar (>80% overlap)
        shorter = min(len(name1), len(name2))
        longer = max(len(name1), len(name2))
        
        if shorter == 0:
            return False
        
        # Count matching characters in order
        matches = sum(1 for i in range(shorter) if i < len(name1) and i < len(name2) and name1[i] == name2[i])
        similarity = matches / longer
        
        return similarity > 0.8
