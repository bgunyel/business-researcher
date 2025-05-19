from dataclasses import Field

from ai_common import ConfigurationBase, TavilySearchCategory


class Configuration(ConfigurationBase):
    """The configurable fields for the chatbot."""
    context_window_length: int = int(12 * 1024)
    max_iterations: int = 5
    number_of_days_back: int = None
    number_of_queries: int = 3
    search_category: TavilySearchCategory = "general"
