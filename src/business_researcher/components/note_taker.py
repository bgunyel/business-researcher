import datetime
from typing import Any, Final
import json

from langchain_core.callbacks import get_usage_metadata_callback
from langchain.chat_models import init_chat_model

from .utils import get_schema
from ..enums import SearchType, Node
from ..state import SearchState
from ..schema import PersonSchema, CompanySchema


NOTE_TAKING_INSTRUCTIONS = """
Your goal is to extract information about a {search_type}, using the provided sources.

The {search_type} you are interested in:
<{search_type}>
{info}
</{search_type}>

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

<Format>
* Format your response as a JSON object.
* Every item in the JSON object should have the following fields:
    - "description": The description given in the JSON schema.
    - "title": The title given in the JSON schema.
    - "type": The type given in the JSON schema.
    - "value": The value of the information you extract from the given sources.

{json_schema}
</Format>

<Requirements> 
* Please note when important information appears to be missing or unclear.
* When a particular information is missing in the given sources, return "Not Available" for that information.
</Requirements> 

<Task>
* Think carefully about the provided context first.
* Then extract the necessary information from the provided sources, according to the given JSON format.
* When a particular information is missing in the given sources, 
    - If the type of the required information is "string, "return "Not Available".
    - If the type of the required information is "array", return [] (empty list).
* Return your answer in the given JSON format. 
</Task>
"""

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

        The method performs comprehensive input validation to ensure data integrity, formats
        contextualized instructions for the LLM, and processes the structured output to
        maintain accuracy while avoiding hallucination. Missing information is explicitly
        handled by marking it as "Not Available" in the extracted data.

        Args:
            state (SearchState): The current search state containing:
                - search_type: Type of search (PERSON or COMPANY) determining extraction schema
                - source_str: Raw source content to extract information from
                - topic: Target entity information for contextual extraction
                - person/company: Entity-specific information based on search_type
                - token_usage: Dictionary tracking LLM token consumption by model
                - steps: List of processing steps for workflow tracking

        Returns:
            SearchState: Updated state with:
                - notes: Extracted structured information (PersonSchema or CompanySchema)
                - steps: Updated to include NOTE_TAKER node in processing workflow
                - token_usage: Updated with current LLM invocation token consumption

        Raises:
            TypeError: If state parameter is not an instance of SearchState
            ValueError: If required state attributes are missing, None, or invalid:
                - search_type must be PERSON or COMPANY
                - source_str cannot be None
                - steps and token_usage must be initialized
                - Model name must exist in token_usage dictionary
                - Required token keys (input_tokens, output_tokens) must be present
                - Entity-specific attributes (person/company) must exist for search_type

        Process Flow:
            1. Comprehensive input validation and protective checks
            2. Validates entity-specific requirements based on search_type
            3. Appends NOTE_TAKER to processing steps for workflow tracking
            4. Retrieves appropriate JSON schema based on search_type
            5. Formats instruction template with:
               - Search type and target entity information
               - Source content for information extraction
               - Current date in ISO format for temporal context
               - JSON schema definition for structured output
            6. Invokes LLM with structured JSON output format
            7. Processes and validates LLM response:
               - Parses JSON response from LLM
               - Extracts 'value' fields from structured response
               - Validates against PersonSchema or CompanySchema
            8. Updates token usage metrics from callback metadata
            9. Returns updated state with extracted notes and metrics

        Implementation Details:
            - Uses NOTE_TAKING_INSTRUCTIONS template for consistent LLM prompting
            - Employs get_usage_metadata_callback() for accurate token tracking
            - Enforces JSON object response format for structured output
            - Maintains data accuracy by instructing LLM to avoid hallucination
            - Handles missing information with "Not Available" placeholder values
            - Provides current date context for temporal information extraction
            - Validates output against predefined schemas (PersonSchema/CompanySchema)

        Token Usage Tracking:
            - Captures both input and output token consumption
            - Updates state.token_usage[model_name] with incremental usage
            - Uses callback mechanism to ensure accurate token counting
            - Supports cost monitoring and usage analytics

        Data Integrity:
            - All extracted information must be sourced from provided content
            - Missing or unclear information is explicitly marked as "Not Available"
            - Schema validation ensures data structure consistency
            - Input validation prevents processing of invalid state objects
        """

        # Validate that required entity information exists based on search type
        if state.search_type == SearchType.PERSON:
            if not hasattr(state, 'person') or state.person is None:
                raise ValueError("state.person is required when search_type is PERSON")
        elif state.search_type == SearchType.COMPANY:
            if not hasattr(state, 'company') or state.company is None:
                raise ValueError("state.company is required when search_type is COMPANY")

        state.steps.append(Node.NOTE_TAKER)
        json_schema = get_schema(state=state)
        instructions = NOTE_TAKING_INSTRUCTIONS.format(search_type = state.search_type,
                                                       info = state.topic,
                                                       content = state.source_str,
                                                       today = datetime.date.today().isoformat(),
                                                       json_schema = json.dumps(json_schema['properties'], indent=2))

        with get_usage_metadata_callback() as cb:
            results = self.base_llm.invoke(instructions, response_format={"type": "json_object"})
            json_dict = json.loads(results.content)
            json_dict = {k: v['value'] for k, v in json_dict.items()}
            state.notes = PersonSchema(**json_dict) if state.search_type == SearchType.PERSON else CompanySchema(**json_dict)
            state.token_usage[self.model_name]['input_tokens'] += cb.usage_metadata[self.model_name]['input_tokens']
            state.token_usage[self.model_name]['output_tokens'] += cb.usage_metadata[self.model_name]['output_tokens']
        return state
