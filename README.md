# Business Researcher

An AI-powered business research tool that automates the process of gathering comprehensive information about professionals and companies using web search and LLM-based analysis.

## Overview

Business Researcher is an AI-driven research platform that combines web search capabilities with advanced language models to deliver structured business intelligence. The system uses a multi-agent workflow approach to ensure accuracy and reliability in research outputs.

### Key Capabilities

- **Automated Research Pipeline**: End-to-end automation from query generation to final output
- **Multi-Source Data Integration**: Combines web search and various online sources
- **Quality Assurance**: Built-in validation and review mechanisms for data accuracy
- **Token Usage Tracking**: Cost monitoring and optimization across different LLM providers
- **State-based Workflow**: LangGraph-powered workflow management for complex research tasks
- **Structured Output**: Pydantic-validated schemas for consistent data formats

## Features

### Research Capabilities

**Person Research:**
- **Professional Profile**: LinkedIn profile analysis, current role, and work email discovery
- **Career Intelligence**: Work history, experience timeline, and career progression
- **Contact Information**: Email addresses, phone numbers, and professional contact details
- **Location Data**: Current location, previous locations, and geographic insights
- **Company Affiliations**: Current and past employers, role progression, and organizational context
- **Educational Background**: Academic credentials, certifications, and professional development
- **Achievement Tracking**: Awards, publications, speaking engagements, and notable accomplishments

**Company Research:**
- **Corporate Intelligence**: Official company details, website, LinkedIn, and Crunchbase profiles
- **Leadership Analysis**: C-suite executives, board members, and key personnel identification
- **Product Portfolio**: Comprehensive product and service catalog with market positioning
- **Financial Intelligence**: Funding rounds, investment amounts, valuation history, and financial metrics
- **Market Position**: Competitive analysis, market share, and differentiation factors
- **Organizational Structure**: Department organization, team sizes, and reporting structures
- **Growth Metrics**: Employee count trends, revenue projections, and expansion indicators
- **Partnership Network**: Strategic partnerships, vendor relationships, and business alliances

### Architecture

Built using **LangGraph** as a state-based workflow orchestrator with a sophisticated multi-step research pipeline:

1. **Query Writer** - Generates optimized, contextual search queries based on research objectives
2. **Web Search** - Executes comprehensive searches using Tavily API with intelligent source selection
3. **Note Taker** - Extracts structured information from search results using schema-validated LLM processing
4. **Note Reviewer** - Validates, refines, and enhances extracted data with iterative quality improvement
5. **LinkedIn Finder** - Specialized LinkedIn profile discovery and validation component
6. **Routing Logic** - Intelligent workflow routing based on research progress and quality metrics

### Data Processing Pipeline

The system employs a sophisticated data processing approach:

- **Source Deduplication**: Prevents redundant processing of identical sources
- **Content Aggregation**: Intelligent merging of information from multiple sources
- **Schema Validation**: Pydantic-based validation ensures data structure consistency
- **Quality Scoring**: Automated assessment of information completeness and reliability
- **Iterative Refinement**: Multi-pass processing for enhanced accuracy and detail

## Technical Stack

### Core Frameworks
- **LangGraph**: Advanced workflow orchestration and state management
- **LangChain**: LLM integrations, model abstraction, and chain composition
- **Pydantic**: Data validation, serialization, and structured outputs
- **Rich**: Enhanced console output formatting and progress visualization

### External Services
- **Tavily**: Professional web search API for real-time information gathering

### Development Tools
- **uv**: Fast Python package management and dependency resolution
- **Makefile**: Automated build and development workflow management
- **Type Hints**: Comprehensive type annotations for better code reliability

## Supported LLM Providers

### Production-Ready Providers
- **Groq**: 
  - Llama-3.3-70b-versatile (high performance, cost-effective)
  - DeepSeek-R1-distill (reasoning-optimized model)
- **OpenAI**: 
  - GPT-4.1 (high accuracy, comprehensive reasoning)
  - O3 reasoning model (advanced problem-solving capabilities)

### Development and Testing
- **vLLM**: Custom model endpoints for specialized use cases
- **Ollama**: Local model deployment for development and testing

### Model Selection Guidance
- **Groq Llama-3.3-70b**: Recommended for cost-effective, high-volume research
- **DeepSeek-R1**: Optimal for research tasks requiring deep analytical thinking
- **OpenAI GPT-4.1**: Best for complex reasoning and high-accuracy requirements

## Installation

### Prerequisites
- Python 3.11 or higher
- Git for repository cloning
- API keys for required services (Groq/OpenAI, Tavily)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/bgunyel/business-researcher.git
cd business-researcher

# Install dependencies using uv (recommended)
uv sync --upgrade

# Alternative: Use Makefile for dependency management
make sync
```

## Configuration

### Environment Variables

Set up your API keys as environment variables:

```bash
# Required API Keys
export GROQ_API_KEY="your-groq-api-key"
export OPENAI_API_KEY="your-openai-api-key" 
export TAVILY_API_KEY="your-tavily-api-key"
```

### Environment File

Create a `.env` file with your API keys:

```bash
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
```

### Required API Keys and Setup

#### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create account and generate API key
3. Set `GROQ_API_KEY` environment variable

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Generate API key in your account settings
3. Set `OPENAI_API_KEY` environment variable

#### Tavily API Key
1. Visit [Tavily](https://tavily.com/)
2. Sign up for API access
3. Set `TAVILY_API_KEY` environment variable

## Usage

```python
import asyncio
from business_researcher import BusinessResearcher
from business_researcher.state import SearchState, Person, Company
from business_researcher.enums import SearchType
from config import settings

