from pydantic import Field
from ai_common import CfgBase, TavilySearchCategory, TavilySearchDepth


class Configuration(CfgBase):
    """The configurable fields for the workflow"""
    max_iterations: int = Field(gt=0)  # (0, inf)
    max_results_per_query: int = Field(gt=0)  # (0, inf)
    max_tokens_per_source: int = Field(gt=0)  # (0, inf)
    number_of_days_back: int = None
    number_of_queries: int = Field(gt=0)  # (0, inf)
    search_category: TavilySearchCategory = Field(default="general")
    search_depth: TavilySearchDepth = Field(default="basic")
    chunks_per_source: int = Field(default=3, gt=0)
    include_images: bool = False
    include_image_descriptions: bool = False
    include_favicon: bool = False
    strip_thinking_tokens: bool  # = True
