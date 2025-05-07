from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableConfig

from ..enums import Node, SearchType
from ..state import SearchState
from ..configuration import Configuration
from ..schema import data_extraction_schema
from .utils import generate_info_str

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

Return the queries as a JSON object:

{{
    queries: [
            {{
                "query": "string",
                "aspect": "string",
                "rationale": "string"
            }}
    ]
}}
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

Return the queries as a JSON object:

{{
    queries: [
            {{
                "query": "string",
                "aspect": "string",
                "rationale": "string"
            }}
    ]
}}
"""

QUERY_WRITING_INSTRUCTIONS = {
    SearchType.PERSON.value: PERSON_QUERY_WRITING_INSTRUCTIONS,
    SearchType.COMPANY.value: COMPANY_QUERY_WRITING_INSTRUCTIONS,
}


class QueryWriter:
    def __init__(self, model_name: str, context_window_length: int, ollama_url: str):
        self.model_name = model_name
        self.query_writer_llm = ChatOllama(
            model=model_name,
            temperature=0,
            base_url=ollama_url,
            format='json',
            num_ctx=context_window_length,
        ) | JsonOutputParser()

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
        instructions = query_instructions_template.format(info=info_str,
                                                          schema=data_extraction_schema[state.search_type],
                                                          number_of_queries=configurable.number_of_queries)

        results = self.query_writer_llm.invoke(
            [
                SystemMessage(content=instructions),
                HumanMessage(content="Generate search queries that will help with research.")
            ]
        )

        state.search_queries = [x['query'] for x in results['queries']]
        return state
