from .enums import SearchType


PERSON_EXTRACTION_SCHEMA = {
    "description": "Person information",
    "title": "Person",
    "type": "object",
    "required": [
        "years_experience",
        "current_company",
        "role",
        "prior_companies",
    ],
    "properties": {
        "role": {"type": "string", "description": "Current role of the person."},
        "years_experience": {
            "type": "number",
            "description": "How many years of full time work experience (excluding internships) does this person have.",
        },
        "current_company": {
            "type": "string",
            "description": "The name of the current company the person works at.",
        },
        "prior_companies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of previous companies where the person has worked",
        },
    },
}

COMPANY_EXTRACTION_SCHEMA = {
    "title": "CompanyInfo",
    "description": "Basic information about a company",
    "type": "object",
    "required": ["company_name"],
    "properties": {
        "company_name": {
            "type": "string",
            "description": "Official name of the company",
        },
        "founding_year": {
            "type": "integer",
            "description": "Year the company was founded",
        },
        "founder_names": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Names of the founding team members",
        },
        "product_description": {
            "type": "string",
            "description": "Brief description of the company's main product or service",
        },
        "funding_summary": {
            "type": "string",
            "description": "Summary of the company's funding history",
        },
    },
}

data_extraction_schema = {
    SearchType.PERSON.value: PERSON_EXTRACTION_SCHEMA,
    SearchType.COMPANY.value: COMPANY_EXTRACTION_SCHEMA,
}