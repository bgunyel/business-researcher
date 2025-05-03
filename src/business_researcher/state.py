from typing import Any, Optional
from pydantic import BaseModel


class Person(BaseModel):
    """Class representing the person to research."""

    name: Optional[str] = None
    company: Optional[str] = None
    linkedin: Optional[str] = None
    email: str
    role: Optional[str] = None


class Company(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str]


class SearchState(BaseModel):
    """
    Represents the state of business search.

    Attributes:
        search_type: 'person' or 'company'
        steps: steps followed during graph run

    """
    search_queries: list[str]
    source_str: str
    steps: list[str]
    search_type: str # 'person' or 'company'
    person: Optional[Person] = None
    company: Optional[Company] = None
    extraction_schema: dict[str, Any]
