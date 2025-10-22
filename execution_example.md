# Complete Execution Example - Step by Step

## User Request
```
Discovery Type: "Potential Customers"
Additional Criteria: "Focus on Company located only in California"
Top N: 10
```

---

## Step 1: RAG System - Generate Search Queries

### Input
```json
{
  "query_type": "customer",
  "additional_criteria": "Focus on Company located only in California",
  "context": "AxleWave provides DealerFlow Cloud - a modern retail OS for automotive dealerships..."
}
```

### Prompt (Simplified)
```
Based on AxleWave's ideal customer profile and additional criteria, 
generate 3-5 web search queries.

Context: AxleWave provides DealerFlow Cloud - a modern retail operating system
for automotive dealerships that modernizes DMS, CRM, inventory management, and operations.

Ideal Customer: Automotive dealership groups with 10-500 locations seeking
to modernize their technology stack.

Additional Criteria: Focus on Company located only in California

Generate targeted search queries that will find these companies.
Integrate the criteria directly into each query.
```

### Output
```json
{
  "search_queries": [
    "California automotive dealership groups",
    "California franchise auto dealers modernizing technology",
    "California multi-rooftop car dealership management",
    "California automotive dealer service directors",
    "California OEM certified automotive dealerships"
  ]
}
```

**Metrics:**
- Latency: 1.92s
- Tokens: 1,938
- Cost: $0.29-$1.16 (OpenAI gpt-4o-mini: $0.15-$0.60/1M tokens)

---

## Step 2: Research Agent - Web Search (Tavily API)

### Input (Query 1)
```
"California automotive dealership groups"
```

### Tavily API Call (Not Traced)
```python
tavily.search(
    query="California automotive dealership groups",
    max_results=20  # Increased from 5 to ensure enough results
)
```

### Output (Sample - 5 of 20 results)
```json
[
  {
    "title": "Lithia Motors - California Dealerships",
    "url": "https://www.lithia.com/california",
    "content": "Lithia Motors operates 50+ automotive dealerships across California...",
    "score": 0.92
  },
  {
    "title": "Penske Automotive Group - West Coast",
    "url": "https://www.penskeautomotive.com/california",
    "content": "Penske Automotive Group operates 25+ dealerships in California...",
    "score": 0.89
  },
  {
    "title": "AutoNation California",
    "url": "https://www.autonation.com/california",
    "content": "AutoNation operates 35 dealerships throughout California...",
    "score": 0.87
  },
  {
    "title": "Keyes Automotive Group",
    "url": "https://www.keyesauto.com",
    "content": "Family-owned Keyes Automotive operates 12 dealerships in Southern California...",
    "score": 0.83
  },
  {
    "title": "Modesto Toyota",
    "url": "https://www.modestotoyota.com",
    "content": "Modesto Toyota is a leading dealership in Central California...",
    "score": 0.81
  }
]
```

**Metrics (per query):**
- Latency: ~2-3s
- Cost: ~$0.002 (Tavily API, not LLM)

---

## Step 3: Enrichment Agent - Extract Company Data + Validate Criteria

### Input (Company 1: Lithia Motors)
```json
{
  "company_name": "Lithia Motors",
  "url": "https://www.lithia.com/california",
  "search_content": "Lithia Motors operates 50+ automotive dealerships across California...",
  "additional_criteria": "Focus on Company located only in California"
}
```

### Prompt (Simplified)
```
Extract structured information from this search result:

Title: Lithia Motors - California Dealerships
URL: https://www.lithia.com/california
Content: Lithia Motors operates 50+ automotive dealerships across California...

Additional User Criteria: Focus on Company located only in California

Extract the following information in JSON format:

1. company_name: The official company name
2. website_url: The actual company website (NOT profile sites like LinkedIn/Crunchbase)
3. locations: List of geographic locations (ONLY city/state, e.g., "Los Angeles, CA")
4. category: Type of business (e.g., "Automotive Dealership Group")
5. estimated_size: Company size (number of locations, employees, or revenue estimate)
6. business_description: Brief description of what they do
7. criteria_match: Boolean - does this company match the additional criteria?
8. match_reason: Explanation of why it matches or doesn't match

Instructions:
- For website_url: Extract the root domain (e.g., linkedin.com/company/xyz → find actual company site)
- For locations: Extract ONLY geographic names from the content
- For criteria_match: Evaluate if the company meets "Focus on Company located only in California"
- Provide clear reasoning in match_reason
```

