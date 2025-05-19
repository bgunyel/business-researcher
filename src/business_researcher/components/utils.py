from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from openai import OpenAI


from ..state import SearchState
from ..enums import SearchType, LlmServers


def generate_info_str(state: SearchState):
    match state.search_type:
        case SearchType.PERSON.value:
            search_object = state.person
        case SearchType.COMPANY.value:
            search_object = state.company
        case _:
            raise ValueError('Invalid search type!')

    info_str = ''
    for attr in search_object.model_dump().keys():
        info_str += f'{attr.upper()}: {search_object.model_dump()[attr]}\n' if search_object.model_dump()[attr] is not None else ''

    return info_str


def get_llm(llm_server: LlmServers, model_params: dict[str, Any]) -> BaseChatModel:
    llm_base_url = model_params.get('llm_base_url', '')

    match llm_server:
        case LlmServers.GROQ:
            llm = ChatGroq(
                model=model_params['model_name'],
                temperature=0,
                api_key=model_params['groq_api_key'],
            )
        case LlmServers.OLLAMA:
            llm = ChatOllama(
                model=model_params['model_name'],
                temperature=0,
                base_url=llm_base_url,
                format=model_params['format'],
                num_ctx=model_params['context_window_length'],
            )
        case LlmServers.VLLM:
            client = OpenAI(base_url=f'{llm_base_url}/v1', api_key=model_params['vllm_api_key'])
            max_model_len = client.models.list().data[0].model_extra['max_model_len']  # Keep this
            llm = ChatOpenAI(api_key=model_params['vllm_api_key'],
                             model=client.models.list().data[0].id,
                             temperature=0,
                             base_url=f'{llm_base_url}/v1')
        case _:
            raise ValueError(f'LLM Server {llm_server.value} is currently not supported!')
    return llm
