from typing import Any, Optional
from pydantic import BaseModel

from ai_common import SearchQuery
from .schema import PersonSchema, CompanySchema


class Person(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str] = None
    company: Optional[str] = None


class Company(BaseModel):
    """Class representing the person to research."""

    name: str
    email: Optional[str]


class SearchState(BaseModel):
    """
    Comprehensive state management for business research workflows.

    SearchState serves as the central data structure that tracks and manages all aspects
    of a business research session, including entity information, search progress, 
    extracted data, and operational metadata. It supports both person and company
    research workflows with comprehensive state tracking throughout the entire
    research pipeline.

    The state object is passed through all components of the business research system,
    allowing each component to access necessary information, update progress, and
    contribute to the final research output. It maintains data integrity through
    Pydantic validation and provides a unified interface for all research operations.

    Key Functionality:
        - Entity Management: Stores person or company information being researched
        - Search Coordination: Manages search queries, focus areas, and iteration tracking
        - Data Extraction: Holds raw source content and structured extracted information
        - Progress Tracking: Maintains workflow steps and success/failure states
        - Resource Management: Tracks token usage and unique sources for optimization
        - Schema Validation: Ensures data consistency through Pydantic model validation

    Workflow Integration:
        The state object flows through the business research pipeline components:
        1. QueryWriter: Updates search_queries and search_focus
        2. WebSearcher: Populates source_str and unique_sources
        3. NoteTaker: Extracts structured data into notes attribute
        4. NoteReviewer: Validates and refines extracted information
        5. Final output: Consolidated in out_info for delivery

    State Persistence:
        All modifications to the state are tracked and preserved throughout the
        research session, enabling resume functionality, debugging, and audit trails.
        Token usage tracking supports cost monitoring and optimization across
        different LLM providers and models.

    Attributes:
        company (Optional[Company]): Company entity information when search_type is 'company'.
            Contains company name and optional email for targeted research.

        is_review_successful (bool): Flag indicating whether the review process
            completed successfully. Used to determine if extracted information
            meets quality standards and research objectives.

        iteration (int): Current iteration number in the research process.
            Supports iterative refinement and tracks research depth for
            complex queries requiring multiple search cycles.

        notes (PersonSchema | CompanySchema | None): Structured extracted information
            from source content. Schema type depends on search_type - PersonSchema
            for person research, CompanySchema for company research.

        out_info (PersonSchema | CompanySchema | None): Final validated and
            reviewed research output. Represents the consolidated, quality-assured
            information ready for delivery to end users.

        person (Optional[Person]): Person entity information when search_type is 'person'.
            Contains person name, optional email, and company affiliation for
            targeted biographical and professional research.

        search_focus (list[str]): Specific areas or topics to focus research efforts.
            Guides query generation and information extraction to ensure
            comprehensive coverage of required information domains.

        search_queries (list[SearchQuery]): Collection of search queries generated
            and executed during the research process. Includes both successful
            and attempted queries for audit and optimization purposes.

        search_type (str): Type of entity being researched - 'person' or 'company'.
            Determines which schemas, templates, and validation rules are applied
            throughout the research workflow.

        source_str (str): Concatenated raw source content from all search results.
            Serves as the primary input for information extraction and includes
            web search results, documents, and other research materials.

        steps (list[str]): Chronological list of processing steps completed.
            Tracks workflow progress, enables debugging, and supports resume
            functionality by identifying completed vs. pending operations.

        token_usage (dict): Comprehensive token consumption tracking by model.
            Structure: {model_name: {'input_tokens': int, 'output_tokens': int}}
            Supports cost monitoring, optimization, and resource planning.

        topic (str): Primary research topic or query description.
            Provides context for search query generation and information
            extraction, ensuring research stays focused on user objectives.

        unique_sources (dict[str, Any]): Deduplicated source information to prevent
            redundant processing. Maps source identifiers to source metadata,
            optimizing search efficiency and reducing unnecessary API calls.

    Example Usage:
        ```python
        # Initialize state for person research
        state = SearchState(
            search_type='person',
            topic='John Smith CEO background',
            person=Person(name='John Smith', company='Tech Corp'),
            search_focus=['career', 'education', 'achievements'],
            iteration=0,
            is_review_successful=False,
            search_queries=[],
            source_str='',
            steps=[],
            token_usage={'gpt-4': {'input_tokens': 0, 'output_tokens': 0}},
            unique_sources={},
            notes=None,
            out_info=None
        )
        ```

    Validation:
        - All attributes are validated through Pydantic BaseModel
        - Optional fields default to None where appropriate
        - Type hints ensure proper data structure throughout workflow
        - Schema objects (PersonSchema/CompanySchema) provide structured validation
    """
    company: Optional[Company] = None
    is_review_successful: bool
    iteration: int
    notes: PersonSchema | CompanySchema | None
    out_info: PersonSchema | CompanySchema | None
    person: Optional[Person] = None
    search_focus: list[str]
    search_queries: list[SearchQuery]
    search_type: str  # 'person' or 'company'
    source_str: str
    steps: list[str]
    token_usage: dict
    topic: str
    unique_sources: dict[str, Any]