# Custom LLM configuration
llm_config = {
        'language_model': {
            'model': 'llama-3.3-70b-versatile',
            'model_provider': LlmServers.GROQ.value,
            'api_key': settings.GROQ_API_KEY,
            'model_args': {
                'temperature': 0,
                'max_retries': 5,
                'max_tokens': 32768,
                'model_kwargs': {
                    'top_p': 0.95,
                    'service_tier': "auto",
                }
            }
        },
        'reasoning_model': {
            'model': 'deepseek-r1-distill-llama-70b',
            'model_provider': LlmServers.GROQ.value,
            'api_key': settings.GROQ_API_KEY,
            'model_args': {
                'temperature': 0,
                'max_retries': 5,
                'max_tokens': 32768,
                'model_kwargs': {
                    'top_p': 0.95,
                    'service_tier': "auto",
                }
            }
        }
    }
    
# Custom research configuration
config = {
        "configurable": {
            'thread_id': str(uuid4()),
            'max_iterations': 3,
            'max_results_per_query': 4,
            'max_tokens_per_source': 10000,
            'number_of_days_back': 1e6,
            'number_of_queries': 3,
            'search_category': 'general',
        }
    }

# Initialize with custom LLM config
researcher = BusinessResearcher(
    llm_config=llm_config,
    web_search_api_key="your-tavily-key",
)

# Detailed person research
person = {
    	"name": "Jane Smith",
    	"company": "Innovation Labs",
    	"search_type": SearchType.PERSON,
	}

# Execute the research
event_loop = asyncio.new_event_loop()
out_dict = event_loop.run_until_complete(business_researcher.run(input_dict=person, config=config))
event_loop.close()
```

## Output Schema

### Person Research Output

```json
{
  "name": "John Doe",
  "linkedin": "https://linkedin.com/in/johndoe",
  "role": "Senior Software Engineer",
  "work_email": "john.doe@techcorp.com",
  "current_location": "San Francisco, CA",
  "company": "Tech Corp",
  "work_history": [
    {
      "company": "Tech Corp",
      "role": "Senior Software Engineer",
      "duration": "2021-Present",
      "description": "Lead developer for cloud infrastructure"
    }
  ],
  "years_of_experience": 8,
  "contact_info": {
    "email": "john.doe@techcorp.com",
    "phone": "+1-555-0123"
  },
  "education": "BS Computer Science, Stanford University",
  "skills": ["Python", "AWS", "Kubernetes"],
  "achievements": ["AWS Certified Solutions Architect"]
}
```

### Company Research Output

```json
{
  "name": "Tech Corp",
  "website": "https://techcorp.com",
  "linkedin": "https://linkedin.com/company/techcorp",
  "crunchbase": "https://crunchbase.com/organization/techcorp",
  "leadership": [
    {
      "name": "Alice Johnson",
      "role": "CEO",
      "linkedin": "https://linkedin.com/in/alicejohnson"
    }
  ],
  "products_services": [
    "Cloud Infrastructure Platform",
    "DevOps Automation Tools"
  ],
  "company_overview": "Leading provider of cloud infrastructure solutions",
  "funding_info": {
    "total_funding": "$50M",
    "latest_round": "Series B",
    "latest_amount": "$25M",
    "latest_date": "2023-06-15",
    "investors": ["Venture Capital Firm A", "Angel Investor Group"]
  },
  "employee_count": "150-200",
  "industry": "Cloud Computing",
  "founded_year": 2018,
  "headquarters": "San Francisco, CA"
}
```

## Project Structure

```
business-researcher/
├── Makefile                     # Build and dependency management
├── pyproject.toml              # Project configuration and dependencies
├── uv.lock                     # Dependency lock file
├── .env                        # Environment variables (create this)
├── out/                        # Output directory for research results
└── src/
    ├── business_researcher/
    │   ├── components/              # Individual processing components
    │   │   ├── query_writer.py      # Search query generation
    │   │   ├── note_taker.py        # Information extraction
    │   │   ├── note_reviewer.py     # Quality validation
    │   │   ├── linkedin_finder.py   # LinkedIn profile validation
    │   │   ├── routing.py           # Workflow routing logic
    │   │   └── utils.py             # Utility functions
    │   ├── researcher.py            # Main orchestrator class
    │   ├── schema.py               # Data models and validation
    │   ├── state.py                # Workflow state management
    │   ├── enums.py                # Type definitions
    │   ├── configuration.py        # Configuration management
    │   └── __init__.py             # Package initialization
    ├── config.py                   # Global configuration
    └── main_dev.py                 # Development entry point
```

## Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/bgunyel/business-researcher
cd business-researcher
uv sync --upgrade

# Create environment file with your API keys
cp .env.example .env  # Create .env file if it doesn't exist
# Edit .env with your API keys
```

### Code Quality

The project maintains high code quality standards:

- **Type Hints**: Comprehensive type annotations throughout codebase
- **Pydantic Validation**: Structured data validation for all inputs/outputs
- **Code Formatting**: Consistent code style
- **Documentation**: Detailed docstrings and comprehensive README

## Performance Features

- **Token Usage Tracking**: Smart token usage tracking and optimization
- **Source Deduplication**: Prevents redundant processing of identical sources
- **Iterative Refinement**: Multi-pass processing for enhanced accuracy

## Troubleshooting

### Common Issues

**API Key Issues:**
```bash
# Verify API keys are set
echo $GROQ_API_KEY
echo $TAVILY_API_KEY

# Test API connectivity
python -c "import os; from groq import Groq; print(Groq(api_key=os.getenv('GROQ_API_KEY')).models.list())"
```

**Installation Issues:**
```bash
# Clear uv cache
uv cache clean

# Reinstall dependencies
rm uv.lock
uv sync --upgrade
```

**Research Quality Issues:**
- Check API key configuration
- Verify internet connectivity
- Review search query parameters

## License

This project is licensed under the MIT License.
