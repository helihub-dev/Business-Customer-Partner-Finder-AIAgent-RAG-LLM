"""Scoring Agent - Ranks companies by fit score."""
from typing import Dict
from prompts.prompts import (
    SCORING_EVALUATE_COMPANY,
    SCORING_CRITERIA_CUSTOMER,
    SCORING_CRITERIA_PARTNER
)


def safe_print(msg):
    """Print with error handling."""
    try:
        print(msg)
    except:
        pass


class ScoringAgent:
    """Agent that scores and ranks companies."""
    
    def __init__(self, llm_client, company_context: str):
        """Initialize scoring agent."""
        self.llm = llm_client
        self.company_context = company_context
    
    def score_company(self, 
                     company_info: Dict, 
                     category: str) -> Dict:
        """Score a single company."""
        
        criteria = self._get_criteria(category)
        
        # Safely handle locations and size_indicators
        locations = company_info.get('locations', [])
        if not isinstance(locations, list):
            locations = [str(locations)] if locations else []
        
        size_indicators = company_info.get('size_indicators', [])
        if not isinstance(size_indicators, list):
            size_indicators = [str(size_indicators)] if size_indicators else []
        
        # Use centralized prompt template
        prompt = SCORING_EVALUATE_COMPANY.format(
            company_context=self.company_context,
            company_name=company_info['company_name'],
            website_url=company_info['website_url'],
            locations=', '.join(locations),
            size_indicators=', '.join(size_indicators),
            business_description=company_info.get('business_description', 'N/A'),
            category=category,
            criteria=criteria
        )

        try:
            result = self.llm.generate_json_with_trace(
                prompt,
                prompt_name="SCORING_EVALUATE_COMPANY",
                input_vars={
                    "company_name": company_info['company_name'],
                    "category": category
                }
            )
            
            # Merge with original company info
            return {
                **company_info,
                'fit_score': result.get('fit_score', 0),
                'estimated_size': result.get('estimated_size', 'Medium'),
                'rationale': result.get('rationale', ''),
                'category': category
            }
        except Exception as e:
            safe_print(f"  ⚠️  Scoring error: {e}")
            return {
                **company_info,
                'fit_score': 0,
                'estimated_size': 'Medium',
                'rationale': 'Error during scoring',
                'category': category
            }
    
    def score_companies(self, companies: list, category: str, progress_callback=None) -> list:
        """Score all companies."""
        safe_print(f"\n🎯 Scoring {len(companies)} companies as {category}s...")
        
        scored = []
        for i, company in enumerate(companies, 1):
            safe_print(f"  [{i}/{len(companies)}] {company['company_name']}")
            
            if progress_callback:
                progress_callback(i, len(companies), company['company_name'])
            
            result = self.score_company(company, category)
            scored.append(result)
            safe_print(f"    Score: {result['fit_score']}/100")
        
        # Sort by score
        scored.sort(key=lambda x: x['fit_score'], reverse=True)
        
        safe_print(f"\n✓ Scored and ranked {len(scored)} companies")
        return scored
    
    @staticmethod
    def _get_criteria(category: str) -> str:
        """Get evaluation criteria for category."""
        if category == "Customer":
            return SCORING_CRITERIA_CUSTOMER
        else:  # Partner
            return SCORING_CRITERIA_PARTNER
