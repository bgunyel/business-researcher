from typing import Any

from ..state import SearchState
from ..enums import SearchType
from ..schema import PersonSchema, CompanySchema


def generate_info_str(state: SearchState):
    match state.search_type:
        case SearchType.PERSON:
            search_object = state.person
        case SearchType.COMPANY:
            search_object = state.company
        case _:
            raise ValueError('Invalid search type!')

    info_str = ''
    for attr in search_object.model_dump().keys():
        info_str += f'{attr.upper()}: {search_object.model_dump()[attr]}\n' if search_object.model_dump()[attr] is not None else ''

    return info_str


def generate_schema_str(schema: dict[str, Any]) -> str:
    schema_str = '\n'
    for k, v in schema['properties'].items():
        value = v['description']
        schema_str += f'{k}: {value}\n'
    return schema_str


def get_schema(state: SearchState) -> dict[str, Any]:
    match state.search_type:
        case SearchType.PERSON:
            schema = PersonSchema.model_json_schema()
        case SearchType.COMPANY:
            schema = CompanySchema.model_json_schema()
        case _:
            raise RuntimeError(f"Unknown search type {state.search_type}")
    return schema
