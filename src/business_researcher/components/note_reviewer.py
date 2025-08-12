import copy
import json
from typing import Any, Final
import datetime

from langchain_core.callbacks import get_usage_metadata_callback
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

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

<Format>
* Format your response as a JSON object.
* The JSON object should have the following fields:    
    - "is_satisfactory": (Boolean decision) True if all required fields are well populated, False otherwise.
    - "missing_fields": (List of string) List of field names that are missing or incomplete.    
    - "reasoning": (string) Brief explanation of the assessment.
</Format>

<Requirements>
* A field is marked as missing if that field is present in the schema but missing in the extracted information.
* A field is marked as missing if that field is incomplete or containing uncertain information.
* A field is marked as missing if that field contains placeholder values or "unknown" markers.
* A field is marked as missing if that field contains a value filled with a masked value (e.g. h***@langchain.com).
* A field is marked as missing if that field is populated with outdated information.  
</Requirements>

<Task>:
* Analyze if all required fields are present and sufficiently populated.
* Return your answer in the given JSON format.
</Task>
"""

"""
class ReviewOutput(BaseModel):
    is_satisfactory: bool = Field(
        description='True if all required fields are well populated, False otherwise'
    )
    missing_fields: list[str] = Field(
        description='List of field names that are missing or incomplete'
    )
    reasoning: str = Field(description='Brief explanation of the assessment')
"""


class NoteReviewer:
    def __init__(self, model_params: dict[str, Any], configuration_module_prefix: str):
        self.model_name = model_params['model']
        self.configuration_module_prefix: Final = configuration_module_prefix
        self.base_llm = init_chat_model(
            model=model_params['model'],
            model_provider=model_params['model_provider'],
            api_key=model_params['api_key'],
            **model_params['model_args']
        )
        # self.structured_llm = self.base_llm.with_structured_output(ReviewOutput)


    def run(self, state: SearchState) -> SearchState:
        """
        Review and validate the quality and completeness of extracted information.

        This method evaluates the extracted notes against the required schema to determine
        if all necessary information has been successfully gathered. It performs LinkedIn
        profile validation, manages iterative information accumulation, and provides
        structured feedback on missing or incomplete fields to guide further research.

        Args:
            state (SearchState): The current search state containing:
                - search_type: Type of search (PERSON or COMPANY) for validation rules
                - notes: Extracted information to be reviewed (PersonSchema or CompanySchema)
                - iteration: Current iteration count for tracking research progress
                - out_info: Accumulated output information across iterations
                - search_focus: Fields to focus on in subsequent iterations
                - token_usage: Dictionary to track LLM token consumption

        Returns:
            SearchState: Updated state with:
                - out_info: Updated accumulated information (first iteration or focused updates)
                - steps: Updated to include NOTE_REVIEWER node
                - iteration: Incremented iteration counter
                - is_review_successful: Boolean indicating if review criteria are met
                - search_focus: List of missing/incomplete fields for next iteration
                - token_usage: Updated with LLM token consumption metrics

        Process:
            1. Validates LinkedIn profile URLs based on search type requirements
            2. Manages information accumulation across iterations:
               - First iteration: Deep copy all extracted notes to out_info
               - Subsequent iterations: Update only focused fields in out_info
            3. Adds NOTE_REVIEWER to processing steps and increments iteration
            4. Generates schema-based review instructions with current date context
            5. Invokes structured LLM to assess information completeness
            6. Tracks token usage for monitoring and cost management
            7. Updates review status and identifies fields needing attention

        LinkedIn Validation:
            - Person searches: Requires 'linkedin.com/in/' in profile URL
            - Company searches: Requires 'linkedin.com/company/' in profile URL
            - Invalid profiles are marked as 'Not Available'

        Review Criteria:
            - Evaluates presence and quality of all required schema fields
            - Identifies incomplete, uncertain, or placeholder information
            - Considers temporal relevance of extracted data
            - Provides structured feedback for iterative improvement

        Note:
            - Uses ReviewOutput schema for structured assessment results
            - Supports iterative research by focusing on missing fields
            - Token usage tracking for monitoring and cost management
            - Current date provided for temporal context in review
        """

        if (
                ((state.search_type == SearchType.PERSON) and ('linkedin.com/in/' not in state.notes.linkedin_profile)) or
                ((state.search_type == SearchType.COMPANY) and ('linkedin.com/company/' not in state.notes.linkedin_profile))
        ):
            state.notes.linkedin_profile = 'Not Available'

        if state.iteration == 0:
            state.out_info = copy.deepcopy(state.notes)
        else:
            for key in state.search_focus:
                setattr(state.out_info, key, getattr(state.notes, key))



        schema = get_schema(state=state)
        instructions = REVIEW_PROMPT.format(schema=json.dumps(schema, indent=2),
                                            info=state.out_info.model_dump(),
                                            today=datetime.date.today().isoformat())

        with get_usage_metadata_callback() as cb:
            # results = self.structured_llm.invoke(instructions)
            results = self.base_llm.invoke(instructions, response_format={"type": "json_object"})
            json_dict = json.loads(results.content)

            state.token_usage[self.model_name]['input_tokens'] += cb.usage_metadata[self.model_name]['input_tokens']
            state.token_usage[self.model_name]['output_tokens'] += cb.usage_metadata[self.model_name]['output_tokens']
        state.is_review_successful = json_dict['is_satisfactory']

        if state.iteration == 0:
            state.search_focus = json_dict['missing_fields']
        else:
            state.search_focus = [x for x in json_dict['missing_fields'] if x in state.search_focus]

        # Leave these two steps as the last before return.
        state.steps.append(Node.NOTE_REVIEWER)
        state.iteration += 1
        return state
