import copy
import json
from typing import Any
import pprint
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from ai_common import LlmServers, get_llm
from ..state import SearchState
from ..enums import Node


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

TASK:
Analyze if all required fields are present and sufficiently populated. Consider:
1. Are any required fields missing?
2. Are any fields incomplete or containing uncertain information?
3. Are there fields with placeholder values or "unknown" markers?
"""


class ReviewOutput(BaseModel):
    is_satisfactory: bool = Field(
        description="True if all required fields are well populated, False otherwise"
    )
    missing_fields: list[str] = Field(
        description="List of field names that are missing or incomplete"
    )
    search_queries: list[str] = Field(
        description="If is_satisfactory is False, provide 1-3 targeted search queries to find the missing information"
    )
    reasoning: str = Field(description="Brief explanation of the assessment")


class NoteReviewer:
    def __init__(self, llm_server: LlmServers, model_params: dict[str, Any]):
        model_params['model_name'] = model_params['reasoning_model']
        self.base_llm = get_llm(llm_server=llm_server, model_params=model_params)
        self.structured_llm = self.base_llm.with_structured_output(ReviewOutput)

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:

        if state.iteration == 0:
            state.out_info = copy.deepcopy(state.notes)
        else:
            for k, v in state.notes.items():
                state.out_info[k] = v

        state.steps.append(Node.NOTE_REVIEWER.value)
        state.iteration += 1

        instructions = REVIEW_PROMPT.format(schema=json.dumps(state.extraction_schema, indent=2),
                                            info=state.out_info)
        results = self.structured_llm.invoke(instructions)

        state.is_review_successful = results.is_satisfactory
        state.search_focus = results.missing_fields

        print(f'iteration: {state.iteration - 1}')
        pprint.pp(state.notes)
        pprint.pp(state.out_info)
        pprint.pp(state.search_queries)

        return state