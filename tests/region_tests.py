import json
from typing import NoReturn, Dict

from jsonschema import validate, ValidationError
import pytest

from kopilov_regions_proj.utils import make_get_request, get_all_regions, get_total_regions_count, get_total_page_count

METHOD = 'regions'


def test_all_regions_validate(entrypoint: str, get_regions_in_array_schema: Dict) -> NoReturn:
    """
    Автотест валидации всех регионов системы по json-схеме.

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param get_regions_in_array_schema: json-схема для валидации элементов
    :type: Dict
    """
    total_page_count = get_total_page_count(entrypoint, METHOD)

    for page in range(1, total_page_count):
        params = f'?page={page}'
        method_with_params = ''.join([METHOD, params])

        response = make_get_request(entrypoint, method_with_params)

        try:
            validate(response.json(), schema=get_regions_in_array_schema)
        except ValidationError as e:
            pytest.fail('Ошибка при валидации ответа')

        assert response.status_code == 200
        assert response.ok


@pytest.mark.xfail(reason='Ошибка в общем числе элементов и параметре total_count')
def test_regions_total_count(entrypoint: str) -> NoReturn:
    """
    Автотест проверки соответствия общего количества регионов и параметра total-count.

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String
    """
    total_regions_count = get_total_regions_count(entrypoint, METHOD)
    list_of_regions = get_all_regions(entrypoint, METHOD)

    assert len(
        list_of_regions) == total_regions_count, f'Общее число элементов {len(list_of_regions)} не соответствует параметру total_count: {total_regions_count}'


@pytest.mark.parametrize('pattern', ['новос', 'НОВОС', 'рск', 'РСК'])
def test_pattern_search_region(entrypoint: str, pattern: str) -> NoReturn:
    """
    Автотест поиска региона по строке-шаблону.

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param pattern: подстрока, по которой производится поиск
    :type: String
    """
    param = f'?q={pattern}'
    method_with_params = ''.join([METHOD, param])

    response = make_get_request(entrypoint, method_with_params)

    items_list = response.json()['items']

    for item in items_list:
        assert pattern.lower() in item['name'].lower()


@pytest.mark.xfail(reason='Некорректная фильтрация по коду kg')
def test_search_region_by_code(entrypoint: str) -> NoReturn:
    """
    Автотест фильтрации регионов по коду страны.

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String
    """
    country_codes = ('ru', 'kg', 'kz', 'cz')

    for code in country_codes:
        param = f'?country_code={code}'
        method_with_params = ''.join([METHOD, param])

        response = make_get_request(entrypoint, method_with_params)

        list_of_regions = response.json()['items']

        for region in list_of_regions:
            # breakpoint()

            assert region['country']['code'] == code, f'Некорректная фильтрация для country_code: {code}'


def test_get_regions_by_page(entrypoint: str) -> NoReturn:
    """
    Автотест количества элементов на странице (значение параметра по умолчанию).

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String
    """
    param_page_1 = f'?page=1'
    param_page_2 = f'?page=2'

    method_with_param_page_1 = ''.join([METHOD, param_page_1])
    method_with_param_page_2 = ''.join([METHOD, param_page_2])

    response_page_1 = make_get_request(entrypoint, method_with_param_page_1)
    response_page_2 = make_get_request(entrypoint, method_with_param_page_2)

    page_1_items = response_page_1.json()['items']
    page_2_items = response_page_2.json()['items']

    assert page_1_items != page_2_items


@pytest.mark.xfail(reason='Количество элементов по умолчанию не соответствует 15')
def test_page_size_default_value(entrypoint: str) -> NoReturn:
    """
    Автотест количества элементов на странице (значение параметра по умолчанию).

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String
    """
    DEFAULT_SIZE = 15

    response = make_get_request(entrypoint, METHOD)
    list_of_regions = response.json()['items']

    assert len(list_of_regions) == DEFAULT_SIZE


@pytest.mark.parametrize('page_size', [5, 10, 15])
def test_valid_page_size_param(entrypoint: str, page_size: int) -> NoReturn:
    """
    Автотест количества элементов на странице (позитивный кейс).

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param page_size: количество объектов, единовременно отображаемое на странице
    :type: Integer
    """
    param = f'?page_size={page_size}'
    method_with_params = ''.join([METHOD, param])

    response = make_get_request(entrypoint, method_with_params)

    list_of_regions = response.json()['items']

    assert len(list_of_regions) == page_size


@pytest.mark.parametrize('page_size', [-1, 0, 7])
def test_invalid_page_size_param(entrypoint: str, page_size: int) -> NoReturn:
    """
    Автотест количества элементов на странице (негативный кейс)

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param page_size: количество объектов, единовременно отображаемое на странице
    :type: Integer
    """
    error_msg = "Параметр 'page_size' может быть одним из следующих значений: 5, 10, 15"

    param = f'?page_size={page_size}'
    method_with_params = ''.join([METHOD, param])

    response = make_get_request(entrypoint, method_with_params)

    assert response.json()['error']['message'] == error_msg


@pytest.mark.parametrize('page_size', [-1.2, 0.0, 7.1])
def test_decimal_page_size(entrypoint: str, page_size: int) -> NoReturn:
    """
    Автотест количества элементов на странице (негативный кейс)

    :param entrypoint: точка входа, на которую делается апи-запрос
    :type: String

    :param page_size: количество объектов, единовременно отображаемое на странице
    :type: Integer
    """
    error_msg = "Параметр 'page_size' длжен быть целым числом"

    param = f'?page_size={page_size}'
    method_with_params = ''.join([METHOD, param])
    response = make_get_request(entrypoint, method_with_params)

    assert response.json()['error']['message'] == error_msg
