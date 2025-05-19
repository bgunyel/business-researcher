import datetime
import time

from config import settings
from ai_common import Engine
from src.business_researcher import BusinessResearcher, SearchType
from src.business_researcher.enums import LlmServers

from openai import OpenAI
from langchain_openai import ChatOpenAI


def main():

    """
    engine = Engine(
        responder=BusinessResearcher(
            model_name=settings.LANGUAGE_MODEL,
            llm_base_url=settings.LLM_BASE_URL,
            web_search_api_key=settings.TAVILY_API_KEY
        ),
        models=[settings.LANGUAGE_MODEL],
        ollama_url=settings.LLM_BASE_URL,
        save_to_folder=settings.OUT_FOLDER
    )
    """

    llm_server = LlmServers.GROQ

    llm_config = {
        LlmServers.GROQ.value: {
            'model_name': None,
            'groq_api_key': settings.GROQ_API_KEY,
            'language_model': settings.LANGUAGE_MODEL,
            'reasoning_model': settings.REASONING_MODEL,
        },
        LlmServers.VLLM.value: {
            'llm_base_url': None,
            'vllm_api_key': None
        },
        LlmServers.OLLAMA.value: {
            'model_name': None,
            'llm_base_url': None,
            'format': None,  # Literal['', 'json']
            'context_window_length': None,
        }
    }

    researcher = BusinessResearcher(llm_server = llm_server,
                                    llm_config = llm_config[llm_server.value],
                                    web_search_api_key = settings.TAVILY_API_KEY)

    print(f'LLM Server: {llm_server.value}')
    print(f'Language Model: {settings.LANGUAGE_MODEL}')
    print(f'Reasoning Model: {settings.REASONING_MODEL}')

    input_dict = {
        'person': {
            "name": "Harrison Chase",
            "email": "harrison@langchain.dev",
            'search_type': SearchType('person')
        },
        'company': {
            "name": "LangChain",
            'search_type': SearchType('company')
        }
    }

    out = researcher.get_response(input_dict=input_dict['company'])
    # engine.save_flow_chart(save_to_folder=settings.OUT_FOLDER)
    # response = engine.get_response(input_dict=input_dict['person'])

    dummy = -32



if __name__ == '__main__':
    time_now = datetime.datetime.now().replace(microsecond=0).astimezone(
        tz=datetime.timezone(offset=datetime.timedelta(hours=3), name='UTC+3'))

    print(f'{settings.APPLICATION_NAME} started at {time_now}')
    time1 = time.time()
    main()
    time2 = time.time()

    time_now = datetime.datetime.now().replace(microsecond=0).astimezone(
        tz=datetime.timezone(offset=datetime.timedelta(hours=3), name='UTC+3'))
    print(f'{settings.APPLICATION_NAME} finished at {time_now}')
    print(f'{settings.APPLICATION_NAME} took {(time2 - time1):.2f} seconds')
