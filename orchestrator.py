"""Orchestrator - Coordinates all agents."""
from typing import List, Dict
from agents.research_agent import ResearchAgent
from agents.enrichment_agent import EnrichmentAgent
from agents.scoring_agent import ScoringAgent
from agents.validation_agent import ValidationAgent
from utils.llm_client import LLMClient
from utils.rag import RAGSystem


def safe_print(msg):
    """Print with error handling."""
    try:
        print(msg)
    except:
        pass


class CompanyDiscoveryOrchestrator:
    """Orchestrates the multi-agent company discovery workflow."""
    
    def __init__(self, rag_system: RAGSystem):
        """Initialize orchestrator with all agents."""
        self.rag = rag_system
        
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.enrichment_agent = EnrichmentAgent(rag_system.llm)
        self.validation_agent = ValidationAgent(min_score=20)  # Very inclusive to ensure enough results
        
        # Get company context for scoring
        self.company_context = rag_system.get_company_profile()
        self.scoring_agent = ScoringAgent(rag_system.llm, self.company_context)
    
    def discover(self, 
                query_type: str,
                additional_criteria: str = "",
                top_n: int = 10) -> List[Dict]:
        """Run full discovery workflow."""
        
        safe_print(f"\n{'='*60}")
        safe_print(f"🚀 Starting {query_type.upper()} Discovery")
        safe_print(f"{'='*60}\n")
        
        # Step 1: Generate search queries using RAG
        safe_print("📝 Step 1: Generating search queries...")
        search_queries = self.rag.generate_search_queries(query_type, additional_criteria)
        
        safe_print(f"✓ Generated {len(search_queries)} queries:")
        for i, q in enumerate(search_queries, 1):
            safe_print(f"  {i}. {q}")
        
        # Step 2: Research - Find companies
        safe_print(f"\n{'='*60}")
        safe_print("🔍 Step 2: Researching companies...")
        safe_print(f"{'='*60}")
        
        # Increase search results significantly to account for filtering
        # Search for 2x the requested amount per query to ensure enough after filtering
        max_per_query = max(5, top_n)  # At least 10 per query
        
        search_results = self.research_agent.discover_companies(
            search_queries, 
            max_per_query=max_per_query
        )
        
        if not search_results:
            safe_print("❌ No results found")
            return []
        
        # Step 3: Enrichment - Extract company data
        safe_print(f"\n{'='*60}")
        safe_print("🔬 Step 3: Enriching company data...")
        safe_print(f"{'='*60}")
        enriched_companies = self.enrichment_agent.enrich_companies(
            search_results, 
            additional_criteria
        )
        
        if not enriched_companies:
            safe_print("❌ No companies extracted")
            return []
        
        # Filter by criteria match
        matching_companies = [c for c in enriched_companies if c.get('criteria_match', True)]
        filtered_companies = [c for c in enriched_companies if not c.get('criteria_match', True)]
        
        if filtered_companies:
            safe_print(f"\n⚠️  Filtered out {len(filtered_companies)} companies due to criteria:")
            for company in filtered_companies[:5]:  # Show first 5
                safe_print(f"  - {company['company_name']}: {company.get('match_reason', 'N/A')}")
            if len(filtered_companies) > 5:
                safe_print(f"  ... and {len(filtered_companies) - 5} more")
        
        if not matching_companies:
            safe_print("❌ No companies match the criteria")
            return []
        
        safe_print(f"✓ {len(matching_companies)} companies match criteria")
        
        # Deduplicate
        matching_companies = self.validation_agent.deduplicate(matching_companies)
        
        # Step 4: Scoring - Rank by fit
        safe_print(f"\n{'='*60}")
        safe_print("🎯 Step 4: Scoring and ranking...")
        safe_print(f"{'='*60}")
        category = "Customer" if query_type == "customer" else "Partner"
        scored_companies = self.scoring_agent.score_companies(
            matching_companies, 
            category
        )
        
        # Step 5: Validation - Filter and return top N
        safe_print(f"\n{'='*60}")
        safe_print("✅ Step 5: Validating results...")
        safe_print(f"{'='*60}")
        final_results = self.validation_agent.validate_and_filter(
            scored_companies, 
            top_n=top_n
        )
        
        # Attach filtered companies for UI display
        if filtered_companies and final_results:
            final_results[0]['_filtered_companies'] = filtered_companies
        
        safe_print(f"\n{'='*60}")
        safe_print(f"✅ Discovery Complete: {len(final_results)} companies")
        safe_print(f"{'='*60}\n")
        
        return final_results
    
    def format_results(self, companies: List[Dict]) -> str:
        """Format results for display."""
        output = []
        
        for i, company in enumerate(companies, 1):
            output.append(f"\n{i}. {company['company_name']}")
            output.append(f"   Website: {company['website_url']}")
            output.append(f"   Locations: {', '.join(company.get('locations', ['N/A']))}")
            output.append(f"   Size: {company['estimated_size']}")
            output.append(f"   Fit Score: {company['fit_score']}/100")
            output.append(f"   Category: {company['category']}")
            output.append(f"   Rationale: {company['rationale']}")
        
        return '\n'.join(output)
