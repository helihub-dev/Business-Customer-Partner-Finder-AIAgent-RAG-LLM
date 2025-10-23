# LLM Prompts Documentation

**Version:** 1.0  
**Last Updated:** October 23, 2025  
**System:** AxleWave Discovery - AI-Powered Multi-Agent System

---

## Table of Contents

1. [Overview](#overview)
2. [Prompt Architecture](#prompt-architecture)
3. [RAG System Prompts](#rag-system-prompts)
4. [Agent-Specific Prompts](#agent-specific-prompts)
5. [Search Engine Strings](#search-engine-strings)
6. [Prompt Design Principles](#prompt-design-principles)
7. [Performance Optimization](#performance-optimization)

---

## Overview

This document provides comprehensive documentation of all LLM prompts and search engine strings employed by the AxleWave Discovery system. The system uses a centralized prompt library (`prompts/prompts.py`) for maintainability, versioning, and performance tracking.

### Key Features

- **Centralized Management**: All prompts defined in single source file
- **Version Control**: Each prompt has metadata tracking version and purpose
- **Structured Outputs**: JSON-based responses for reliable parsing
- **Context Integration**: RAG-enhanced prompts with company knowledge
- **Criteria Validation**: Built-in filtering logic within prompts

---

## Prompt Architecture

### Design Pattern

```
User Query → RAG Context Retrieval → Prompt Template → LLM → Structured Output
```

### Prompt Components

1. **Context Section**: Retrieved from vector store (ChromaDB)
2. **Task Description**: Clear instruction on what to generate
3. **Input Variables**: Dynamic data (company info, search results)
4. **Output Format**: JSON schema specification
5. **Examples**: Few-shot learning where applicable
6. **Constraints**: Validation rules and criteria

---

## RAG System Prompts

### 1. RAG_QUERY_WITH_CONTEXT

**Purpose**: Query LLM with retrieved context from vector store

**Template**:
```
Context about AxleWave Technologies:

{context}

Question: {query}

Answer based on the context provided:
```

**Input Variables**:
- `context`: Retrieved document chunks from ChromaDB (5 chunks default)
- `query`: User's question about AxleWave

**Expected Output**: Natural language answer grounded in context

**Usage**: General Q&A about company, products, and capabilities

**Average Tokens**: ~500

**Example**:
```python
# Input
query = "What are the key features of DealerFlow Cloud?"
context = "DealerFlow Cloud is a comprehensive DMS platform..."

# Output
"DealerFlow Cloud offers inventory management, customer relationship 
management, service scheduling, and real-time analytics..."
```

---

### 2. RAG_GENERATE_SEARCH_QUERIES

**Purpose**: Generate targeted web search queries for company discovery

**Template**:
```
Based on this company profile:

{company_context}

Generate 3-5 specific web search queries to find potential {query_type}s.

Additional Criteria: {additional_criteria}

IMPORTANT: If additional criteria is provided (not "None"), INTEGRATE it 
into EVERY query.

Examples:
- If criteria is "Focus on California": Generate "California automotive 
  dealerships", "California dealer groups", etc.
- If criteria is "Enterprise companies only": Generate "enterprise automotive 
  software", "large dealership groups", etc.
- If criteria is "API integration partners": Generate "automotive API providers", 
  "dealership software integrations", etc.

For CUSTOMERS: Find companies that would buy this product (dealerships, 
dealer groups, OEMs)
For PARTNERS: Find companies that would integrate/partner (payment processors, 
CRM vendors, analytics providers)

Return ONLY a JSON array of search query strings, no explanation:
{"queries": ["query1", "query2", ...]}
```

**Input Variables**:
- `company_context`: Comprehensive profile from vector store (10 chunks)
- `query_type`: "Customer" or "Partner"
- `additional_criteria`: User-specified filters (location, size, technology)

**Expected Output**: JSON array of 3-5 search query strings

**Average Tokens**: ~300

**Key Design Elements**:
1. **Criteria Integration**: Forces LLM to incorporate user filters into every query
2. **Few-Shot Examples**: Shows how to integrate different criteria types
3. **Role Clarity**: Distinguishes between customer vs partner search intent
4. **Structured Output**: JSON format for reliable parsing

**Example Output**:
```json
{
  "queries": [
    "California automotive dealership groups DMS software",
    "Southern California car dealer management systems",
    "Los Angeles area dealership technology solutions",
    "San Francisco Bay Area automotive retail software",
    "California multi-location dealer groups"
  ]
}
```

---

## Agent-Specific Prompts

### 3. ENRICHMENT_EXTRACT_COMPANY_INFO

**Purpose**: Extract structured company data from search results with criteria validation

**Template**:
```
Extract company information from this search result:

Title: {title}
URL: {url}
Content: {content}

Additional Criteria: {additional_criteria}

Extract and return JSON with:
- company_name: Official company name (or null if not a company)
- website_url: Main company website URL (IMPORTANT: Extract the actual company 
  website, NOT linkedin.com, crunchbase.com, or other profile sites. Look for 
  mentions like "visit us at", "website:", or domain names in the content)
- locations: Array of ONLY city/state/country names (e.g., ["San Francisco, CA", 
  "Austin, TX"]). Extract ONLY geographic locations from phrases like "based in", 
  "located in", "headquarters in". DO NOT include descriptions, features, or 
  non-location text.
- size_indicators: Array of size clues (employee count, revenue, "enterprise", 
  "startup", "Fortune 500", etc)
- business_description: 1-sentence what they do
- criteria_match: true/false - Does this company match the additional criteria? 
  (If criteria is "None", return true)
- match_reason: Brief explanation (1 sentence) why it matches or doesn't match 
  the criteria

IMPORTANT:
- For website_url: Find the ACTUAL company domain, not profile pages
- For locations: ONLY geographic names (cities, states, countries). NO descriptions, 
  features, or other text
- For criteria_match: Carefully evaluate if company meets the specified criteria
- If you cannot find specific information, use null for that field

Examples of CORRECT locations:
- ["San Ramon, CA", "Pleasanton, CA"]
- ["California", "Texas"]
- ["United States"]

Examples of INCORRECT locations (DO NOT include):
- ["With its highly configurable integration and greater customer engagement 
   capabilities, AR, San Ramon, CA"]
- ["Based in San Francisco with offices"]
- ["Headquarters: New York"]

Examples:
- Criteria "California only" + Company in Florida → criteria_match: false, 
  match_reason: "Headquartered in Florida, not California"
- Criteria "luxury brands" + Company sells BMW/Mercedes → criteria_match: true, 
  match_reason: "Specializes in luxury automotive brands"
- Criteria "None" → criteria_match: true, match_reason: "No specific criteria 
  to validate"

Return ONLY valid JSON. If this is not about a real company, return 
{"company_name": null}
```

**Input Variables**:
- `title`: Search result title
- `url`: Source URL
- `content`: Search result content (up to 2000 chars)
- `additional_criteria`: User-specified validation rules

**Expected Output**: JSON with company fields or null

**Average Tokens**: ~400

**Key Design Elements**:
1. **Criteria Validation**: Integrated filtering during enrichment (no extra LLM calls)
2. **URL Cleaning**: Explicit instructions to avoid profile sites
3. **Location Extraction**: Strict rules to extract only geographic names
4. **Few-Shot Examples**: Shows correct vs incorrect location formats
5. **Null Handling**: Clear instructions for missing data

**Example Output**:
```json
{
  "company_name": "Sonic Automotive",
  "website_url": "https://sonicautomotive.com",
  "locations": ["Charlotte, NC", "Denver, CO"],
  "size_indicators": ["Fortune 500", "100+ dealerships", "publicly traded"],
  "business_description": "One of the largest automotive retailers in the US operating franchised dealerships",
  "criteria_match": true,
  "match_reason": "Large multi-location dealer group matching enterprise criteria"
}
```

---

### 4. SCORING_EVALUATE_COMPANY

**Purpose**: Score and rank companies by fit with AxleWave's ideal profile

**Template**:
```
You are evaluating companies for AxleWave Technologies.

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

Be realistic - not every company is a perfect fit.
```

**Input Variables**:
- `company_context`: AxleWave profile from RAG
- `company_name`, `website_url`, `locations`, `size_indicators`, `business_description`: Enriched company data
- `category`: "Customer" or "Partner"
- `criteria`: Category-specific evaluation rules

**Expected Output**: JSON with scoring details

**Average Tokens**: ~600

**Scoring Criteria - Customers**:
```
- Automotive dealership or dealer group (HIGH priority)
- Multiple locations (5-200 rooftops ideal)
- North America based
- Mentions of legacy systems, modernization, digital transformation
- Size: Medium to Large preferred
```

**Scoring Criteria - Partners**:
```
- Complementary technology (payments, CRM, analytics, lending)
- Automotive industry experience
- API/integration capabilities
- Not a direct competitor (not a DMS provider)
- Established presence in market
```

**Example Output**:
```json
{
  "fit_score": 85,
  "estimated_size": "Large",
  "rationale": "Sonic Automotive is an ideal customer with 100+ dealership locations across the US. As a Fortune 500 company, they have the scale and budget for enterprise DMS solutions. Their focus on digital transformation aligns perfectly with DealerFlow Cloud's modernization value proposition.",
  "category": "Customer"
}
```

---

## Search Engine Strings

### Tavily API Configuration

**Search Depth**: `advanced` (deeper crawling for better results)

**Domains**: 
- Include: None (open search)
- Exclude: None (allow all sources)

**Max Results per Query**: 20 (configurable in orchestrator)

### Query Generation Strategy

The system generates 3-5 targeted queries per discovery request, combining:

1. **Core Business Context**: "automotive dealership", "dealer management system"
2. **Geographic Filters**: "California", "Texas", "North America"
3. **Size Indicators**: "enterprise", "multi-location", "Fortune 500"
4. **Technology Focus**: "cloud software", "API integration", "payment processing"

### Example Query Sets

**Customer Discovery (No Criteria)**:
```
1. "automotive dealership groups North America DMS software"
2. "multi-location car dealers management systems"
3. "enterprise dealership technology solutions"
4. "automotive retail groups digital transformation"
5. "dealer groups modernization cloud software"
```

**Customer Discovery (California Focus)**:
```
1. "California automotive dealership groups"
2. "Southern California car dealer management"
3. "Bay Area dealership technology"
4. "Los Angeles automotive retail software"
5. "San Diego dealer groups DMS"
```

**Partner Discovery (Payment Focus)**:
```
1. "automotive payment processing integration"
2. "dealership payment gateway providers"
3. "car dealer payment solutions API"
4. "automotive finance payment technology"
5. "dealer payment processing partners"
```

---

## Prompt Design Principles

### 1. Clarity and Specificity

- **Clear Instructions**: Explicit task description
- **Structured Format**: JSON schema specification
- **Examples**: Few-shot learning for complex tasks
- **Constraints**: Validation rules stated upfront

### 2. Context Integration

- **RAG Enhancement**: All prompts leverage vector store context
- **Company Profile**: Consistent AxleWave context across agents
- **Dynamic Variables**: Template-based variable injection

### 3. Error Prevention

- **Null Handling**: Instructions for missing data
- **Format Validation**: JSON-only responses
- **Edge Cases**: Examples of incorrect outputs to avoid

### 4. Criteria Enforcement

- **Integrated Validation**: Criteria checking during enrichment
- **Match Reasoning**: Explanations for filter decisions
- **Flexible Logic**: Handles "None" criteria gracefully

### 5. Output Consistency

- **Structured JSON**: All agent outputs use JSON
- **Standard Fields**: Consistent naming across agents
- **Type Safety**: Explicit type specifications

---

## Prompt Metadata

Each prompt includes metadata for tracking:

```python
PROMPT_METADATA = {
    "PROMPT_NAME": {
        "version": "1.0",
        "purpose": "Description of what prompt does",
        "input_vars": ["var1", "var2"],
        "expected_output": "Output format description",
        "avg_tokens": 500
    }
}
```

**Usage**:
```python
from prompts.prompts import get_prompt, get_prompt_metadata

# Get prompt template
prompt = get_prompt("RAG_QUERY_WITH_CONTEXT")

# Get metadata
metadata = get_prompt_metadata("RAG_QUERY_WITH_CONTEXT")
print(f"Purpose: {metadata['purpose']}")
print(f"Avg tokens: {metadata['avg_tokens']}")
```


---

## References

- **Prompt Library**: `/prompts/prompts.py`
- **Enrichment Agent**: `/agents/enrichment_agent.py`
- **Scoring Agent**: `/agents/scoring_agent.py`
- **RAG System**: `/utils/rag.py`
- **Prompt Tracing**: See `PROMPT_TRACING.md`