### Output (Matching Company)
```json
{
  "company_name": "Lithia Motors",
  "website_url": "https://www.lithia.com",
  "category": "Automotive Dealership Group",
  "estimated_size": "50+ locations, 5000+ employees",
  "locations": ["California", "Los Angeles", "San Diego", "San Francisco"],
  "business_description": "Multi-location automotive dealership group operating across California",
  "criteria_match": true,
  "match_reason": "Operates 50+ dealerships in California, meets location criteria"
}
```

### Output (Non-Matching Company - Van Horn Automotive)
```json
{
  "company_name": "Van Horn Automotive Group",
  "website_url": "https://www.vanhornautomotive.com",
  "category": "Automotive Dealership Group",
  "estimated_size": "15+ locations",
  "locations": ["Wisconsin", "Iowa"],
  "business_description": "Multi-location automotive dealership group in Midwest",
  "criteria_match": false,
  "match_reason": "Headquartered in Wisconsin, not California"
}
```

**Metrics:**
- Latency: ~1.85s per company
- Tokens: ~600 per company
- Cost: ~$0.09-$0.36 per company (OpenAI gpt-4o-mini)
- Total for 100 companies: 185s, 60,000 tokens, $9.00-$36.00

**Processing Details:**
1. LLM extracts structured data from each search result
2. Validates company against user criteria during extraction
3. If LLM fails to extract location, regex patterns search content for:
   - "based in [City, State]"
   - "located in [City, State]"
   - "headquarters in [City, State]"
4. Returns structured JSON with all fields
5. Some results may not be companies and return null (filtered out)

**This repeats for all 100 search results.**

---

## Step 3.5: Criteria Filtering

### Input
```json
[
  {"company_name": "Lithia Motors", "criteria_match": true, ...},
  {"company_name": "Penske Automotive", "criteria_match": true, ...},
  {"company_name": "Van Horn Automotive", "criteria_match": false, ...},
  {"company_name": "Tuttle-Click", "criteria_match": false, ...},
  // ... 96 more companies
]
```

### Processing
```python
# Separate matching and non-matching
matching = [c for c in enriched if c['criteria_match'] == true]
filtered_out = [c for c in enriched if c['criteria_match'] == false]

print(f"✓ {len(matching)} companies match criteria")
print(f"⚠️ Filtered out {len(filtered_out)} companies:")
for company in filtered_out[:5]:
    print(f"  - {company['company_name']}: {company['match_reason']}")
```

### Output
```
✓ 45 companies match criteria
⚠️ Filtered out 55 companies due to criteria:
  - Van Horn Automotive: Headquartered in Wisconsin, not California
  - Tuttle-Click: Based in Arizona, not California
  - AutoNation: Headquartered in Florida (has CA locations but not CA-only)
  - Dealertrack: National software company, not California-specific
  - Hendrick Automotive: Based in North Carolina
  ... and 50 more
```

**Metrics:**
- Latency: <0.1s (instant, no LLM calls)
- Tokens: 0
- Cost: $0

**Processing:**
1. Separate companies by `criteria_match` field
2. Keep only companies where `criteria_match == true`
3. Store filtered companies with reasons for transparency
4. Pass matching companies to next step

---

## Step 4: Deduplication

### Input (Matching Companies)
```json
[
  {"company_name": "Lithia Motors", "website_url": "https://www.lithia.com", ...},
  {"company_name": "Lithia California", "website_url": "https://www.lithia.com/california", ...},
  {"company_name": "Penske Automotive", "website_url": "https://www.penskeautomotive.com", ...},
  {"company_name": "Penske Auto Group", "website_url": "https://penskeautomotive.com", ...},
  // ... 41 more companies
]
```

