from ai_common import ConfigurationBase, TavilySearchCategory


class Configuration(ConfigurationBase):
    """The configurable fields for the chatbot."""
    number_of_queries: int = 1
    search_category: TavilySearchCategory = "general"
    number_of_days_back: int = None
    context_window_length: int = int(12 * 1024)
