from pydantic import BaseModel, Field


class PersonSchema(BaseModel):
    name: str = Field(description="Name and surname of the person")
    linkedin_profile: str = Field(description="Linkedin profile URL of the person")
    role: str = Field(description="Role of the person in his/her current company")
    work_email: str = Field(description="Work email of the person")
    current_location: str = Field(description="Current location of the person")
    current_company: str = Field(description="The name of the current company the person works at")
    companies: list[str] = Field(description="ist of  companies where the person has worked, including the current company")
    years_experience: str = Field(
        description="Total number of years of full time work experience (excluding internships) this person has. Only the number, no explanation."
    )


class CompanySchema(BaseModel):
    name: str = Field(description="Official name of the company")
    is_verified: bool = Field(description="Confirmation whether this is the intended company, not a similarly named one")
    website: str = Field(description="Company's official website URL")
    linkedin_profile: str = Field(description="Linkedin URL of the company")
    crunchbase_profile: str = Field(description="Crunchbase profile URL of the company")
    address: str = Field(description="Company's official address")
    similar_companies: list[str] = Field(description="List of similarly named companies that could be confused with the target")
    distinguishing_features: str = Field(description="Key features that distinguish this company from similarly named ones")
    ceo: str = Field(description="Name of the CEO of the company")
    key_executives: list[str] = Field(description="Key executive people in the company. Only names and surnames, no titles")
    org_chart_summary: str = Field(description="Brief description of organizational structure")
    main_products: list[str] = Field(description="List of main products available in the company")
    services: list[str] = Field(description="List of services available in the company")
    company_summary: str = Field(description="Summary of the most important company information")
    year_founded: str = Field(description="Year when the company was founded")
    total_funding_mm_usd: str = Field(description="Total funding raised in millions of USD")
    latest_funding_round: str = Field(description="Type of the most recent funding round (e.g., Series A, Seed, Debt, etc.)")
    latest_funding_round_date: str = Field(description="Date of the most recent funding round (YYYY-MM-DD)")
    latest_funding_round_amount_mm_usd: str = Field(description="Amount raised in the most recent funding round in millions of USD")
