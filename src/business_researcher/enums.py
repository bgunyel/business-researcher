from typing import ClassVar
from ai_common import NodeBase
from pydantic import BaseModel, ConfigDict

class SearchType(BaseModel):
    model_config = ConfigDict(frozen=True)
    # Class attributes
    COMPANY: ClassVar[str] = 'company'
    PERSON: ClassVar[str] = 'person'

class Node(NodeBase):
    model_config = ConfigDict(frozen=True)

    # Class attributes
    LINKEDIN_FINDER: ClassVar[str] = 'linkedin_finder'
    NOTE_TAKER: ClassVar[str] = 'note_taker'
    NOTE_REVIEWER: ClassVar[str] = 'note_reviewer'
    RESET: ClassVar[str] = 'reset'
