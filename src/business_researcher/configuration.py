from ai_common import ConfigurationBase, TavilySearchCategory


DEFAULT_REPORT_STRUCTURE = """THIS WILL BE MODIFIED"""


class Configuration(ConfigurationBase):
    """The configurable fields for the chatbot."""
    number_of_queries: int = 3
    search_category: TavilySearchCategory = "general"
    number_of_days_back: int = None
    context_window_length: int = 4096
