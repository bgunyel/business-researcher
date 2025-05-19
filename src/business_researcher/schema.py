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
  "title": "Company Info",
  "description": "Comprehensive information about a company",
  "type": "object",
  "properties": {
    "company_name": {
      "type": "string",
      "description": "Official name of the company"
    },
    "verified_company": {
      "type": "boolean",
      "description": "Confirmation whether this is the intended company, not a similarly named one"
    },
    "website": {
      "type": "string",
      "format": "uri",
      "description": "Company's official website URL",
    },
    "linkedin_url": {
      "type": "string",
      "format": "uri",
      "description": "URL of the company LinkedIn profile",
    },
    "crunchbase_profile": {
      "type": "string",
      "format": "uri",
      "description": "Company's Crunchbase profile URL",
    },
    "similar_companies": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of similarly named companies that could be confused with the target"
    },
    "distinguishing_features": {
      "type": "string",
      "description": "Key features that distinguish this company from similarly named ones"
    },
    "ceo": {
      "type": "string",
      "description": "Name of the company's CEO"
    },
    "key_executives": {
      	"type": "array",
    	"items": {"type": "string"},
    	"description": "Key executive people in the company. Only names and surnames, no titles",
    },
    "org_chart_summary": {
      "type": "string",
      "description": "Brief description of organizational structure"
    },
    "main_products": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Main products of the company",
    },
    "services": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Main services of the company",
    },
    "company_summary": {
      "type": "string",
      "description": "Concise, dense summary of the most important company information (max 250 words)"
    },
    "year_founded": {
      "type": "integer",
      "minimum": 1800,
      "description": "Year when the company was founded",
    },
    "total_funding_mm_usd": {
      "type": "number",
      "minimum": 0,
      "description": "Total funding raised in millions of USD",
    },
    "latest_funding_round": {
      "type": "string",
      "description": "Type of the most recent funding round (e.g., Series A, Seed, etc.)",
    },
    "latest_funding_round_date": {
      "type": "string",
      "format": "date",
      "description": "Date of the most recent funding round (YYYY-MM-DD)",
    },
    "latest_funding_round_amount_mm_usd": {
      "type": "number",
      "minimum": 0,
      "description": "Amount raised in the most recent funding round in millions of USD",
    },
  },
  "required": [
    "company_name",
    "verified_company",
    "website",
    "linkedin_url",
    "crunchbase_profile",
    "similar_companies",
    "distinguishing_features",
    "ceo",
    "key_executives",
    "org_chart_summary",
    "main_products",
    "services",
    "company_summary",
    "year_founded",
    "total_funding_mm_usd",
    "latest_funding_round",
    "latest_funding_round_date",
    "latest_funding_round_amount_mm_usd",
  ]
}



"""
COMPANY_EXTRACTION_SCHEMA = {
    "type": "object",
    "title": "company_info",
    "properties": {
        "name": {
            "type": "string",
            "description": "Official company name"
        },
        "description": {
            "type": "string",
            "description": "Concise, dense summary of the most important company information (max 250 words)",
        },
        "website": {
            "type": "string",
            "format": "uri",
            "description": "Company's official website URL",
        },
        "linkedin_url": {
            "type": "string",
            "format": "uri",
            "description": "URL of the company LinkedIn profile",
        },
        "crunchbase_profile": {
            "type": "string",
            "format": "uri",
            "description": "Company's Crunchbase profile URL",
        },
        "year_founded": {
            "type": "integer",
            "minimum": 1800,
            "description": "Year when the company was founded",
        },
        "ceo": {
            "type": "string",
            "description": "Name of the company's CEO"
        },
        "total_funding_mm_usd": {
            "type": "number",
            "minimum": 0,
            "description": "Total funding raised in millions of USD",
        },
        "latest_round": {
            "type": "string",
            "description": "Type of the most recent funding round (e.g., Series A, Seed, etc.)",
        },
        "latest_round_date": {
            "type": "string",
            "format": "date",
            "description": "Date of the most recent funding round (YYYY-MM-DD)",
        },
        "latest_round_amount_mm_usd": {
            "type": "number",
            "minimum": 0,
            "description": "Amount raised in the most recent funding round in millions of USD",
        },
    },
    "required": [
        "name",
        "description",
        "website",
        "linkedin_url",
        "crunchbase_profile",
        "year_founded",
        "ceo",
        "total_funding_mm_usd",
        "latest_round",
        "latest_round_date",
        "latest_round_amount_mm_usd",
    ],
    "description": "Company information",
}

"""

data_extraction_schema = {
    SearchType.PERSON.value: PERSON_EXTRACTION_SCHEMA,
    SearchType.COMPANY.value: COMPANY_EXTRACTION_SCHEMA,
}