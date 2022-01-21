import json
from typing import Dict
import urllib3

import pytest

from kopilov_regions_proj.settings import URL


@pytest.fixture(scope='session', autouse=True)
def disable_request_warnings():
    """
    Отключает варнинги со стороны urllib3 для работы requests по протоколу https.
    Почитать тут: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@pytest.fixture(scope='session')
def entrypoint() -> str:
    """
    Фикстура получения точки входа для апи-запросов.

    :return: возвращает entrypoint для апи-запросов.
    :rtype: String
    """
    return URL


@pytest.fixture(scope='module')
def get_regions_in_array_schema() -> Dict:
    """
    Модульная фикстура, возвращающая открытую схему account_in_array_schema.
    """
    with open('./testdata/regions_schema.json', 'r', encoding='utf-8') as f:
        schema = json.load(f)

        yield schema
