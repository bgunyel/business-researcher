import copy
import datetime
from typing import Any

from ai_common import LlmServers, get_llm
from .utils import generate_info_str
from ..enums import SearchType, Node
from ..state import SearchState

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

Today's date is:
<today>
{today}
</today>

Generate notes about the person you are interested in. Do not generate notes about an hypothetical person.
Generate notes from the sources that are given to you. Do not generate notes from hypothetical sources.

Important: The sources may include information about multiple people with the same name. Leverage the email of the person you are looking for.

Please make sure that:
1. You generate notes from the provided sources.
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

Today's date is:
<today>
{today}
</today>

Generate notes about the company you are interested in. Do not generate notes about an hypothetical company.
Generate notes from the sources that are given to you. Do not generate notes from hypothetical sources.

Important: The sources may include information about multiple companies with the similar names. 

Please make sure that:
1. You generate notes from the provided sources.
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
    def __init__(self, llm_server: LlmServers, model_params: dict[str, Any]):
        self.llm_server = llm_server
        self.model_params = model_params

    def run(self, state: SearchState) -> SearchState:

        state.steps.append(Node.NOTE_TAKER.value)

        info_str = generate_info_str(state=state)
        note_taking_instructions_template = NOTE_TAKING_INSTRUCTIONS[state.search_type]

        schema = copy.deepcopy(state.extraction_schema)
        if len(state.search_focus) > 0:
            schema['required'] = state.search_focus
            schema['properties'] = {k: v for k, v in schema['properties'].items() if k in state.search_focus}

        instructions = note_taking_instructions_template.format(info=info_str,
                                                                content=state.source_str,
                                                                schema=schema,
                                                                today=datetime.date.today().isoformat())
        if state.iteration == 0:
            self.model_params['model_name'] = self.model_params['language_model']
        else:
            self.model_params['model_name'] = self.model_params['reasoning_model']

        base_llm = get_llm(llm_server=self.llm_server, model_params=self.model_params)
        structured_llm = base_llm.with_structured_output(schema=schema, method='json_schema')
        state.notes = structured_llm.invoke(instructions)
        return state
