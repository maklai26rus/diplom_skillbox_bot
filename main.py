import telebot

from bd_hotel.hotel_bd.hotel_bd import HotelBd
from bd_hotel.text_hotel import text_hotel, update_text
from bd_hotel.kye_bot import key_add, keybord_foto, keybord_foto_nubrer, keybord_output
from bd_hotel.my_calendar import MyStyleCalendar
from user.usermessenger import UserMessenger
from decouple import config
from telegram_bot_calendar import LSTEP

SECRET_KEY_BOT = config('SECRET_KEY_BOT')

bot = telebot.TeleBot(SECRET_KEY_BOT)

USER = UserMessenger()
HOTEL_BD = HotelBd()
TEXT = text_hotel()


@bot.message_handler(commands=['start'])
def run(message):
    command_user(message)


@bot.message_handler(content_types=['text'])
def command_user(message):
    """Начала программы
    Спрашивает начала заезда
    """
    HOTEL_BD.logging(message=message, date=str(USER.today), command=message.text)
    if message.text.lower() == '/help':
        [(bot.send_message(message.from_user.id, v)) for v in TEXT['HELPCOMMAND']]
    elif message.text.lower() in TEXT['HELPCOMMAND'][1:4]:  # '/lowprice', '/highprice', '/bestdeal'
        run_start_date(message)
    elif message.text.lower() in TEXT['HELPCOMMAND'][4]:  # '/history'
        history(message)
    else:
        bot.send_message(message.from_user.id, TEXT['TEXT_GREETING'])
    USER.cheking = message.text


def run_start_date(message):
    """Запуск модуля календаря
    Идет обновление данные начала и отъезд

    """
    USER.consent = False
    USER.get_start = None
    USER.get_end = None
    start_date(message)
    bot.register_next_step_handler(message, cheking_date)


def cheking_date(message):
    """Проверка на входящие данные по дате заезда

    USER.get_start должен быть не меньше сегоднешнего
    USER.get_end не дорлжен быть больше 30 дней и не меньше USER.get_start

    В отстальных слачаях обнуление счечика и заново запускает run_start_date

    """

    if message.text.lower() in TEXT['HELPCOMMAND']:
        command_user(message)
    else:
        try:
            USER.get_start = USER.get_date(USER.get_start)
            USER.get_end = USER.get_date(USER.get_end)
        except AttributeError:
            pass

        if not USER.get_start or not USER.get_end:
            bot.send_message(message.from_user.id, TEXT['ERROR_DATE_SPAN'])
            run_start_date(message)
        else:
            how_many_hotels_show(message)


def start_date(message):
    """Запуск модуля календарь. Выбирает дату заезда с помощью клавиатуры """
    calendar, step = MyStyleCalendar(locale='ru', min_date=USER.today,
                                     max_date=USER.max_today).build()
    bot.send_message(message.from_user.id, TEXT['TEXT_DATE'])
    bot.send_message(message.chat.id, f"{LSTEP[step]}", reply_markup=calendar)


