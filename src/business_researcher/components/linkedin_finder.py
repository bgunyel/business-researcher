from ai_common import format_sources
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama

from .utils import generate_info_str
from ..enums import Node, SearchType
from ..state import SearchState

PERSON_LINKEDIN_FIND_INSTRUCTIONS = """
# Role
You are an expert researcher that specializes in analyzing the linkedin url, the contents of the url and a person's information.

# Task
Your task is to decide whether the given url belongs to the person below by analyzing the url and the url content. 

<person>
{info}
</person>

<url>
{url}
</url>

<url_content>
{url_content}
</url_content>

# Output:
Return your answer as a JSON Object with a single key 'result':
    * Return YES if the url and the url content belong to the person.
    * Return NO if the url does not belong to the person.

# Specifics
A valid Linkedin profile may contain the experience, education, skills, publications, projects, etc of the given person.
Be careful about linkedin profiles which belong to people other than the person you are given.
"""


COMPANY_LINKEDIN_FIND_INSTRUCTIONS = """
# Role
You are an expert researcher that specializes in analyzing the linkedin url, the contents of the url and a company's information.

# Task
Your task is to decide whether the given url belongs to the company below by analyzing the url and the url content. 

<company>
{info}
</company>

<url>
{url}
</url>

<url_content>
{url_content}
</url_content>

# Output:
Return your answer as a JSON Object with a single key 'result':
    * Return YES if the url and the url content belong to the company.
    * Return NO if the url does not belong to the company.

# Specifics
A valid Linkedin company page may contain the overview, website, industry, company size, funding, etc of the given company.
Be careful about linkedin company pages which belong to companies other than the company you are given.
"""

LINKEDIN_FIND_INSTRUCTIONS = {
    SearchType.PERSON.value: PERSON_LINKEDIN_FIND_INSTRUCTIONS,
    SearchType.COMPANY.value: COMPANY_LINKEDIN_FIND_INSTRUCTIONS,
}


class LinkedinFinder:
    def __init__(self, model_name: str, context_window_length: int, ollama_url: str):
        self.model_name = model_name
        self.linkedin_llm = ChatOllama(
            model=model_name,
            temperature=0,
            base_url=ollama_url,
            format='json',
            num_ctx=context_window_length,
        ) | JsonOutputParser()

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:
        # configurable = Configuration.from_runnable_config(config=config)
        state.steps.append(Node.LINKEDIN_FINDER.value)
        info_str = generate_info_str(state=state)
        linkedin_instructions_template = LINKEDIN_FIND_INSTRUCTIONS[state.search_type]

        unique_sources = {}
        for key, value in state.unique_sources.items():
            url = value['url']

            if (
                    ((state.search_type == SearchType.PERSON.value) and ('linkedin.com/in/' in url)) or
                    ((state.search_type == SearchType.COMPANY.value) and ('linkedin.com/company/' in url))
            ):
                content = value['content']
                raw_content = value['raw_content'] if value['raw_content'] is not None else ''
                content += raw_content
                instructions = linkedin_instructions_template.format(info=info_str, url=url, url_content=content)
                results = self.linkedin_llm.invoke(instructions)

                if results['result'] == 'YES':
                    unique_sources[url] = {'url': url,
                                           'content': content,
                                           'raw_content': raw_content,
                                           'title': value['title']}


        source_str = format_sources(unique_sources=unique_sources, max_tokens_per_source=5000, include_raw_content=True)
        state.unique_sources = unique_sources
        state.source_str = source_str
        return state
