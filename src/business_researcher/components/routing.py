from typing import Literal
from langchain_core.runnables import RunnableConfig

from .. state import SearchState
from ..configuration import Configuration


def is_review_successful(state: SearchState, config: RunnableConfig) -> Literal['successful', 'unsuccessful', 'max_iter']:
    configurable = Configuration.from_runnable(runnable=config)

    if state.is_review_successful:
        return 'successful'
    else:
        if state.iteration == configurable.max_iterations:
            return 'max_iter'
        else:
            return 'unsuccessful'
