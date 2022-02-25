def text_hotel():
    """Текст в модуле
    """
    _text = {
        'TEXT_GREETING': "Вас приветсвует БОТ MBB_HOTEL жду ваших запросов: /help ",
        'TEXT_FOTO': 'Введите правильны вариант Да/Нет',
        'TEXT_ADD': 'Обновляю следющию дополнительную страницу',
        'TEXT_DATE': 'Дата бранирование \nпример :"14.12.2022"',
        'TEXT_DATE_END': 'Дата отъезда \nпример :"14.12.2022"',
        'TEXT_EXPECTATION': 'Дождитесь ответа. Идет запрос на сайт',
        'TEXT_OUTPUT': "Ваш запрос готов нажмите 'ВЫВОД'",
        'ERROR_CITY': 'Такого города нет, повторите запрос с начала',
        'ERROR_DATE': 'Неправильный формат даты привер "14.12.2022" - "Д.М.Г"',
        'ERROR_FOTO': 'Введите правильное кол-во фотографий',
        'ERROR_HISTORY': 'Вашей истории не обнаружено. Начтите пользоваться ботом',
        'HELPCOMMAND': ['/help', '/lowprice', '/highprice', '/bestdeal', '/history'],  # порядок не менять!!!
        'CITY': "В какой город хотите направиться? : ",
        'KEY_ADD': 'add',
        'WAITING': 'Нечего не вводите идет запрос на сайт, ожидайте ответа',
        'LOAD_FOTO': "Необходимость загрузки и вывода фотографий для каждого отеля (“Да/Нет”) : ",
        'NONE_HOTEL': "Больше нет объектов размещения, соответствующих вашим критериям поиска. Измените ваши даты, чтобы увидеть новые варианты размещения.",

    }
    return _text


def update_text(dict_data_hotel):
    """Текст в модуле
    принимает словарь
    для отображения кол-ва
    """
    _text = {
        'TEXT_NUMBER_HOTELS': f"Прошу ввести цифру в диапозоне от 0 до {len(dict_data_hotel)}' ",
        'HOTEL': f'Сколько отелей, вы хотете просмотреть из {len(dict_data_hotel)} ?',
        'HOTEL_ADD': f'Сколько отелей показать Вам из {len(dict_data_hotel)}? \n загрузить еще одну страницу? наберите команду add',
    }
    return _text
