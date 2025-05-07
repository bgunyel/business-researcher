import json
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from ..configuration import Configuration
from ..enums import SearchType, Node
from ..schema import data_extraction_schema
from ..state import SearchState
from .utils import generate_info_str


PERSON_NOTE_TAKING_INSTRUCTIONS = """
Your goal is to take clear, organized notes about a person, using the provided sources.
You will focus on information according to the given schema.

The person you are interested in:
<person>
{info}
</person>

The sources you are going to use:
<sources>
{content}
</sources>

The schema you are going to focus:
<schema>
{schema}
</schema>

Use the person you are interested in. Do not generate notes about an hypothetical person.
Use the sources that are given to you. Do not generate notes from hypothetical sources.

Important: The sources may include information about multiple people with the same name. Leverage the email of the person you are looking for.

Please make sure that:
1. You use the provided sources.
2. Your notes are detailed, well-organized and easy to read.
3. Your notes include specific facts, dates, and figures when available.
4. Your notes maintain accuracy of the original content. Do not hallucinate.

Please note when important information appears to be missing or unclear.
When a particular information is missing in the given sources, return "Not Available" for that information.
"""

COMPANY_NOTE_TAKING_INSTRUCTIONS = """
Your goal is to take clear, organized notes about a company, using the provided sources.
You will focus on information according to the given schema.

The company you are interested in:
<company>
{info}
</company>

The sources you are going to use:
<sources>
{content}
</sources>

The schema you are going to focus:
<schema>
{schema}
</schema>

Use the company you are interested in. Do not generate notes about an hypothetical company.
Use the sources that are given to you. Do not generate notes from hypothetical sources.

Important: The sources may include information about multiple companies with the similar names. 

Please make sure that:
1. You use the provided sources.
2. Your notes are detailed, well-organized and easy to read.
3. Your notes include specific facts, dates, and figures when available.
4. Your notes maintain accuracy of the original content. Do not hallucinate.

Please note when important information appears to be missing or unclear.
When a particular information is missing in the given sources, return "Not Available" for that information. 
"""

NOTE_TAKING_INSTRUCTIONS = {
    SearchType.PERSON.value: PERSON_NOTE_TAKING_INSTRUCTIONS,
    SearchType.COMPANY.value: COMPANY_NOTE_TAKING_INSTRUCTIONS,
}


class NoteTaker:
    def __init__(self, model_name: str, context_window_length: int, ollama_url: str):
        self.model_name = model_name
        """
        self.note_taker_llm = ChatOllama(
            model=model_name,
            temperature=0,
            base_url=ollama_url,
            format='json',
            num_ctx=context_window_length,
        ) | JsonOutputParser()
        """

        self.base_llm = ChatOllama(
            model=model_name,
            temperature=0,
            base_url=ollama_url,
            num_ctx=context_window_length,
        )

    def run(self, state: SearchState, config: RunnableConfig) -> SearchState:

        configurable = Configuration.from_runnable_config(config=config)
        state.steps.append(Node.NOTE_TAKER.value)

        info_str = generate_info_str(state=state)
        note_taking_instructions_template = NOTE_TAKING_INSTRUCTIONS[state.search_type]
        instructions = note_taking_instructions_template.format(info=info_str,
                                                                content=state.source_str,
                                                                schema=json.dumps(data_extraction_schema[state.search_type], indent=2))

        # results = self.note_taker_llm.invoke(instructions)
        structured_llm = self.base_llm.with_structured_output(schema=state.extraction_schema, method='json_schema')
        results = structured_llm.invoke(instructions)
        state.notes = results

        for key, value in results.items():
            if key in state.out_info.keys():
                state.out_info[key]['value'] = value['property_value'] if value['property_value'] is not None else value

        return state
