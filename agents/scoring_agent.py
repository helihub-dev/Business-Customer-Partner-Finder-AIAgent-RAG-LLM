"""Scoring Agent - Ranks companies by fit score."""
from typing import Dict


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
        
        prompt = f"""You are evaluating companies for AxleWave Technologies.

AXLEWAVE CONTEXT:
{self.company_context}

COMPANY TO EVALUATE:
Name: {company_info['company_name']}
Website: {company_info['website_url']}
Locations: {', '.join(company_info.get('locations', []))}
Size Indicators: {', '.join(company_info.get('size_indicators', []))}
Description: {company_info.get('business_description', 'N/A')}

EVALUATION CRITERIA ({category}):
{criteria}

Return JSON with:
- fit_score: 0-100 (how well they fit)
- estimated_size: "Small" | "Medium" | "Large"
- rationale: 2-3 sentences explaining the score
- category: "{category}"

Be realistic - not every company is a perfect fit."""

        try:
            result = self.llm.generate_json(prompt)
            
            # Merge with original company info
            return {
                **company_info,
                'fit_score': result.get('fit_score', 0),
                'estimated_size': result.get('estimated_size', 'Medium'),
                'rationale': result.get('rationale', ''),
                'category': category
            }
        except Exception as e:
            print(f"  ⚠️  Scoring error: {e}")
            return {
                **company_info,
                'fit_score': 0,
                'estimated_size': 'Medium',
                'rationale': 'Error during scoring',
                'category': category
            }
    
    def score_companies(self, companies: list, category: str) -> list:
        """Score all companies."""
        print(f"\n🎯 Scoring {len(companies)} companies as {category}s...")
        
        scored = []
        for i, company in enumerate(companies, 1):
            print(f"  [{i}/{len(companies)}] {company['company_name']}")
            result = self.score_company(company, category)
            scored.append(result)
            print(f"    Score: {result['fit_score']}/100")
        
        # Sort by score
        scored.sort(key=lambda x: x['fit_score'], reverse=True)
        
        print(f"\n✓ Scored and ranked {len(scored)} companies")
        return scored
    
    @staticmethod
    def _get_criteria(category: str) -> str:
        """Get evaluation criteria for category."""
        if category == "Customer":
            return """
- Automotive dealership or dealer group (HIGH priority)
- Multiple locations (5-200 rooftops ideal)
- North America based
- Mentions of legacy systems, modernization, digital transformation
- Size: Medium to Large preferred
"""
        else:  # Partner
            return """
- Complementary technology (payments, CRM, analytics, lending)
- Automotive industry experience
- API/integration capabilities
- Not a direct competitor (not a DMS provider)
- Established presence in market
"""
