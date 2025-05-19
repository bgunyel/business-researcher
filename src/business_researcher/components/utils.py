from ..state import SearchState
from ..enums import SearchType


def generate_info_str(state: SearchState):
    match state.search_type:
        case SearchType.PERSON.value:
            search_object = state.person
        case SearchType.COMPANY.value:
            search_object = state.company
        case _:
            raise ValueError('Invalid search type!')

    info_str = ''
    for attr in search_object.model_dump().keys():
        info_str += f'{attr.upper()}: {search_object.model_dump()[attr]}\n' if search_object.model_dump()[attr] is not None else ''

    return info_str
