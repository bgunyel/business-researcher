import os
from pydantic_settings import BaseSettings
from pydantic import SecretStr

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_DIR = os.path.abspath(os.path.join(FILE_DIR, os.pardir))


class Settings(BaseSettings):
    APPLICATION_NAME: str = "Business Researcher"

    ANTHROPIC_API_KEY: SecretStr = ""
    GROQ_API_KEY: SecretStr = ""
    LANGSMITH_API_KEY: SecretStr = ""
    LANGSMITH_TRACING: str = "false"
    OLLAMA_API_KEY: SecretStr = ""
    OPENAI_API_KEY: SecretStr = ""
    SUPABASE_URL: SecretStr = ""
    SUPABASE_SECRET_KEY: SecretStr = ""
    TAVILY_API_KEY: SecretStr = ""

    LLM_BASE_URL: SecretStr = ""
    VLLM_API_KEY: SecretStr = ""

    OUT_FOLDER: str = os.path.join(ENV_FILE_DIR, 'out')

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"
        env_file = os.path.join(ENV_FILE_DIR, '.env')

settings = Settings()
