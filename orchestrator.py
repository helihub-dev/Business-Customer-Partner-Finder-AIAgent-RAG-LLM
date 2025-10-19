"""Orchestrator - Coordinates all agents."""
from typing import List, Dict
from agents.research_agent import ResearchAgent
from agents.enrichment_agent import EnrichmentAgent
from agents.scoring_agent import ScoringAgent
from agents.validation_agent import ValidationAgent
from utils.llm_client import LLMClient
from utils.rag import RAGSystem


class CompanyDiscoveryOrchestrator:
    """Orchestrates the multi-agent company discovery workflow."""
    
    def __init__(self, rag_system: RAGSystem):
        """Initialize orchestrator with all agents."""
        self.rag = rag_system
        
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.enrichment_agent = EnrichmentAgent(rag_system.llm)
        self.validation_agent = ValidationAgent(min_score=40)
        
        # Get company context for scoring
        self.company_context = rag_system.get_company_profile()
        self.scoring_agent = ScoringAgent(rag_system.llm, self.company_context)
    
    def discover(self, 
                query_type: str,
                additional_criteria: str = "",
                top_n: int = 10) -> List[Dict]:
        """Run full discovery workflow."""
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting {query_type.upper()} Discovery")
        print(f"{'='*60}\n")
        
        # Step 1: Generate search queries using RAG
        print("📝 Step 1: Generating search queries...")
        search_queries = self.rag.generate_search_queries(query_type)
        
        if additional_criteria:
            search_queries.append(additional_criteria)
        
        print(f"✓ Generated {len(search_queries)} queries:")
        for i, q in enumerate(search_queries, 1):
            print(f"  {i}. {q}")
        
        # Step 2: Research - Find companies
        print(f"\n{'='*60}")
        print("🔍 Step 2: Researching companies...")
        print(f"{'='*60}")
        search_results = self.research_agent.discover_companies(
            search_queries, 
            max_per_query=5
        )
        
        if not search_results:
            print("❌ No results found")
            return []
        
        # Step 3: Enrichment - Extract company data
        print(f"\n{'='*60}")
        print("🔬 Step 3: Enriching company data...")
        print(f"{'='*60}")
        enriched_companies = self.enrichment_agent.enrich_companies(search_results)
        
        if not enriched_companies:
            print("❌ No companies extracted")
            return []
        
        # Deduplicate
        enriched_companies = self.validation_agent.deduplicate(enriched_companies)
        
        # Step 4: Scoring - Rank by fit
        print(f"\n{'='*60}")
        print("🎯 Step 4: Scoring and ranking...")
        print(f"{'='*60}")
        category = "Customer" if query_type == "customer" else "Partner"
        scored_companies = self.scoring_agent.score_companies(
            enriched_companies, 
            category
        )
        
        # Step 5: Validation - Filter and return top N
        print(f"\n{'='*60}")
        print("✅ Step 5: Validating results...")
        print(f"{'='*60}")
        final_results = self.validation_agent.validate_and_filter(
            scored_companies, 
            top_n=top_n
        )
        
        print(f"\n{'='*60}")
        print(f"✅ Discovery Complete: {len(final_results)} companies")
        print(f"{'='*60}\n")
        
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
