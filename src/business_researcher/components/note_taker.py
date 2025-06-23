import datetime
from typing import Any, Final

from langchain_core.callbacks import get_usage_metadata_callback
from langchain.chat_models import init_chat_model

from .utils import generate_info_str
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
    SearchType.PERSON: PERSON_NOTE_TAKING_INSTRUCTIONS,
    SearchType.COMPANY: COMPANY_NOTE_TAKING_INSTRUCTIONS,
}


class NoteTaker:
    def __init__(self, model_params: dict[str, Any], configuration_module_prefix: str):
        self.model_name = model_params['model']
        self.configuration_module_prefix: Final = configuration_module_prefix
        self.base_llm = init_chat_model(
            model=model_params['model'],
            model_provider=model_params['model_provider'],
            api_key=model_params['api_key'],
            **model_params['model_args']
        )


    def run(self, state: SearchState) -> SearchState:
        """
        Extract structured information from source content based on search type.

        This method processes the source content provided in the search state and extracts
        structured information about either a person or company using specialized instruction
        templates and appropriate schema validation. The extraction is performed using an
        LLM with structured output to ensure data consistency and accuracy, while tracking
        token usage for monitoring and cost management.

        Args:
            state (SearchState): The current search state containing:
                - search_type: Type of search (PERSON or COMPANY) determining extraction schema
                - source_str: Raw source content to extract information from
                - person or company: Target entity information for context
                - token_usage: Dictionary to track LLM token consumption
                - Additional context for information extraction

        Returns:
            SearchState: Updated state with:
                - notes: Extracted structured information (PersonSchema or CompanySchema)
                - steps: Updated to include NOTE_TAKER node
                - token_usage: Updated with LLM token consumption metrics

        Process:
            1. Adds NOTE_TAKER to the processing steps
            2. Generates contextual information string about the target entity
            3. Selects appropriate instruction template based on search type
            4. Formats instructions with entity info, source content, and current date
            5. Configures structured LLM output based on search type:
               - PersonSchema for person searches
               - CompanySchema for company searches
            6. Invokes LLM to extract structured information from sources
            7. Tracks token usage for both input and output tokens
            8. Updates state with extracted notes and token metrics

        Raises:
            RuntimeError: If an unknown search type is encountered

        Note:
            - Extraction maintains accuracy and avoids hallucination
            - Missing information is marked as "Not Available"
            - Current date is provided for temporal context in ISO format
            - Output is validated against the appropriate schema (PersonSchema/CompanySchema)
            - All extracted information is sourced from provided content only
            - Token usage is tracked for monitoring and cost management purposes
            - Uses callback mechanism to capture usage metadata during LLM invocation
        """
        # Input validation and protective checks
        if not isinstance(state, SearchState):
            raise TypeError("state must be an instance of SearchState")
        
        if not hasattr(state, 'search_type') or not state.search_type:
            raise ValueError("state.search_type is required and cannot be empty")
        
        if state.search_type not in [SearchType.PERSON, SearchType.COMPANY]:
            raise ValueError(f"Invalid search_type: {state.search_type}. Must be '{SearchType.PERSON}' or '{SearchType.COMPANY}'")
        
        if not hasattr(state, 'source_str') or state.source_str is None:
            raise ValueError("state.source_str is required and cannot be None")
        
        if not hasattr(state, 'steps') or state.steps is None:
            raise ValueError("state.steps is required and cannot be None")
        
        if not hasattr(state, 'token_usage') or state.token_usage is None:
            raise ValueError("state.token_usage is required and cannot be None")
        
        if self.model_name not in state.token_usage:
            raise ValueError(f"Model '{self.model_name}' not found in state.token_usage")
        
        required_token_keys = ['input_tokens', 'output_tokens']
        for key in required_token_keys:
            if key not in state.token_usage[self.model_name]:
                raise ValueError(f"Missing '{key}' in state.token_usage['{self.model_name}']")
        
        # Validate that required entity information exists based on search type
        if state.search_type == SearchType.PERSON:
            if not hasattr(state, 'person') or state.person is None:
                raise ValueError("state.person is required when search_type is PERSON")
        elif state.search_type == SearchType.COMPANY:
            if not hasattr(state, 'company') or state.company is None:
                raise ValueError("state.company is required when search_type is COMPANY")

        state.steps.append(Node.NOTE_TAKER)

        info_str = generate_info_str(state=state)
        note_taking_instructions_template = NOTE_TAKING_INSTRUCTIONS[state.search_type]
        instructions = note_taking_instructions_template.format(info=info_str,
                                                                content=state.source_str,
                                                                today=datetime.date.today().isoformat())
        # noinspection PyUnreachableCode
        match state.search_type:
            case SearchType.PERSON:
                structured_llm = self.base_llm.with_structured_output(PersonSchema)
            case SearchType.COMPANY:
                structured_llm = self.base_llm.with_structured_output(CompanySchema)
            case _:
                raise RuntimeError(f"Unknown search type {state.search_type}")

        with get_usage_metadata_callback() as cb:
            state.notes = structured_llm.invoke(instructions)
            state.token_usage[self.model_name]['input_tokens'] += cb.usage_metadata[self.model_name]['input_tokens']
            state.token_usage[self.model_name]['output_tokens'] += cb.usage_metadata[self.model_name]['output_tokens']
        return state