### Processing (No LLM)
```python
# Deduplicate by URL
def normalize_url(url):
    # Remove protocol, www, trailing slashes
    url = url.lower().replace('https://', '').replace('http://', '')
    url = url.replace('www.', '').rstrip('/')
    return url.split('/')[0]  # Keep only domain

# Deduplicate by company name similarity
def normalize_name(name):
    name = name.lower()
    # Remove common suffixes
    for suffix in [' inc', ' corp', ' llc', ' ltd', ' limited', ' group']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    # Remove non-alphanumeric
    name = ''.join(c for c in name if c.isalnum())
    return name

def are_similar(name1, name2):
    # Check if names are >80% similar
    return name1 in name2 or name2 in name1 or similarity_ratio(name1, name2) > 0.8

# Remove duplicates
seen_urls = set()
seen_names = {}
unique = []

for company in matching_companies:
    url = normalize_url(company['website_url'])
    name = normalize_name(company['company_name'])
    
    if url in seen_urls:
        continue  # Duplicate URL
    
    if any(are_similar(name, seen) for seen in seen_names.keys()):
        continue  # Similar name
    
    seen_urls.add(url)
    seen_names[name] = company['company_name']
    unique.append(company)
```

### Output
```
Deduplication Results:
  ℹ️ Duplicate URL: Lithia California (same as Lithia Motors)
  ℹ️ Similar name: Penske Auto Group ≈ Penske Automotive
  ℹ️ Removed 8 duplicates
✓ 37 unique companies remaining
```

**Metrics:**
- Latency: <0.1s (instant)
- Tokens: 0 (no LLM)
- Cost: $0

---

## Step 5: Scoring Agent - Evaluate & Rank

### Input (Lithia Motors)
```json
{
  "company_data": {
    "company_name": "Lithia Motors",
    "website_url": "https://www.lithia.com",
    "category": "Automotive Dealership Group",
    "estimated_size": "50+ locations, 5000+ employees",
    "locations": ["California", "Los Angeles", "San Diego", "San Francisco"],
    "business_description": "Multi-location automotive dealership group",
    "criteria_match": true
  },
  "rag_context": "AxleWave's DealerFlow Cloud ideal customer profile..."
}
```

### Prompt (Simplified)
```
Evaluate this company's fit for AxleWave's DealerFlow Cloud platform.

Company Information:
- Name: Lithia Motors
- Category: Automotive Dealership Group
- Size: 50+ locations, 5000+ employees
- Locations: California (Los Angeles, San Diego, San Francisco)
- Description: Multi-location automotive dealership group

AxleWave Context (from RAG):
- DealerFlow Cloud is a modern retail OS for automotive dealerships
- Target customers: Dealership groups with 10-500 locations
- Key features: Modern DMS, CRM, inventory management, operational efficiency
- Benefits: Streamlines operations, reduces costs, improves customer experience

Evaluation Criteria for CUSTOMERS:
1. Industry alignment (automotive dealerships)
2. Company size (ideal: 10-500 locations)
3. Technology needs (DMS/CRM modernization)
4. Growth stage (established but seeking to modernize)
5. Geographic fit (if specified in criteria)

Provide:
- fit_score: Integer 0-100 (how well they match)
- estimated_size: Small/Medium/Large (based on locations/employees)
- rationale: 2-3 sentence explanation of the score

Score them objectively based on fit with ideal customer profile.
```

### Output
```json
{
  "company_name": "Lithia Motors",
  "fit_score": 92,
  "estimated_size": "Large",
  "category": "Customer",
  "rationale": "Excellent fit for DealerFlow Cloud. Lithia Motors operates 50+ dealerships across California, placing them squarely in AxleWave's target range of 10-500 locations. As a large multi-location dealership group, they face complex inventory management and operational efficiency challenges that DealerFlow Cloud addresses. Strong potential for enterprise-level deployment."
}
```

**Metrics:**
- Latency: ~1.52s per company
- Tokens: ~456 per company
- Cost: ~$0.068-$0.274 per company (OpenAI gpt-4o-mini)
- Total for 37 companies: 56s, 16,872 tokens, $2.53-$10.12