def end_date(chat_id) -> None:
    """Запуск модуля календарь. Выбирает дату отъезда с помощью клавиатуры"""
    calendar, step = MyStyleCalendar(locale='ru', min_date=USER.today,
                                     max_date=USER.max_today).build()
    bot.send_message(chat_id, TEXT['TEXT_DATE_END'])
    bot.send_message(chat_id, f"{LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=MyStyleCalendar.func())
def cal(c):
    result, key, step = MyStyleCalendar(locale='ru').process(
        c.data)
    if not result and key:
        bot.edit_message_text(f"{LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id, reply_markup=key)
    elif result:
        USER.test = result
        bot.edit_message_text(f"Выбрана дата {result.day}.{result.month}.{result.year}",
                              c.message.chat.id,
                              c.message.message_id)

        if not USER.get_start:
            USER.get_start = USER.test
            end_date(c.message.chat.id)
        elif not USER.get_end:
            USER.get_end = USER.test
            bot.send_message(c.message.chat.id, TEXT['CITY'])


def history(message):
    """Выводим история обращение пользователя """
    command = f"SELECT * FROM USER WHERE user= {message.from_user.id}"
    _history = HOTEL_BD.read_bd(command)
    if _history:
        for v in _history:
            bot.send_message(message.from_user.id, " ".join(map(str, v[2:])).replace('None', ''))
    else:
        bot.send_message(message.from_user.id, TEXT['ERROR_HISTORY'])


def how_many_hotels_show(message):
    """
    Запрос на колв-во отелей

    :param message:
    :return:
    """

    if message.text.lower() in TEXT['HELPCOMMAND']:
        command_user(message)
    else:
        bot.send_message(message.from_user.id, TEXT['TEXT_EXPECTATION'])
        USER.dict_city = HOTEL_BD.request_city(message.text.title())
        if not USER.dict_city:
            bot.send_message(message.from_user.id, TEXT['ERROR_CITY'])
            bot.register_next_step_handler(message, how_many_hotels_show)
        else:

            USER.booking_date = f"c {USER.get_start}  по {USER.get_end}"

            HOTEL_BD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                             booking_date=USER.booking_date)

            if USER.dict_city:
                USER.dict_data_hotel = HOTEL_BD.request_hotel_data(dict_city=USER.dict_city, start_date=USER.get_start,
                                                                   end_date=USER.get_end, text=USER.cheking,
                                                                   page=USER.page)

                processing_number_hotels(message)
            else:
                _text = update_text(USER.dict_data_hotel)  # Обновленяемые данные по отолем
                bot.send_message(message.from_user.id, _text['TEXT_NUMBER_HOTELS'])


def processing_number_hotels(message):
    """Функция для обработки кол-во выводимы отелей
    Проверяет кратность 25 доступных отелей на 1 странице

    """
    USER.page += 1
    if not USER.dict_data_hotel:
        bot.send_message(message.from_user.id, TEXT['NONE_HOTEL'])
        command_user(message)
    else:

        _text = update_text(USER.dict_data_hotel)  # Обновленяемые данные по отолем

        _hd = [h[1] for h in USER.dict_data_hotel.values()]
        HOTEL_BD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                         booking_date=USER.booking_date, hotel=','.join(_hd))

        if USER.cheking in TEXT['HELPCOMMAND'][3]:
            _pr = HOTEL_BD.price_range(USER.dict_data_hotel)
            _d = HOTEL_BD.range_of_distance(USER.dict_data_hotel)
            bot.send_message(message.from_user.id,
                             f'Минимальная стоймость {min(_pr)}$ , максамальная стоймасть {max(_pr)}$')
            bot.send_message(message.from_user.id,
                             f'Минимальное растояние до центра {min(_d)} км, максимальное растояние до центра {max(_d)} км')

        if len(USER.dict_data_hotel) % 25 == 0:
            bot.send_message(message.chat.id, _text['HOTEL_ADD'], reply_markup=key_add())
            bot.register_next_step_handler(message, selection_number_hotels)
        else:
            bot.send_message(message.from_user.id, _text['HOTEL'])
            bot.register_next_step_handler(message, selection_number_hotels)


