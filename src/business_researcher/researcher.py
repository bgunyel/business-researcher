from unittest import case
from uuid import uuid4
from pprint import pprint
from typing import Any

from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableConfig

from ai_common import GraphBase, WebSearch
from .configuration import Configuration
from .enums import SearchType, Node
from .schema import data_extraction_schema
from .state import SearchState, Person, Company
from .components.query_writer import QueryWriter


class Researcher(GraphBase):

    def __init__(self, model_name: str, ollama_url: str, web_search_api_key: str) -> None:
        config = Configuration()
        self.query_writer = QueryWriter(model_name = model_name,
                                        ollama_url = ollama_url,
                                        context_window_length = config.context_window_length)
        self.web_search = WebSearch(api_key=web_search_api_key,
                                    search_category=config.search_category,
                                    number_of_days_back=config.number_of_days_back,
                                    include_raw_content=True)

        self.graph = self.build_graph()


    def web_search_run(self, state: SearchState, config: RunnableConfig) -> SearchState:
        source_str = self.web_search.search(search_queries=state.search_queries)
        state.steps.append(Node.WEB_SEARCH.value)
        state.source_str = source_str
        return state


    def get_response(self, input_dict: dict[str, Any], verbose: bool = False):

        search_type = input_dict['search_type'].value
        schema = data_extraction_schema[search_type]

        match search_type:
            case SearchType.PERSON.value:
                person = Person(
                    name = input_dict['name'] if 'name' in input_dict.keys() else None,
                    company = input_dict['company'] if 'company' in input_dict.keys() else None,
                    linkedin = input_dict['linkedin'] if 'linkedin' in input_dict.keys() else None,
                    email = input_dict['email'] if 'email' in input_dict.keys() else None,
                    role = input_dict['role'] if 'role' in input_dict.keys() else None,
                )
                company = None
            case SearchType.COMPANY.value:
                person = None
                company = Company(
                    name = input_dict['name'] if 'name' in input_dict.keys() else None,
                    email = input_dict['email'] if 'email' in input_dict.keys() else None,
                )
            case _:
                raise ValueError(f'Invalid search type! - Can be either {SearchState.PERSON.value} or {SearchType.COMPANY.value}')

        in_state = SearchState(
            search_type = search_type,
            person = person,
            company = company,
            steps = [],
            search_queries = [],
            extraction_schema = schema,
            source_str= '',
        )

        config = {"configurable": {"thread_id": str(uuid4())}}
        out_state = self.graph.invoke(in_state, config)
        return out_state['content']


    def build_graph(self):
        workflow = StateGraph(SearchState, config_schema=Configuration)

        ## Nodes
        workflow.add_node(node=Node.QUERY_WRITER.value, action=self.query_writer.run)
        workflow.add_node(node=Node.WEB_SEARCH.value, action=self.web_search_run)

        ## Edges
        workflow.add_edge(start_key=START, end_key=Node.QUERY_WRITER.value)
        workflow.add_edge(start_key=Node.QUERY_WRITER.value, end_key=Node.WEB_SEARCH.value)
        workflow.add_edge(start_key=Node.WEB_SEARCH.value, end_key=END)

        # Compile graph
        compiled_graph = workflow.compile()
        return compiled_graph