**Processing:**
1. RAG system retrieves relevant AxleWave context
2. LLM evaluates company against ideal customer profile
3. Scores based on industry, size, needs, and criteria
4. Generates rationale explaining the score
5. All 37 companies are scored and ranked

**This repeats for all 37 unique, matching companies.**

---

## Step 6: Validation Agent - Quality Checks & Final Filtering

### Input (Scored Companies)
```json
[
  {"company_name": "Lithia Motors", "website_url": "https://www.lithia.com", "locations": ["California", "LA"], "fit_score": 92, "category": "Customer", "rationale": "...", ...},
  {"company_name": "Penske Automotive", "website_url": "https://www.penskeautomotive.com", "locations": ["California"], "fit_score": 89, ...},
  {"company_name": "Keyes Automotive", "website_url": "https://www.keyesauto.com", "locations": ["Southern California"], "fit_score": 85, ...},
  {"company_name": "Low Score Company", "fit_score": 18, ...},  // Below threshold
  {"company_name": "Missing Field Co", "website_url": "https://...", ...},  // Missing 'locations' field
  {"company_name": "Unknown Location Co", "locations": ["Location not specified"], "fit_score": 75, ...},  // Invalid location
  // ... 31 more companies
]
```

### Processing (No LLM - Rule-Based Validation)
```python
def validate_company(company):
    """Validate company meets all quality requirements."""
    
    # 1. Check all required fields exist
    required_fields = ['company_name', 'website_url', 'fit_score', 
                      'rationale', 'category', 'locations']
    for field in required_fields:
        if not company.get(field):
            return False, f"Missing required field: {field}"
    
    # 2. Validate fit_score meets minimum threshold
    min_score = 20  # Configurable threshold
    if company['fit_score'] < min_score:
        return False, f"Score too low: {company['fit_score']} < {min_score}"
    
    # 3. Validate URL format
    url = company['website_url']
    if not url.startswith(('http://', 'https://')) or '.' not in url:
        return False, "Invalid URL format"
    
    # 4. Validate locations are meaningful
    locations = company.get('locations', [])
    if not locations or len(locations) == 0:
        return False, "No locations provided"
    if locations == ['Location not specified']:
        return False, "Location not specified (placeholder)"
    
    # 5. Validate estimated_size
    valid_sizes = ['Small', 'Medium', 'Large']
    if company.get('estimated_size') not in valid_sizes:
        company['estimated_size'] = 'Medium'  # Default
    
    return True, "Valid"

# Apply validation to all companies
valid_companies = []
rejected_companies = []

for company in scored_companies:
    is_valid, reason = validate_company(company)
    
    if is_valid:
        valid_companies.append(company)
    else:
        rejected_companies.append({
            'name': company.get('company_name', 'Unknown'),
            'reason': reason
        })

# Sort by fit_score (descending)
valid_companies.sort(key=lambda x: x['fit_score'], reverse=True)

# Return top N companies
top_n = 10
final_results = valid_companies[:top_n]
```

### Validation Output
```
✅ Validating 37 companies...
  ✗ Low Score Company: Score too low: 18 < 20
  ✗ Missing Field Co: Missing required field: locations
  ✗ Unknown Location Co: Location not specified (placeholder)
✓ 34 companies passed validation
✓ Returning top 10 companies
```

**Metrics:**
- Latency: <0.1s (instant, rule-based)
- Tokens: 0 (no LLM)
- Cost: $0

**Validation Summary:**
- Input: 37 scored companies
- Rejected: 3 companies (validation failures)
- Valid: 34 companies
- Returned: Top 10 (sorted by fit_score)

---

