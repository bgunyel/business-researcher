from pydantic import Field
from ai_common import CfgBase, TavilySearchCategory, TavilySearchDepth


class Configuration(CfgBase):
    """The configurable fields for the workflow"""
    max_iterations: int = Field(gt=0)  # (0, inf)
    max_results_per_query: int = Field(gt=0)  # (0, inf)
    max_tokens_per_source: int = Field(gt=0)  # (0, inf)
    number_of_days_back: int = Field(gt=0, lt=50_000)  # (0, 50_000)
    number_of_queries: int = Field(gt=0)  # (0, inf)
    search_category: TavilySearchCategory = Field(description="Search Category")
    search_depth: TavilySearchDepth = Field(description=" Search Depth")
    chunks_per_source: int = Field(default=3, gt=0)
    include_images: bool = Field(default=False)
    include_image_descriptions: bool = Field(default=False)
    include_favicon: bool = Field(default=False)
    strip_thinking_tokens: bool = Field(default=True)
