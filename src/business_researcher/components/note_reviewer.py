import copy
import json
from typing import Any
import pprint
import datetime

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
import rich

from ai_common import LlmServers, get_llm
from ..state import SearchState
from ..enums import Node, SearchType
from .utils import get_schema


REVIEW_PROMPT = """
You are a research analyst tasked with reviewing the quality and completeness of extracted information.

Compare the extracted information with the required schema:

<Schema>
{schema}
</Schema>

Here is the extracted information:
<extracted_info>
{info}
</extracted_info>

Today's date is:
<today>
{today}
</today>

TASK:
Analyze if all required fields are present and sufficiently populated. Consider:
1. Are any required fields missing?
2. Are any fields incomplete or containing uncertain information?
3. Are there fields with placeholder values or "unknown" markers?
4. Are there fields populated with outdated information?
"""


class ReviewOutput(BaseModel):
    is_satisfactory: bool = Field(
        description="True if all required fields are well populated, False otherwise"
    )
    missing_fields: list[str] = Field(
        description="List of field names that are missing or incomplete"
    )
    reasoning: str = Field(description="Brief explanation of the assessment")


class NoteReviewer:
    def __init__(self, llm_server: LlmServers, model_params: dict[str, Any]):
        model_params['model_name'] = model_params['reasoning_model']
        self.base_llm = get_llm(llm_server=llm_server, model_params=model_params)
        self.structured_llm = self.base_llm.with_structured_output(ReviewOutput)

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:

        if (
                ((state.search_type == SearchType.PERSON.value) and ('linkedin.com/in/' not in state.notes.linkedin_profile)) or
                ((state.search_type == SearchType.COMPANY.value) and ('linkedin.com/company/' not in state.notes.linkedin_profile))
        ):
            state.notes.linkedin_profile = 'Not Available'

        if state.iteration == 0:
            state.out_info = copy.deepcopy(state.notes)
        else:
            for key in state.search_focus:
                setattr(state.out_info, key, getattr(state.notes, key))

        state.steps.append(Node.NOTE_REVIEWER.value)
        state.iteration += 1

        schema = get_schema(state=state)
        instructions = REVIEW_PROMPT.format(schema=json.dumps(schema, indent=2),
                                            info=state.out_info.model_dump(),
                                            today=datetime.date.today().isoformat())
        results = self.structured_llm.invoke(instructions)

        state.is_review_successful = results.is_satisfactory
        state.search_focus = results.missing_fields

        print(f'iteration: {state.iteration - 1}')
        rich.print(state.search_queries)
        rich.print(state.out_info)
        rich.print(results)

        return state