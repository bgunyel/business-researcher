import copy
from typing import Any

from langchain_core.runnables import RunnableConfig

from .utils import generate_info_str, get_llm
from ..configuration import Configuration
from ..enums import Node, SearchType, LlmServers
from ..schema import data_extraction_schema
from ..state import SearchState, Queries

"""
QUERY_SCHEMA = {
    "description": "Queries",
    "title": "Queries",
    "type": "object",
    "required": [
        "queries",
    ],
    "properties": {
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    },
                    "rationale": {
                        "type": "string"
                    },
                }
            }
        }
    }
}
"""

PERSON_QUERY_WRITING_INSTRUCTIONS = """
Your goal is to generate targeted web search queries that will gather specific information about a person according to a given schema.

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

You will generate exactly {number_of_queries} queries.
Generate targeted web search queries that will gather specific information about the given person according to the given schema.
"""

COMPANY_QUERY_WRITING_INSTRUCTIONS = """
Your goal is to generate targeted web search queries that will gather specific information about a company according to a given schema.

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

You will generate exactly {number_of_queries} queries.
Generate targeted web search queries that will gather specific information about the given company according to the given schema.
"""

QUERY_WRITING_INSTRUCTIONS = {
    SearchType.PERSON.value: PERSON_QUERY_WRITING_INSTRUCTIONS,
    SearchType.COMPANY.value: COMPANY_QUERY_WRITING_INSTRUCTIONS,
}


class QueryWriter:
    def __init__(self, llm_server: LlmServers, model_params: dict[str, Any]):

        if llm_server == LlmServers.OLLAMA:
            model_params['format'] = 'json'

        model_params['model_name'] = model_params['language_model']
        self.base_llm = get_llm(llm_server=llm_server, model_params=model_params)
        self.structured_llm = self.base_llm.with_structured_output(Queries)

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:
        """
        Writes queries for comprehensive web search.
            :param state: The current flow state
            :param config: The configuration
        """
        configurable = Configuration.from_runnable_config(config = config)
        state.steps.append(Node.QUERY_WRITER.value)

        info_str = generate_info_str(state = state)
        query_instructions_template = QUERY_WRITING_INSTRUCTIONS[state.search_type]

        schema = copy.deepcopy(state.extraction_schema)
        if len(state.search_focus) > 0:
            schema['required'] = state.search_focus
            schema['properties'] = {k: v for k, v in schema['properties'].items() if k in state.search_focus}

        instructions = query_instructions_template.format(info=info_str,
                                                          schema=schema,
                                                          number_of_queries=configurable.number_of_queries)

        results = self.structured_llm.invoke(instructions)
        state.search_queries = results.queries
        # state.search_queries = [x['query'] for x in results['queries']]
        return state
