from typing import Any, Optional
from pydantic import BaseModel

from ai_common import SearchQuery


class Person(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str] = None
    company: Optional[str] = None


class Company(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str]


class SearchState(BaseModel):
    """
    Represents the state of business search.

    Attributes:
        Given in alphabetical order
    """
    company: Optional[Company] = None
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

