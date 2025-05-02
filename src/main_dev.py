import datetime
import time

from config import settings
from ai_common import Engine
from src.business_researcher import Researcher, SearchType


def main():
    business_researcher = Researcher()
    engine = Engine(responder=business_researcher,
                    models=[settings.LANGUAGE_MODEL],
                    ollama_url=settings.OLLAMA_URL,
                    save_to_folder=settings.OUT_FOLDER)

    input_dict = {
        "name": "Harrison Chase",
        "work_email": "harrison@langchain.dev",
        'search_type': SearchType('person')
    }

    response = engine.get_response(input_dict=input_dict)

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
