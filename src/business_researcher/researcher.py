import asyncio
from typing import Any, Final
from uuid import uuid4

from ai_common import GraphBase
from ai_common.components import WebSearchNode
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from .components import QueryWriter, NoteTaker, NoteReviewer, is_review_successful, generate_info_str
from .configuration import Configuration
from .enums import SearchType, Node
from .state import SearchState, Person, Company


class BusinessResearcher(GraphBase):

    def __init__(self, llm_config: dict[str, Any], web_search_api_key: str) -> None:
        self.memory_saver = MemorySaver()
        self.models = list({llm_config['language_model']['model'], llm_config['reasoning_model']['model']})
        self.configuration_module_prefix: Final = 'business_researcher.configuration'

        self.query_writer = QueryWriter(model_params = llm_config['language_model'],
                                        configuration_module_prefix = self.configuration_module_prefix)
        self.web_search_node = WebSearchNode(model_params = llm_config['language_model'],
                                             web_search_api_key = web_search_api_key,
                                             configuration_module_prefix = self.configuration_module_prefix)
        self.note_taker = NoteTaker(model_params=llm_config['reasoning_model'],
                                    configuration_module_prefix=self.configuration_module_prefix)
        self.note_reviewer = NoteReviewer(model_params=llm_config['reasoning_model'],
                                          configuration_module_prefix=self.configuration_module_prefix)

        self.graph = self.build_graph()


        """
        self.web_search = WebSearch(api_key = web_search_api_key,
                                    search_category = config.search_category,
                                    number_of_days_back = config.number_of_days_back,
                                    include_raw_content = True)
        """

    """
    def web_search_run(self, state: SearchState) -> SearchState:
        unique_sources = self.web_search.search(search_queries=[query.search_query for query in state.search_queries])
        source_str = format_sources(unique_sources=unique_sources, max_tokens_per_source=5000, include_raw_content=True)
        state.steps.append(Node.WEB_SEARCH.value)
        state.source_str = source_str
        state.unique_sources = unique_sources
        return state
    """

    async def run(self, input_dict: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
        search_type = input_dict['search_type']

        match search_type:
            case SearchType.PERSON:
                person = Person(
                    name=input_dict['name'] if 'name' in input_dict.keys() else None,
                    company=input_dict['company'] if 'company' in input_dict.keys() else None,
                    email=input_dict['email'] if 'email' in input_dict.keys() else None,
                )
                company = None
            case SearchType.COMPANY:
                person = None
                company = Company(
                    name=input_dict['name'] if 'name' in input_dict.keys() else None,
                    email=input_dict['email'] if 'email' in input_dict.keys() else None,
                )
            case _:
                raise ValueError(f'Invalid search type! - Can be either {SearchType.PERSON} or {SearchType.COMPANY}')

        in_state = SearchState(
            company=company,
            is_review_successful=False,
            iteration=0,
            notes={},
            out_info={},
            person=person,
            search_focus=[],
            search_queries=[],
            search_type=search_type,
            source_str='',
            steps=[],
            token_usage={m: {'input_tokens': 0, 'output_tokens': 0} for m in self.models},
            topic='',
            unique_sources={},
        )
        in_state.topic = generate_info_str(state = in_state)

        for key in in_state.out_info.keys():
            in_state.out_info[key]['value'] = None

        out_state = await self.graph.ainvoke(in_state, config)

        out_dict = {
            'content': out_state['out_info'],
            # 'unique_sources': {k: v for d in out_state['cumulative_unique_sources'] for k, v in d.items()},
            'token_usage': out_state['token_usage'],
        }

        return out_dict


    def get_response(self, input_dict: dict[str, Any], verbose: bool = False):

        config = {
            "configurable": {
                'thread_id': str(uuid4()),
                'max_iterations': 3,
                'max_results_per_query': 4,
                'max_tokens_per_source': 10000,
                'number_of_days_back': 1e6,
                'number_of_queries': 3,
                'search_category': 'general',
            }
        }
        event_loop = asyncio.new_event_loop()
        out_dict = event_loop.run_until_complete(self.run(input_dict=input_dict["topic"], config=config))
        event_loop.close()
        return out_dict['content']


    def build_graph(self):
        workflow = StateGraph(SearchState, config_schema=Configuration)

        ## Nodes
        workflow.add_node(node=Node.QUERY_WRITER, action=self.query_writer.run)
        workflow.add_node(node=Node.WEB_SEARCH, action=self.web_search_node.run)
        workflow.add_node(node=Node.NOTE_TAKER, action=self.note_taker.run)
        workflow.add_node(node=Node.NOTE_REVIEWER, action=self.note_reviewer.run)

        ## Edges
        workflow.add_edge(start_key=START, end_key=Node.QUERY_WRITER)
        workflow.add_edge(start_key=Node.QUERY_WRITER, end_key=Node.WEB_SEARCH)
        workflow.add_edge(start_key=Node.WEB_SEARCH, end_key=Node.NOTE_TAKER)
        workflow.add_edge(start_key=Node.NOTE_TAKER, end_key=Node.NOTE_REVIEWER)

        workflow.add_conditional_edges(
            source=Node.NOTE_REVIEWER,
            path=is_review_successful,
            path_map={
                'successful': END,
                'unsuccessful': Node.QUERY_WRITER,
                'max_iter': END
            }
        )

        ## Compile graph
        compiled_graph = workflow.compile(checkpointer=self.memory_saver)
        return compiled_graph
