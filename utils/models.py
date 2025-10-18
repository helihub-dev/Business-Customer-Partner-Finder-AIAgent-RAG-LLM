"""Data models for company discovery."""
from typing import List, 
from pydantic import BaseModel, HttpUrl, Field


class CompanyResult(BaseModel):
    """Structured output for discovered companies."""
    company_name: str = Field(description="Official company name")
    website_url: str = Field(description="Company website URL")
    locations: List[str] = Field(description="Cities/regions where they operate")
    estimated_size: str = Field(
        description="Company size estimate"
    )
    rationale: str = Field(
        description="2-3 sentence explanation for selection"
    )
    fit_score: int = Field(
        ge=0, le=100, 
        description="Fit score from 0-100"
    )
    category: str = Field(
        description="Whether this is a customer or partner prospect"
    )


class SearchQuery(BaseModel):
    """Search query configuration."""
    query_type: str
    additional_criteria: str = ""
    max_results: int = 10
