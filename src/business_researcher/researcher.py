from unittest import case
from uuid import uuid4
from pprint import pprint
from typing import Any

from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableConfig

from ai_common import GraphBase, WebSearch, format_sources
from .configuration import Configuration
from .enums import SearchType, Node, LlmServers
from .schema import data_extraction_schema
from .state import SearchState, Person, Company
from .components.linkedin_finder import LinkedinFinder
from .components.query_writer import QueryWriter
from .components.note_taker import NoteTaker
from .components.note_reviewer import NoteReviewer
from .components.routing import is_review_successful


class BusinessResearcher(GraphBase):

    def __init__(self, llm_server: LlmServers, llm_config: dict[str, Any], web_search_api_key: str) -> None:
        config = Configuration()

        self.query_writer = QueryWriter(llm_server=llm_server, model_params=llm_config)
        self.web_search = WebSearch(api_key = web_search_api_key,
                                    search_category = config.search_category,
                                    number_of_days_back = config.number_of_days_back,
                                    include_raw_content = True)
        self.note_taker = NoteTaker(llm_server=llm_server, model_params=llm_config)
        self.note_reviewer = NoteReviewer(llm_server=llm_server, model_params=llm_config)

        self.graph = self.build_graph()


    def web_search_run(self, state: SearchState, config: RunnableConfig) -> SearchState:
        """
        if state.iteration == 1:
            match state.search_type:
                case SearchType.PERSON.value:
                    query = f'{state.person.name} linkedin profile'
                    query += f' {state.person.email}' if state.person.email is not None else ''
                    query += f' {state.person.company}' if state.person.company is not None else ''
                case SearchType.COMPANY.value:
                    query = f'{state.company.name} linkedin company page'
                    query += f' {state.company.email}' if state.company.email is not None else ''
                case _:
                    raise RuntimeError(f'Unknown search type {state.search_type}')
            state.search_queries = [query]
        else:
            pass
        """

        unique_sources = self.web_search.search(search_queries=[query.search_query for query in state.search_queries])
        source_str = format_sources(unique_sources=unique_sources, max_tokens_per_source=5000, include_raw_content=True)
        state.steps.append(Node.WEB_SEARCH.value)
        state.source_str = source_str
        state.unique_sources = unique_sources
        return state


    def get_response(self, input_dict: dict[str, Any], verbose: bool = False):

        search_type = input_dict['search_type'].value

        match search_type:
            case SearchType.PERSON.value:
                person = Person(
                    name = input_dict['name'] if 'name' in input_dict.keys() else None,
                    company = input_dict['company'] if 'company' in input_dict.keys() else None,
                    email = input_dict['email'] if 'email' in input_dict.keys() else None,
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
            company=company,
            extraction_schema=data_extraction_schema[search_type],
            is_review_successful=False,
            iteration=0,
            notes={},
            out_info={},
            person = person,
            search_focus=[],
            search_queries=[],
            search_type=search_type,
            source_str= '',
            steps=[],
            unique_sources={},
        )

        for key in in_state.out_info.keys():
            in_state.out_info[key]['value'] = None

        config = {"configurable": {"thread_id": str(uuid4())}}
        out_state = self.graph.invoke(in_state, config)
        return out_state['out_info']


    def build_graph(self):
        workflow = StateGraph(SearchState, config_schema=Configuration)

        ## Nodes
        workflow.add_node(node=Node.QUERY_WRITER.value, action=self.query_writer.run)
        workflow.add_node(node=Node.WEB_SEARCH.value, action=self.web_search_run)
        # workflow.add_node(node=Node.LINKEDIN_FINDER.value, action=self.linkedin_finder.run)
        workflow.add_node(node=Node.NOTE_TAKER.value, action=self.note_taker.run)
        workflow.add_node(node=Node.NOTE_REVIEWER.value, action=self.note_reviewer.run)

        ## Edges
        # workflow.add_edge(start_key=START, end_key=Node.WEB_SEARCH.value)
        workflow.add_edge(start_key=START, end_key=Node.QUERY_WRITER.value)
        workflow.add_edge(start_key=Node.QUERY_WRITER.value, end_key=Node.WEB_SEARCH.value)
        workflow.add_edge(start_key=Node.WEB_SEARCH.value, end_key=Node.NOTE_TAKER.value)
        workflow.add_edge(start_key=Node.NOTE_TAKER.value, end_key=Node.NOTE_REVIEWER.value)

        workflow.add_conditional_edges(
            source=Node.NOTE_REVIEWER.value,
            path=is_review_successful,
            path_map={
                'successful': END,
                'unsuccessful': Node.QUERY_WRITER.value,
                'max_iter': END
            }
        )


        # Compile graph
        compiled_graph = workflow.compile()
        return compiled_graph
