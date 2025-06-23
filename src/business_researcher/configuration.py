from ai_common import CfgBase, TavilySearchCategory


class Configuration(CfgBase):
    """The configurable fields for the workflow"""
    max_iterations: int
    max_results_per_query: int
    max_tokens_per_source: int
    number_of_days_back: int = None
    number_of_queries: int
    search_category: TavilySearchCategory = "general"
