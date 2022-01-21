import requests
from requests.exceptions import ReadTimeout
from requests.models import Response
from typing import Optional, Dict, Union, List


def make_get_request(
    entrypoint: str,
    method: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Union[str, List[str]]]] = None
) -> Response:
    """
    Посылает GET запрос на сервер.
    Возвращает ответ сервера.
    Выставлен таймаут запроса 15 секунд.
    Таймаут был увеличен с 10 до 15 секунд из-за рефакторинга метода GET / scoring/time-slots

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param method: тестируемый API-метод
    :type: String

    :param headers: хэдерсы запроса с bearer-токеном авторизации
    :type: Dictionary

    :param params: опциональный параметр get-запроса
    :type: Dictionary

    :return: возвращает объект Response - ответ сервера.
    :rtype: Response
    """
    try:
        response = requests.get(
            f'{entrypoint}{method}',
            params=params,
            headers=headers,
            verify=False,
            timeout=15,
        )
    except ReadTimeout:
        pytest.fail('Время установки соединения превышает предельно допустимое значение')

    return response


def get_total_regions_count(entrypoint: str, method: str) -> int:
    """
    Утилита получения общего числа регионов в системе

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param method: тестируемый API-метод
    :type: String

    :return: число элементов в системе.
    :rtype: Integer
    """
    response = make_get_request(entrypoint, method)

    return response.json()['total']


def get_total_page_count(entrypoint: str, method: str) -> int:
    """
    Утилита получения общего числа страниц с регионами в системе.

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param method: тестируемый API-метод
    :type: String

    :return: число страниц с регионами в системе.
    :rtype: Integer
    """
    current_page = 1
    page_count = 0

    while True:
        params = f'?page={current_page}'
        method_with_params = ''.join([method, params])

        response = make_get_request(entrypoint, method_with_params)

        if response.json()['items']:
            page_count +=1
            current_page +=1

        else:
            return page_count


def get_all_regions(entrypoint: str, method: str) -> List[Dict[str, Union[int, str, Dict[str, str]]]]:
    """
    Утилиа для получения всех регионов.

    :return: возвращает число список всех регионов.
    :rtype: List
    """
    current_page = 1
    all_regions = []

    while True:
        params = f'?page={current_page}'
        method_with_params = ''.join([method, params])

        response = make_get_request(entrypoint, method_with_params)

        if response.json()['items']:
            all_regions.extend(response.json()['items'])
            current_page +=1

        else:
            return all_regions
