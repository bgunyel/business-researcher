# Business Researcher

An AI-powered business research tool that automates the process of gathering comprehensive information about professionals and companies using web search and LLM-based analysis.

## Features

### Research Capabilities

**Person Research:**
- LinkedIn profile, role, and work email
- Current location and company
- Work history and years of experience
- Contact information and career trajectory

**Company Research:**
- Official details (website, LinkedIn, Crunchbase)
- Leadership team and organizational structure
- Products, services, and company overview
- Funding information (rounds, amounts, dates)
- Distinguishing features from similar companies

### Architecture

Built using **LangGraph** as a state-based workflow orchestrator with a multi-step research pipeline:

1. **Query Writer** - Generates optimized search queries based on input
2. **Web Search** - Executes searches using Tavily API integration
3. **Note Taker** - Extracts structured information from search results
4. **Note Reviewer** - Validates and refines extracted data with iterative improvement

## Technical Stack

- **LangGraph**: Workflow orchestration and state management
- **LangChain**: LLM integrations and model abstraction
- **Tavily**: Web search API for real-time information
- **Pydantic**: Data validation and structured outputs
- **Rich**: Enhanced console output formatting

## Supported LLM Providers

- **Groq**: Llama-3.3-70b-versatile, DeepSeek-R1-distill
- **OpenAI**: GPT-4.1, O3 reasoning model
- **vLLM**: Custom model endpoints
- **Ollama**: Local model deployment

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd business-researcher

# Install dependencies using uv
uv sync
```

## Configuration

Set up your API keys in the configuration:
- `GROQ_API_KEY` - For Groq LLM access
- `OPENAI_API_KEY` - For OpenAI models
- `TAVILY_API_KEY` - For web search functionality

## Usage

```python
from business_researcher import BusinessResearcher, SearchType
from ai_common import LlmServers

# Initialize the researcher
researcher = BusinessResearcher(
    llm_server=LlmServers.GROQ,
    llm_config=llm_config,
    web_search_api_key=tavily_api_key
)

# Research a person
person_input = {
    "name": "John Doe",
    "company": "Tech Corp",
    "search_type": SearchType.PERSON
}

# Research a company
company_input = {
    "name": "Techy Tech Studios",
    "search_type": SearchType.COMPANY
}

# Get results
results_for_person = researcher.get_response(person_input)
results_for_company = researcher.get_response(company_input)
```

## Project Structure

```
src/
├── business_researcher/
│   ├── components/          # Individual processing components
│   │   ├── query_writer.py  # Search query generation
│   │   ├── note_taker.py    # Information extraction
│   │   ├── note_reviewer.py # Quality validation
│   │   └── routing.py       # Workflow routing logic
│   ├── researcher.py        # Main orchestrator class
│   ├── schema.py           # Data models and validation
│   ├── state.py            # Workflow state management
│   └── enums.py            # Type definitions
└── main_dev.py             # Development entry point
```

## License

This project is licensed under the MIT License.