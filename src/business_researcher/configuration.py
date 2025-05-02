from ai_common import ConfigurationBase, TavilySearchCategory


DEFAULT_REPORT_STRUCTURE = """THIS WILL BE MODIFIED"""


class Configuration(ConfigurationBase):
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE
    number_of_queries: int = 2
    search_category: TavilySearchCategory = "general"
    number_of_days_back: int = None
    research_iterations: int = 3
    context_window_length: int = 4096
