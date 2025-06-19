import datetime
import time
import rich

from config import settings
from ai_common import Engine
from src.business_researcher import BusinessResearcher, SearchType
from ai_common import LlmServers


def main():

    llm_server = LlmServers.GROQ

    llm_config = {
        LlmServers.GROQ.value: {
            'model_name': None,
            'groq_api_key': settings.GROQ_API_KEY,
            'language_model': 'llama-3.3-70b-versatile',
            'reasoning_model': 'deepseek-r1-distill-llama-70b',
        },
        LlmServers.OPENAI.value: {
            'model_name': None,
            'openai_api_key': settings.OPENAI_API_KEY,
            'language_model': 'gpt-4.1-2025-04-14',
            'reasoning_model': 'o3',
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

    engine = Engine(
        responder=BusinessResearcher(
            llm_server = llm_server,
            llm_config = llm_config[llm_server.value],
            web_search_api_key = settings.TAVILY_API_KEY
        ),
        llm_server=llm_server,
        models=[settings.LANGUAGE_MODEL, settings.REASONING_MODEL],
        llm_base_url=llm_config[llm_server.value].get('llm_base_url', ''),
        save_to_folder=settings.OUT_FOLDER
    )

    print(f'LLM Server: {llm_server.value}')
    print(f'Language Model: {settings.LANGUAGE_MODEL}')
    print(f'Reasoning Model: {settings.REASONING_MODEL}')
    print('\n\n\n')

    examples = {
        'person': {
            "name": "Ben van Sprundel",
            "company": 'Ben AI',
            'search_type': SearchType('person')
        },
        'company': {
            "name": "Groq",
            'search_type': SearchType('company')
        }
    }

    input_dict = examples['company']
    rich.print(input_dict)

    engine.save_flow_chart(save_to_folder=settings.OUT_FOLDER)
    response = engine.get_response(input_dict=input_dict)
    rich.print(response)

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
