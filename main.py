import telebot

from BD_Hotel.Hotel_Bd.HotelBd import HotelBd
from BD_Hotel.text_hotel import text_hotel, update_text
from BD_Hotel.kye_bot import key_add, keybord_foto, keybord_foto_nubrer, keybord_output
from token_key.tokenKeyHotel import tokenBot
from user.usermessenger import UserMessenger

bot = telebot.TeleBot(tokenBot())
USER = UserMessenger()
_HOTELBD = HotelBd()
TEXT = text_hotel()


@bot.message_handler(commands=['start'])
def run(message):
    command_user(message)


@bot.message_handler(content_types=['text'])
def command_user(message):
    """Начала программы
    Спрашивает начала заезда
    """
    _HOTELBD.logging(message=message, date=str(USER.today), command=message.text)
    if message.text.lower() == '/help':
        [(bot.send_message(message.from_user.id, v)) for v in TEXT['HELPCOMMAND']]
    elif TEXT['HELPCOMMAND'][1:4].__contains__(message.text.lower()):  # '/lowprice', '/highprice', '/bestdeal'
        USER.consent = False
        bot.send_message(message.from_user.id, TEXT['TEXT_DATE'])
        bot.register_next_step_handler(message, date_start)
    elif TEXT['HELPCOMMAND'][4].__contains__(message.text.lower()):  # '/history'
        history(message)
    else:
        bot.send_message(message.from_user.id, TEXT['TEXT_GREETING'])
    USER.cheking = message.text


def history(message):
    command = f"SELECT * FROM USER WHERE user= {message.from_user.id}"
    _history = _HOTELBD.read_bd(command)
    if _history:
        for v in _history:
            bot.send_message(message.from_user.id, " ".join(map(str, v[2:])).replace('None', ''))
    else:
        bot.send_message(message.from_user.id, TEXT['ERROR_HISTORY'])


def date_start(message):
    """ Просит от пользователя дату начала заезда
    Она должна соответсвовать формату д.м.г
    не младше сегоднешнего числа

    переходит date_end
    """
    if TEXT['HELPCOMMAND'].__contains__(message.text.lower()):
        command_user(message)
    else:
        try:
            USER.get_start = USER.get_date(message.text)
            _HOTELBD.logging(message=message, command=USER.cheking, date=USER.today,
                             booking_date=f'Ввод даты заезда  {USER.get_start}')
            if not USER.get_start:
                bot.send_message(message.from_user.id, TEXT['ERROR_DATE'])
                bot.register_next_step_handler(message, date_start)
            else:
                bot.send_message(message.from_user.id, TEXT['TEXT_DATE_END'])
                bot.register_next_step_handler(message, date_end)

        except (IndexError, ValueError):
            bot.send_message(message.from_user.id, TEXT['ERROR_DATE'])
            bot.register_next_step_handler(message, date_start)


def date_end(message):
    """ Просит от пользователя дату отъезд заезда
    Она должна соответсвовать формату д.м.г

    переходит how_many_hotels_show
    """
    if TEXT['HELPCOMMAND'].__contains__(message.text.lower()):
        command_user(message)
    else:
        try:
            USER.get_end = USER.get_date(message.text)
            _HOTELBD.logging(message=message, command=USER.cheking, date=USER.today,
                             booking_date=f'Ввод даты отъезда {USER.get_end}')
            if not USER.get_end:
                bot.send_message(message.from_user.id, TEXT['ERROR_DATE'])
                bot.register_next_step_handler(message, date_end)
            else:
                bot.send_message(message.from_user.id, TEXT['CITY'])
                bot.register_next_step_handler(message, how_many_hotels_show)

        except (IndexError, ValueError):
            bot.send_message(message.from_user.id, TEXT['ERROR_DATE'])
            bot.register_next_step_handler(message, date_end)