### Output (Top 10)
```json
[
  {
    "company_name": "Lithia Motors",
    "website_url": "https://www.lithia.com",
    "category": "Automotive Dealership Group",
    "estimated_size": "50+ locations",
    "locations": ["California", "Los Angeles", "San Diego"],
    "fit_score": 92,
    "rationale": "Excellent fit for DealerFlow Cloud..."
  },
  {
    "company_name": "Penske Automotive Group",
    "website_url": "https://www.penskeautomotive.com",
    "category": "Automotive Dealership Group",
    "estimated_size": "25+ locations",
    "locations": ["California", "Los Angeles"],
    "fit_score": 89,
    "rationale": "Strong fit with premium brand focus..."
  },
  // ... 8 more companies
]
```

**Metrics:**
- Latency: <0.1s (instant)
- Tokens: 0 (no LLM)
- Cost: $0

---

## Final Output to User

### Main Results (Top 10 Companies)

| Rank | Company | Website | Category | Size | Locations | Score | Rationale |
|------|---------|---------|----------|------|-----------|-------|-----------|
| 1 | Lithia Motors | lithia.com | Customer | Large | California, LA, SD | 92 | Excellent fit - 50+ dealerships in target range... |
| 2 | Penske Automotive | penskeautomotive.com | Customer | Large | California, LA | 89 | Strong fit with premium brand focus... |
| 3 | Keyes Automotive | keyesauto.com | Customer | Medium | Southern CA | 85 | Good fit - 12 dealerships, family-owned... |
| 4-10 | ... | ... | ... | ... | ... | 80-84 | ... |

### Export Options
- CSV download with all fields
- JSON export for integrations
- Full company profiles with contact info

### Filtered Companies Report

**Filtered by Criteria (55 companies)**
```
Companies that didn't match: "Focus on Company located only in California"

  Company                   | Location              | Reason
  --------------------------|----------------------|---------------------------
  Van Horn Automotive       | Wisconsin, Iowa      | Not in California
  Tuttle-Click             | Arizona              | Not in California
  AutoNation (HQ)          | Florida              | Headquartered outside CA
  ...52 more
```

**Filtered by Validation (3 companies)**
```
Companies rejected during quality checks:

  Company                 | Reason
  ------------------------|--------------------------------
  Low Score Company       | Score too low: 18 < 20
  Missing Field Co        | Missing required field: locations
  Unknown Location Co     | Location not specified
```

### Processing Funnel
```
Search Results:      100 companies
↓ Enrichment (LLM):  95 extracted (5 not companies)
↓ Criteria Filter:   37 matching (58 filtered by criteria)
↓ Deduplication:     37 unique (0 duplicates in this run)
↓ Scoring (LLM):     37 scored
↓ Validation:        34 valid (3 rejected)
↓ Top N Selection:   10 final results
```

### Performance Characteristics
- **Accuracy**: 100% of results match user criteria
- **Quality**: All results pass strict validation (required fields, valid data)
- **Efficiency**: Criteria filtering reduces scoring API calls by ~60%
- **Transparency**: Users see what was filtered and why
- **Time**: ~7-8 minutes for complete discovery for top 10, ~3-4 mins for top 5

---

## System Execution Summary

### Complete Workflow

1. **Query Generation** - RAG system creates targeted search queries with criteria integrated
2. **Web Search** - Tavily API searches for companies matching queries
3. **Data Extraction** - LLM extracts structured data and validates criteria
4. **Criteria Filtering** - Separates matching from non-matching companies
5. **Deduplication** - Removes duplicate URLs and similar company names  
6. **Scoring** - LLM evaluates fit against ideal customer profile with RAG context
7. **Validation** - Rule-based quality checks ensure complete, valid data
8. **Results** - Top 10 companies delivered with filtered lists for transparency


### Data Quality Standards

All final results guarantee:
- ✅ All required fields present (name, URL, location, score, rationale, category)
- ✅ Valid URL format
- ✅ Real location data (no placeholders)
- ✅ Minimum fit score threshold met (20+)
- ✅ Criteria match (100% relevant to user request)
- ✅ No duplicates (by URL or company name)

### Output Transparency

Users receive:
- Top 10 validated companies with full details
- List of companies filtered by criteria (with reasons)
- List of companies rejected by validation (with reasons)
- Complete metrics and cost information
- Export options (CSV, JSON)
