from typing import Any, Final
import json

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks import get_usage_metadata_callback

from ai_common import Queries, get_config_from_runnable
from .utils import generate_info_str, get_schema
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

It is very important that you generate exactly {number_of_queries} queries.
Generate targeted web search queries that will gather specific information about the given person according to the given schema.
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

When generating the search queries, ensure they:
1. Focus on finding factual, up-to-date company information
2. Target official sources, news, and reliable business databases
3. Do not hallucinate search terms that will make you miss the company profile entirely
4. Include the company name and relevant business terms

Your queries should be:
- Specific enough to avoid irrelevant results
- Targeted to gather information according to the schema
- Diverse enough to cover all aspects of the schema

It is very important that you generate exactly {number_of_queries} queries.
Generate targeted web search queries that will gather specific information about the given company according to the given schema.
"""

QUERY_WRITING_INSTRUCTIONS = {
    SearchType.PERSON: PERSON_QUERY_WRITING_INSTRUCTIONS,
    SearchType.COMPANY: COMPANY_QUERY_WRITING_INSTRUCTIONS,
}


class QueryWriter:
    def __init__(self, model_params: dict[str, Any], configuration_module_prefix: str):
        self.model_name = model_params['model']
        self.configuration_module_prefix: Final = configuration_module_prefix
        base_llm = init_chat_model(
            model=model_params['model'],
            model_provider=model_params['model_provider'],
            api_key=model_params['api_key'],
            **model_params['model_args']
        )
        self.structured_llm = base_llm.with_structured_output(Queries)

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:
        """
        Writes queries for comprehensive web search.
            :param state: The current flow state
            :param config: The configuration
        """
        configurable = get_config_from_runnable(
            configuration_module_prefix=self.configuration_module_prefix,
            config=config
        )
        state.steps.append(Node.QUERY_WRITER)

        info_str = generate_info_str(state = state)
        query_instructions_template = QUERY_WRITING_INSTRUCTIONS[state.search_type]
        schema = get_schema(state = state)

        if len(state.search_focus) > 0:
            schema['required'] = state.search_focus
            schema['properties'] = {k: v for k, v in schema['properties'].items() if k in state.search_focus}

        instructions = query_instructions_template.format(info=info_str,
                                                          schema=json.dumps(schema, indent=2),
                                                          number_of_queries=configurable.number_of_queries)
        with get_usage_metadata_callback() as cb:
            results = self.structured_llm.invoke(instructions)
            state.search_queries = results.queries
            state.token_usage[self.model_name]['input_tokens'] += cb.usage_metadata[self.model_name]['input_tokens']
            state.token_usage[self.model_name]['output_tokens'] += cb.usage_metadata[self.model_name]['output_tokens']

        return state
