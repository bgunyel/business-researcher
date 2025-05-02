from unittest import case
from uuid import uuid4
from pprint import pprint
from typing import Any

from langgraph.graph import START, END, StateGraph
from langchain_core.runnables import RunnableConfig

from ai_common import GraphBase
from .configuration import Configuration
from .enums import SearchType, Node
from .schema import data_extraction_schema


class Researcher(GraphBase):

    def __init__(self):
        pass


    def get_response(self, input_dict: dict[str, Any], verbose: bool = False):

        search_type = input_dict['search_type'].value
        schema = data_extraction_schema[search_type]


        return "Hello"


    def build_graph(self):
        workflow = StateGraph(SummaryState, config_schema=Configuration)

        ## Nodes


        ## Edges



        # Compile graph
        compiled_graph = workflow.compile()
        return compiled_graph