def selection_number_hotels(message):
    """Запрос на обратку нужного кол-во отелей"""

    _hd = [h[1] for h in USER.dict_data_hotel.values()]
    HOTEL_BD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                     booking_date=USER.booking_date, hotel=','.join(_hd))

    _text = update_text(USER.dict_data_hotel)

    if message.text.lower() in TEXT['HELPCOMMAND']:
        command_user(message)
    elif message.text == TEXT['KEY_ADD']:
        bot.send_message(message.from_user.id, TEXT['WAITING'])
        _dict_data_hotel = HOTEL_BD.request_hotel_data(USER.dict_city, start_date=USER.get_start,
                                                       end_date=USER.get_end, text=USER.cheking, page=USER.page)
        for i in _dict_data_hotel.values():
            USER.dict_data_hotel[len(USER.dict_data_hotel) + 1] = i
        processing_number_hotels(message)
    else:
        try:
            _number = int(message.text)
            if 0 < _number <= len(USER.dict_data_hotel):
                USER.selected_hotels = HOTEL_BD.request_hotel(_number, USER.dict_data_hotel)
                bot.send_message(message.chat.id, TEXT['LOAD_FOTO'], reply_markup=keybord_foto())
                bot.register_next_step_handler(message, photo_processing)
            else:
                return ValueError
        except (ValueError, KeyError):
            bot.send_message(message.from_user.id, _text['TEXT_NUMBER_HOTELS'])
            bot.register_next_step_handler(message, selection_number_hotels)


def photo_processing(message):
    """Обработка фотографий Да /Нет

    Да - выводит фотографии по отелям предварительно спрашивая о кол-ве фотографий
    Нет - перехоит на послдний шаг без фото

    """

    _hd = [h[1] for h in USER.selected_hotels]
    HOTEL_BD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                     hotel=','.join(_hd), booking_date=USER.booking_date)

    if message.text.lower() in TEXT['HELPCOMMAND']:
        command_user(message)
    else:
        if message.text.upper() == 'ДА' or USER.consent:
            if not USER.consent:
                """Обращаеться к базе 1 раз"""
                HOTEL_BD.request_foto(USER.selected_hotels)
                USER.selected_hotels = list(map(HOTEL_BD.get_foto, USER.selected_hotels))

            USER.consent = True

            if message.text.isdigit():
                if 0 < int(message.text) <= len(USER.selected_hotels[USER.hotel_counter][5]):
                    USER.selected_hotels[USER.hotel_counter][5] = USER.selected_hotels[USER.hotel_counter][5][
                                                                  0:int(message.text)]
                    USER.hotel_counter += 1
                else:
                    bot.register_next_step_handler(message, photo_processing)
                    bot.send_message(message.from_user.id, TEXT['ERROR_FOTO'])

            if USER.hotel_counter < len(USER.selected_hotels):
                bot.send_message(message.chat.id, f"Сколько фотографий: {USER.selected_hotels[USER.hotel_counter][1]},"
                f"\nпоказать из {len(USER.selected_hotels[USER.hotel_counter][5])}?  : ",
                                 reply_markup=keybord_foto_nubrer(len(USER.selected_hotels[USER.hotel_counter][5])))

                bot.register_next_step_handler(message, photo_processing)
            else:
                bot.send_message(message.chat.id, TEXT['TEXT_OUTPUT'], reply_markup=keybord_output())
                bot.register_next_step_handler(message, conclusion_by_hotels)

        elif message.text.upper() == 'НЕТ':
            conclusion_by_hotels(message)
        else:
            bot.send_message(message.from_user.id, TEXT['TEXT_FOTO'])
            bot.register_next_step_handler(message, photo_processing)


def conclusion_by_hotels(message):
    """Финальный вывод бота.
    Выводит данные по тем отелям которые были выбраны
    """
    _hd = [h[1] for h in USER.selected_hotels]

    HOTEL_BD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                     hotel=','.join(_hd), booking_date=USER.booking_date)

    for v in USER.selected_hotels:
        bot.send_message(message.from_user.id,
                         str(v[1] + ' растояния до центра ' + v[3] + ' цена ' + v[4] + '\n'))
        bot.send_message(message.from_user.id, HOTEL_BD.url_hotel(v[2]))
        try:
            [bot.send_message(message.from_user.id, v[5][i]) for i in range(len(v[5]))]
        except IndexError:
            continue


def main():
    HOTEL_BD.checking_bd()

    bot.infinity_polling()
    # bot.


if __name__ == "__main__":
    main()
