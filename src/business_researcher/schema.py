from .enums import SearchType


PERSON_EXTRACTION_SCHEMA = {
    "description": "Person information",
    "title": "Person",
    "type": "object",
    "required": [
        "linkedin_profile",
        "role",
        "work_email",
        "current_company",
        "companies",
        "years_experience",
    ],
    "properties": {
        "linkedin_profile": {
            "type": "string",
            "description": "Link to the Linkedin profile of the person."
        },
        "role": {
            "type": "string",
            "description": "Current role of the person."
            },
        "work_email": {
            "type": "string",
            "description": "Work email of the person."
        },
        "current_company": {
            "type": "string",
            "description": "The name of the current company the person works at.",
            },
        "companies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of  companies where the person has worked, including the current company",
            },
        "years_experience": {
            "type": "number",
            "description": "Total years of full time work experience (excluding internships) this person has.",
        },
    },
}

COMPANY_EXTRACTION_SCHEMA = {
    "title": "CompanyInfo",
    "description": "Basic information about a company",
    "type": "object",
    "required": [
        "name",
        "description",
        "website",
        "linkedin_url",
        "crunchbase_profile"
        "year_founded",
        "ceo",
        "founder_names",
        "product_description",
        "funding_summary"
    ],
    "properties": {
        "name": {
            "type": "string",
            "description": "Official name of the company",
        },
        "description": {
            "type": "string",
            "description": "Brief overview of the company's products or services",
        },
        "website": {
            "type": "string",
            "description": "Website of the company",
        },
        "linkedin_url": {
            "type": "string",
            "description": "Link to the Linkedin profile of the company."
        },
        "crunchbase_profile": {
            "type": "string",
            "description": "Link to the Crunchbase profile of the company."
        },
        "year_founded": {
            "type": "integer",
            "description": "Year the company was founded",
        },
        "ceo": {
            "type": "string",
            "description": "CEO of the company"
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