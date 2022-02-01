import requests
import json
from typing import Dict, List, Any, Optional, Union

from decouple import config

from .regular_expressions import remove_tags
from .log import my_log, logger


@my_log
def search_city(searching_city: str) -> Union[Dict[str, str], None]:
    """
    Getting dict with hotels names and ID's
    """
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": searching_city, "locale": "ru_RU"}

    key = config('rapdapi-key')

    headers = {
        'x-rapidapi-key': key,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)

    except requests.exceptions.RequestException as e:
        logger.error(f'Connection error: {e}')

        return None

    try:
        name_dict = {remove_tags(second_elem['caption']): second_elem['destinationId']
                     for first_elem in data['suggestions'] if first_elem['group'] == 'CITY_GROUP'
                     for second_elem in first_elem['entities']}

    except KeyError:
        name_dict = {}
        logger.info(f'Искомый город ({searching_city}) не найден.')
    except Exception as e:
        logger.error(f'Ошибка {e}')
        name_dict = {}

    return name_dict


@my_log
def search_hotel(city_id: str, sort_order: str, page_num: str = '1', hotels_num: str = '25',
                 max_price: Optional[str] = None, min_price: Optional[str] = None) -> Union[List[Dict[str, Any]], None]:
    """
    Getting hotels information and return sorted hotels list
    """
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"adults1": "1", "pageNumber": page_num, "destinationId": city_id,
                   "pageSize": hotels_num, "checkOut": "2020-01-15", "checkIn": "2020-01-08",
                   "priceMax": max_price, "sortOrder": sort_order, "locale": "ru_RU", "priceMin": min_price}

    headers = {
        'x-rapidapi-key': "7fc898a196msh4366a2cd7923c0cp1b136ajsnc638ab549e48",
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)

    except requests.exceptions.RequestException as e:
        logger.error(f'Connection error: {e}')
        return None

    try:
        data = data['data']['body']['searchResults']['results']
        result = [dict_for_hotel(i_hotel) for i_hotel in data]
        logger.info(f'Количество отелей до фильтрации {len(result)}')

    except KeyError:
        result = []
        logger.info(f'Поиск отелей не дал результатов.\n'
                    f' Введенные фильтры: {city_id}, {hotels_num}, {sort_order}, {max_price}, {min_price}\n')
    except Exception as e:
        result = []
        logger.error(f'Ошибка {e}')

    return result


@my_log
def dict_for_hotel(hotel_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Getting dict with names, address, price and distance to center
    """

    hotel_dict = {'name': hotel_data.get('name', 'название не указано'),
                  'address': hotel_data.get('address', {}).get('streetAddress', 'адрес не указан'),
                  'price': hotel_data.get('ratePlan', {}).get('price', {}).get('current', 'цена не указана'),
                  'distance': hotel_data['landmarks'][0]['distance']}
    return hotel_dict
