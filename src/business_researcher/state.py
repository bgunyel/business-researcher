from typing import Any, Optional, List
from pydantic import BaseModel, Field


class Person(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str] = None
    company: Optional[str] = None


class Company(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str]


class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")


class Queries(BaseModel):
    queries: List[SearchQuery] = Field(description="List of search queries.")


class SearchState(BaseModel):
    """
    Represents the state of business search.

    Attributes:
        Given in alphabetical order
    """
    company: Optional[Company] = None
    # extraction_schema: dict[str, Any]
    is_review_successful: bool
    iteration: int
    notes: dict[str, Any]
    out_info: dict[str, Any]
    person: Optional[Person] = None
    search_focus: list[str]
    search_queries: list[SearchQuery]
    search_type: str  # 'person' or 'company'
    source_str: str
    steps: list[str]
    unique_sources: dict[str, Any]

