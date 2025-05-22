import copy
import datetime
from typing import Any
import json
from unittest import case

from ai_common import LlmServers, get_llm
from .utils import generate_info_str, get_schema
from ..enums import SearchType, Node
from ..state import SearchState
from ..schema import PersonSchema, CompanySchema


PERSON_NOTE_TAKING_INSTRUCTIONS = """
Your goal is to extract information about a person, using the provided sources.

The person you are interested in:
<person>
{info}
</person>

The sources you are going to use:
<sources>
{content}
</sources>

Today's date is:
<today>
{today}
</today>

Please make sure that:
1. You extract information from the provided sources.
2. You maintain accuracy of the original content. Do not hallucinate.

Please note when important information appears to be missing or unclear.
When a particular information is missing in the given sources, return "Not Available" for that information.
"""

COMPANY_NOTE_TAKING_INSTRUCTIONS = """
Your goal is to extract information about a company, using the provided sources.

The company you are interested in:
<company>
{info}
</company>

The sources you are going to use:
<sources>
{content}
</sources>

Today's date is:
<today>
{today}
</today>

Please make sure that:
1. You extract information from the provided sources.
2. You maintain accuracy of the original content. Do not hallucinate.

Please note when important information appears to be missing or unclear.
When a particular information is missing in the given sources, return "Not Available" for that information. 
"""

NOTE_TAKING_INSTRUCTIONS = {
    SearchType.PERSON.value: PERSON_NOTE_TAKING_INSTRUCTIONS,
    SearchType.COMPANY.value: COMPANY_NOTE_TAKING_INSTRUCTIONS,
}


class NoteTaker:
    def __init__(self, llm_server: LlmServers, model_params: dict[str, Any]):
        self.llm_server = llm_server
        self.model_params = model_params

        self.model_params['model_name'] = self.model_params['reasoning_model']
        self.base_llm = get_llm(llm_server=self.llm_server, model_params=self.model_params)

    def run(self, state: SearchState) -> SearchState:

        state.steps.append(Node.NOTE_TAKER.value)

        info_str = generate_info_str(state=state)
        note_taking_instructions_template = NOTE_TAKING_INSTRUCTIONS[state.search_type]
        instructions = note_taking_instructions_template.format(info=info_str,
                                                                content=state.source_str,
                                                                today=datetime.date.today().isoformat())

        match state.search_type:
            case SearchType.PERSON.value:
                structured_llm = self.base_llm.with_structured_output(PersonSchema)
            case SearchType.COMPANY.value:
                structured_llm = self.base_llm.with_structured_output(CompanySchema)
            case _:
                raise RuntimeError(f"Unknown search type {state.search_type}")

        state.notes = structured_llm.invoke(instructions)
        return state
