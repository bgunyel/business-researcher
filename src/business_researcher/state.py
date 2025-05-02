from pydantic import BaseModel


class SearchState(BaseModel):
    """
    Represents the state of business search.

    Attributes:
        search_type: 'person' or 'company'
        steps: steps followed during graph run

    """
    search_type: str # 'person' or 'company'
    steps: list[str]
