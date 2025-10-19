"""Validation Agent - Ensures data quality."""
from typing import List, Dict, Tuple
import re


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
        print(f"\n✅ Validating {len(companies)} companies...")
        
        valid_companies = []
        
        for company in companies:
            is_valid, reason = self.validate_company(company)
            
            if is_valid:
                valid_companies.append(company)
            else:
                print(f"  ✗ {company.get('company_name', 'Unknown')}: {reason}")
        
        print(f"✓ {len(valid_companies)} companies passed validation")
        
        # Return top N
        result = valid_companies[:top_n]
        print(f"✓ Returning top {len(result)} companies")
        
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
        """Remove duplicate companies."""
        seen = set()
        unique = []
        
        for company in companies:
            # Use company name as key (lowercase, no spaces)
            key = company['company_name'].lower().replace(' ', '')
            
            if key not in seen:
                seen.add(key)
                unique.append(company)
        
        if len(unique) < len(companies):
            print(f"  ℹ️  Removed {len(companies) - len(unique)} duplicates")
        
        return unique
