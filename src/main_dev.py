import datetime
import time
import rich

from config import settings
from ai_common import Engine
from src.business_researcher import BusinessResearcher, SearchType
from ai_common import LlmServers


def main():
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

    language_model = llm_config['language_model'].get('model', '')
    reasoning_model = llm_config['reasoning_model'].get('model', '')

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
