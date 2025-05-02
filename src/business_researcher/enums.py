from enum import Enum


class SearchType(Enum):
    COMPANY = 'company'
    PERSON = 'person'

class Node(Enum):
    # In alphabetical order
    QUERY_WRITER = 'query_writer'
    RESET = 'reset'
    WEB_SEARCH = 'web_search'

