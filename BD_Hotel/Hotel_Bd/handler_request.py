import json

import requests

# from token_key import tokenKey
from token_key.tokenKeyHotel import tokenKey

HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': tokenKey(),
}


def request_processing_city(data):
    """Обработчик запроса по городам
    возращает словарь с 3 данными от сайта. Могут быть как в единичном случае так и в множественном
    name Город
    destinationId Id города
    caption Край или республика"""
    _data_dict = {}
    _json_data = json.loads(data)
    for en, i in enumerate(_json_data['suggestions'][0]["entities"]):
        _data_dict[en] = [i['name'], i['destinationId'],
                          i['caption'].replace("<span class='highlighted'>", '').replace('</span>', ''), ]

    return _data_dict


def request_processing_hotel(data):
    """Обработчик запроса по hotel
    возращает словарь с  данными от сайта. Могут быть как в единичном случае так и в множественном
    name Город
    destinationId Id города
    caption Край или республика"""
    _data_dict = {}
    _json_data = json.loads(data)
    _hotel = _json_data['data']['body']['searchResults']['results']
    for en, i in enumerate(_hotel):
        try:
            _data_dict[en] = [i['address']['locality'], i['name'], i['id'], i['landmarks'][0]['distance'],
                              i['ratePlan']['price']['current']]
        except KeyError:
            continue
    return _data_dict


def request_foto_data(data):
    """Обработчик запроса по hotel для получение url фото от каждого отеля
    фотографии небольшого размера . для быстрой загрузки пользователю

    Буква 'd' размер фото


    """
    _data_list = []
    _json_data = json.loads(data)
    _foto = _json_data['hotelImages']
    _data_list = [i['baseUrl'].replace('{size}', 'd') for i in _foto]
    return _data_list


def request_url_city(city):
    """Запрос на сайт Hotel для получение данных по городам"""
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {'query': city, "locale": "ru_RU"}

    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        return response.text
    else:
        print('Не подключается к сайту')


def get_hotel_text(city_id, start_date, end_date, sortOrder="PRICE", pageNumber=1):
    """Обработка отелев в городе
    Получаем id города. для просмотров количесво отелев в городе """
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": city_id, "pageNumber": pageNumber, "pageSize": "25", "adults1": "1",
                   "checkIn": start_date,
                   "checkOut": end_date, "sortOrder": sortOrder, "locale": "ru_RU",
                   "currency": "USD"}

    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        return response.text
    else:
        print('Не подключается к сайту')


def request_foto_hotel(id_hotel):
    """Обработка получение фото об отеле"""
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": id_hotel}

    response = requests.request("GET", url, headers=HEADERS, params=querystring)
    if response.status_code == 200:
        return response.text
    else:
        print('Не подключается к сайту')
