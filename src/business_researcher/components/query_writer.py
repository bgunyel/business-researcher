from typing import Any, Final
import json

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import get_usage_metadata_callback

from ai_common import get_config_from_runnable, SearchQuery
from .utils import get_schema
from ..enums import Node, SearchType
from ..state import SearchState


PERSON_QUERY_WRITING_INSTRUCTIONS = """
Your goal is to generate targeted web search queries that will gather specific information about a person according to a given schema.
You will generate exactly {number_of_queries} queries.

<person>
{info}
</person>

<schema>
{schema}
</schema>

<Requirements>
When generating the search queries, ensure they:
1. Make sure to look up the right name.
2. Make sure to include the email in every query if email is provided.
3. Make sure to include the company in every query if company is provided.
4. Do not hallucinate search terms that will make you miss the persons profile entirely
5. Take advantage of the Linkedin URL if it exists, you can include the raw URL in your search query as that will lead you to the correct page guaranteed.

Your queries should be:
- Specific enough to avoid irrelevant results
- Targeted to gather information according to the schema
- Diverse enough to cover all aspects of the schema
</Requirements>

<Format>
* Format your response as a JSON object with one field:
    - queries: Queries you generate according to the given topic.
* Each query should have the following three fields:
    - search_query: Text of the query.
    - aspect: Which aspect of the topic the query aims to cover.
    - rationale: Your reasoning.    

Return the queries in JSON format:
{{
    queries: [
            {{
                "search_query": "string",
                "aspect": "string",
                "rationale": "string"
            }}
    ]
}}
</Format>

<Task>
It is very important that you generate exactly {number_of_queries} queries.
Generate targeted web search queries that will gather specific information about the given person according to the given schema.
</Task>
"""

COMPANY_QUERY_WRITING_INSTRUCTIONS = """
Your goal is to generate targeted web search queries that will gather specific information about a company according to a given schema.
You will generate exactly {number_of_queries} queries.

<company>
{info}
</company>

<schema>
{schema}
</schema>

<Requirements>
When generating the search queries, ensure they:
1. Focus on finding factual, up-to-date company information
2. Target official sources, news, and reliable business databases
3. Do not hallucinate search terms that will make you miss the company profile entirely
4. Include the company name and relevant business terms

Your queries should be:
- Specific enough to avoid irrelevant results
- Targeted to gather information according to the schema
- Diverse enough to cover all aspects of the schema
</Requirements>

<Format>
* Format your response as a JSON object with one field:
    - queries: Queries you generate according to the given topic.
* Each query should have the following three fields:
    - search_query: Text of the query.
    - aspect: Which aspect of the topic the query aims to cover.
    - rationale: Your reasoning.    

Return the queries in JSON format:
{{
    queries: [
            {{
                "search_query": "string",
                "aspect": "string",
                "rationale": "string"
            }}
    ]
}}
</Format>

<Task>
It is very important that you generate exactly {number_of_queries} queries.
Generate targeted web search queries that will gather specific information about the given company according to the given schema.
</Task>
"""

QUERY_WRITING_INSTRUCTIONS = {
    SearchType.PERSON: PERSON_QUERY_WRITING_INSTRUCTIONS,
    SearchType.COMPANY: COMPANY_QUERY_WRITING_INSTRUCTIONS,
}


class QueryWriter:
    def __init__(self, model_params: dict[str, Any], configuration_module_prefix: str):
        self.model_name = model_params['model']
        self.configuration_module_prefix: Final = configuration_module_prefix
        self.base_llm = init_chat_model(
            model=model_params['model'],
            model_provider=model_params['model_provider'],
            api_key=model_params['api_key'],
            **model_params['model_args']
        )
        # self.structured_llm = base_llm.with_structured_output(Queries)

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:
        """
        Generate targeted web search queries based on the search type and extraction schema.

        This method creates specialized search queries for either person or company research,
        using the appropriate instruction template and the current state information. The 
        queries are generated using a structured LLM output to ensure they align with the
        required data schema and search focus.

        Args:
            state (SearchState): The current search state containing:
                - search_type: Type of search (PERSON or COMPANY)
                - search_focus: List of specific fields to focus on (optional)
                - extraction_schema: Schema defining the structure of data to extract
                - Additional context information for query generation
            config (RunnableConfig): Runtime configuration containing:
                - Configurable parameters including number_of_queries
                - Other execution context settings

        Returns:
            SearchState: Updated state with:
                - search_queries: List of generated search query strings
                - steps: Updated to include QUERY_WRITER node
                - token_usage: Updated with LLM token consumption metrics

        Process:
            1. Extracts configuration parameters from the runnable config
            2. Adds QUERY_WRITER to the processing steps
            3. Generates contextual information string from current state
            4. Selects appropriate query instruction template based on search type
            5. Builds extraction schema, optionally filtered by search focus
            6. Formats instructions with context, schema, and query count
            7. Invokes structured LLM to generate queries matching the Queries schema
            8. Tracks token usage for monitoring and cost management
            9. Updates state with generated queries and returns modified state

        Note:
            - Query generation is optimized for the specific search type (person vs company)
            - Token usage is tracked for both input and output tokens
            - Search focus can limit schema properties to specific fields of interest
            - All queries are validated against the structured Queries output schema
        """

        configurable = get_config_from_runnable(
            configuration_module_prefix=self.configuration_module_prefix,
            config=config
        )
        state.steps.append(Node.QUERY_WRITER)
        query_instructions_template = QUERY_WRITING_INSTRUCTIONS[state.search_type]
        schema = get_schema(state = state)

        if len(state.search_focus) > 0:
            schema['required'] = state.search_focus
            schema['properties'] = {k: v for k, v in schema['properties'].items() if k in state.search_focus}

        instructions = query_instructions_template.format(info=state.topic,
                                                          schema=json.dumps(schema, indent=2),
                                                          number_of_queries=configurable.number_of_queries)
        with get_usage_metadata_callback() as cb:
            results = self.base_llm.invoke(instructions, response_format={"type": "json_object"})
            state.token_usage[self.model_name]['input_tokens'] += cb.usage_metadata[self.model_name]['input_tokens']
            state.token_usage[self.model_name]['output_tokens'] += cb.usage_metadata[self.model_name]['output_tokens']
            json_dict = json.loads(results.content)
            state.search_queries = [SearchQuery(**q) for q in json_dict['queries']]

        return state
