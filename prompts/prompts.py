"""
Centralized Prompt Library for AxleWave Discovery System
Version: 1.0
Last Updated: 2025-10-18

All prompts used across the system are defined here for:
- Easy maintenance and versioning
- Performance tracking and optimization
- Documentation and auditability
"""

# ============================================================================
# RAG SYSTEM PROMPTS
# ============================================================================

RAG_QUERY_WITH_CONTEXT = """Context about AxleWave Technologies:

{context}

Question: {query}

Answer based on the context provided:"""

RAG_GENERATE_SEARCH_QUERIES = """Based on this company profile:

{company_context}

Generate 3-5 specific web search queries to find potential {query_type}s.

Additional Criteria: {additional_criteria}

IMPORTANT: If additional criteria is provided (not "None"), INTEGRATE it into EVERY query.

Examples:
- If criteria is "Focus on California": Generate "California automotive dealerships", "California dealer groups", etc.
- If criteria is "Enterprise companies only": Generate "enterprise automotive software", "large dealership groups", etc.
- If criteria is "API integration partners": Generate "automotive API providers", "dealership software integrations", etc.

For CUSTOMERS: Find companies that would buy this product (dealerships, dealer groups, OEMs)
For PARTNERS: Find companies that would integrate/partner (payment processors, CRM vendors, analytics providers)

Return ONLY a JSON array of search query strings, no explanation:
{{"queries": ["query1", "query2", ...]}}"""


# ============================================================================
# ENRICHMENT AGENT PROMPTS
# ============================================================================

ENRICHMENT_EXTRACT_COMPANY_INFO = """Extract company information from this search result:

Title: {title}
URL: {url}
Content: {content}

Additional Criteria: {additional_criteria}

Extract and return JSON with:
- company_name: Official company name (or null if not a company)
- website_url: Main company website URL (IMPORTANT: Extract the actual company website, NOT linkedin.com, crunchbase.com, or other profile sites. Look for mentions like "visit us at", "website:", or domain names in the content)
- locations: Array of ONLY city/state/country names (e.g., ["San Francisco, CA", "Austin, TX"]). Extract ONLY geographic locations from phrases like "based in", "located in", "headquarters in". DO NOT include descriptions, features, or non-location text.
- size_indicators: Array of size clues (employee count, revenue, "enterprise", "startup", "Fortune 500", etc)
- business_description: 1-sentence what they do
- criteria_match: true/false - Does this company match the additional criteria? (If criteria is "None", return true)
- match_reason: Brief explanation (1 sentence) why it matches or doesn't match the criteria

IMPORTANT:
- For website_url: Find the ACTUAL company domain, not profile pages
- For locations: ONLY geographic names (cities, states, countries). NO descriptions, features, or other text
- For criteria_match: Carefully evaluate if company meets the specified criteria
- If you cannot find specific information, use null for that field

Examples of CORRECT locations:
- ["San Ramon, CA", "Pleasanton, CA"]
- ["California", "Texas"]
- ["United States"]

Examples of INCORRECT locations (DO NOT include):
- ["With its highly configurable integration and greater customer engagement capabilities, AR, San Ramon, CA"]
- ["Based in San Francisco with offices"]
- ["Headquarters: New York"]

Examples:
- Criteria "California only" + Company in Florida → criteria_match: false, match_reason: "Headquartered in Florida, not California"
- Criteria "luxury brands" + Company sells BMW/Mercedes → criteria_match: true, match_reason: "Specializes in luxury automotive brands"
- Criteria "None" → criteria_match: true, match_reason: "No specific criteria to validate"

Return ONLY valid JSON. If this is not about a real company, return {{"company_name": null}}"""


# ============================================================================
# SCORING AGENT PROMPTS
# ============================================================================

SCORING_EVALUATE_COMPANY = """You are evaluating companies for AxleWave Technologies.

AXLEWAVE CONTEXT:
{company_context}

COMPANY TO EVALUATE:
Name: {company_name}
Website: {website_url}
Locations: {locations}
Size Indicators: {size_indicators}
Description: {business_description}

EVALUATION CRITERIA ({category}):
{criteria}

Return JSON with:
- fit_score: 0-100 (how well they fit)
- estimated_size: "Small" | "Medium" | "Large"
- rationale: 2-3 sentences explaining the score
- category: "{category}"

Be realistic - not every company is a perfect fit."""

# Scoring criteria templates
SCORING_CRITERIA_CUSTOMER = """
- Automotive dealership or dealer group (HIGH priority)
- Multiple locations (5-200 rooftops ideal)
- North America based
- Mentions of legacy systems, modernization, digital transformation
- Size: Medium to Large preferred
"""

SCORING_CRITERIA_PARTNER = """
- Complementary technology (payments, CRM, analytics, lending)
- Automotive industry experience
- API/integration capabilities
- Not a direct competitor (not a DMS provider)
- Established presence in market
"""


# ============================================================================
# PROMPT METADATA (for tracking and optimization)
# ============================================================================

PROMPT_METADATA = {
    "RAG_QUERY_WITH_CONTEXT": {
        "version": "1.0",
        "purpose": "Query LLM with retrieved context from vector store",
        "input_vars": ["context", "query"],
        "expected_output": "Natural language answer",
        "avg_tokens": 500,
    },
    "RAG_GENERATE_SEARCH_QUERIES": {
        "version": "1.0",
        "purpose": "Generate targeted search queries for company discovery",
        "input_vars": ["company_context", "query_type"],
        "expected_output": "JSON array of search queries",
        "avg_tokens": 300,
    },
    "ENRICHMENT_EXTRACT_COMPANY_INFO": {
        "version": "1.0",
        "purpose": "Extract structured company data from search results",
        "input_vars": ["title", "url", "content"],
        "expected_output": "JSON with company fields or null",
        "avg_tokens": 400,
    },
    "SCORING_EVALUATE_COMPANY": {
        "version": "1.0",
        "purpose": "Score and rank companies by fit",
        "input_vars": ["company_context", "company_name", "website_url", "locations", 
                       "size_indicators", "business_description", "category", "criteria"],
        "expected_output": "JSON with fit_score, estimated_size, rationale",
        "avg_tokens": 600,
    },
}


def get_prompt(prompt_name: str) -> str:
    """
    Get a prompt by name.
    
    Args:
        prompt_name: Name of the prompt constant
        
    Returns:
        Prompt template string
    """
    return globals().get(prompt_name, "")


def get_prompt_metadata(prompt_name: str) -> dict:
    """
    Get metadata for a prompt.
    
    Args:
        prompt_name: Name of the prompt constant
        
    Returns:
        Dictionary with prompt metadata
    """
    return PROMPT_METADATA.get(prompt_name, {})
