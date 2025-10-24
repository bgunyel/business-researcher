import os
import asyncio
import datetime
import time
import rich
from uuid import uuid4

from langchain_core.runnables import RunnableConfig

from config import settings
from src.business_researcher import BusinessResearcher, SearchType
from ai_common import LlmServers, calculate_token_cost


def main():
    os.environ['LANGSMITH_API_KEY'] = settings.LANGSMITH_API_KEY
    os.environ['LANGSMITH_TRACING'] = settings.LANGSMITH_TRACING

    llm_config = {
        'language_model': {
            'model': 'llama-3.3-70b-versatile',
            'model_provider': LlmServers.GROQ.value,
            'api_key': settings.GROQ_API_KEY,
            'max_llm_retries': 3,
            'model_args': {
                'service_tier': "auto",
                'temperature': 0,
                'max_retries': 5,
                'max_tokens': 32768,
                'model_kwargs': {
                    'top_p': 0.95,
                }
            }
        },
        'reasoning_model': {
            'model': 'openai/gpt-oss-120b',  # 'qwen/qwen3-32b',  # 'deepseek-r1-distill-llama-70b',
            'model_provider': LlmServers.GROQ.value,
            'api_key': settings.GROQ_API_KEY,
            'max_llm_retries': 3,
            'model_args': {
                'service_tier': "auto",
                'temperature': 0,
                'max_retries': 5,
                'max_tokens': 65536,  # for deepseek and qwen3: 32768,
                'reasoning_effort': 'medium',  # only for gpt-oss models: ['high', 'medium', 'low']
                'model_kwargs': {
                    'top_p': 0.95,
                }
            }
        }
    }

    language_model = llm_config['language_model'].get('model', '')
    reasoning_model = llm_config['reasoning_model'].get('model', '')

    config = RunnableConfig(
        recursion_limit=100,
        configurable = {
            'thread_id': str(uuid4()),
            'max_iterations': 5,
            'max_results_per_query': 5,
            'max_tokens_per_source': 10000,
            'number_of_days_back': 360,
            'number_of_queries': 3,
            'search_depth': 'advanced',
            },
        )



    print(f'Language Model: {language_model}')
    print(f'Reasoning Model: {reasoning_model}')
    print('\n\n')

    business_researcher = BusinessResearcher(llm_config = llm_config, web_search_api_key = settings.TAVILY_API_KEY)

    examples = {
        'person': {
            "name": "William Gaybrick",
            "company": 'Stripe',
            'search_type': SearchType.PERSON
        },
        'company': {
            "name": "Stripe",
            'search_type': SearchType.COMPANY
        }
    }

    input_dict = examples['company']
    rich.print(input_dict)

    event_loop = asyncio.new_event_loop()
    out_dict = event_loop.run_until_complete(business_researcher.run(input_dict=input_dict, config=config))
    event_loop.close()

    rich.print(out_dict['content'])

    cost_list, total_cost = calculate_token_cost(llm_config=llm_config, token_usage=out_dict['token_usage'])
    print(f'Total Token Usage Cost: {total_cost:.4f} USD')
    for item in cost_list:
        print(f"\t* {item['model_provider']}: {item['model']} --> {item['cost']:.4f} USD")

    print('\n\n\n')


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