def how_many_hotels_show(message):
    """
    Запрос на колв-во отелей

    :param message:
    :return:
    """

    if TEXT['HELPCOMMAND'].__contains__(message.text.lower()):
        command_user(message)
    else:
        bot.send_message(message.from_user.id, TEXT['TEXT_EXPECTATION'])
        USER.dict_city = _HOTELBD.request_city(message.text.title())
        if not USER.dict_city:
            bot.send_message(message.from_user.id, TEXT['ERROR_CITY'])
            bot.register_next_step_handler(message, how_many_hotels_show)
        else:

            USER.booking_date = f"c {USER.get_start}  по {USER.get_end}"

            _HOTELBD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                             booking_date=USER.booking_date)

            if USER.dict_city:
                USER.dict_data_hotel = _HOTELBD.request_hotel_data(dict_city=USER.dict_city, start_date=USER.get_start,
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

        _HOTELBD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                         booking_date=USER.booking_date, hotel=','.join(_hd))

        if TEXT['HELPCOMMAND'][3].__contains__(USER.cheking):
            _pr = _HOTELBD.price_range(USER.dict_data_hotel)
            _d = _HOTELBD.range_of_distance(USER.dict_data_hotel)
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
    _HOTELBD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                     booking_date=USER.booking_date, hotel=','.join(_hd))

    if TEXT['HELPCOMMAND'].__contains__(message.text.lower()):
        command_user(message)
    elif message.text == TEXT['KEY_ADD']:
        bot.send_message(message.from_user.id, TEXT['WAITING'])
        _dict_data_hotel = _HOTELBD.request_hotel_data(USER.dict_city, start_date=USER.get_start,
                                                       end_date=USER.get_end, text=USER.cheking, page=USER.page)
        for i in _dict_data_hotel.values():
            USER.dict_data_hotel[len(USER.dict_data_hotel) + 1] = i
        processing_number_hotels(message)
    else:
        try:
            _number = int(message.text)
            if 0 < _number <= len(USER.dict_data_hotel):
                USER.selected_hotels = _HOTELBD.request_hotel(_number, USER.dict_data_hotel)
                bot.send_message(message.chat.id, TEXT['LOAD_FOTO'], reply_markup=keybord_foto())
                bot.register_next_step_handler(message, photo_processing)
            else:
                return ValueError
        except (ValueError, KeyError):
            bot.send_message(message.from_user.id, TEXT['TEXT_NUMBER_HOTELS'])
            bot.register_next_step_handler(message, selection_number_hotels)


def photo_processing(message):
    """Обработка фотографий Да /Нет """
    _hd = [h[1] for h in USER.selected_hotels]
    _HOTELBD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                     hotel=','.join(_hd), booking_date=USER.booking_date)
    if TEXT['HELPCOMMAND'].__contains__(message.text.lower()):
        command_user(message)
    else:
        if message.text.upper() == 'ДА' or USER.consent:
            if not USER.consent:
                """Обращаеться к базе 1 раз"""
                _HOTELBD.request_foto(USER.selected_hotels)
                USER.selected_hotels = list(map(_HOTELBD.get_foto, USER.selected_hotels))

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
    """Вывод для пользователя """
    _hd = [h[1] for h in USER.selected_hotels]
    _HOTELBD.logging(message=message, date=USER.today, command=USER.cheking, city=USER.dict_city[0][1],
                     hotel=','.join(_hd), booking_date=USER.booking_date)
    for v in USER.selected_hotels:
        bot.send_message(message.from_user.id,
                         str(v[1] + ' растояния до центра ' + v[3] + ' цена ' + v[4] + '\n'))
        bot.send_message(message.from_user.id, _HOTELBD.url_hotel(v[2]))
        try:
            [bot.send_message(message.from_user.id, v[5][i]) for i in range(len(v[5]))]
        except IndexError:
            continue


def main():
    _HOTELBD.checking_bd()

    bot.infinity_polling()


if __name__ == "__main__":
    main()
