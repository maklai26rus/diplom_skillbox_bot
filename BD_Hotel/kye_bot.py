import telebot

from BD_Hotel.text_hotel import text_hotel

TEXT = text_hotel()


def key_add():
    """Кнопка добавление новый отелей с других страниц"""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(TEXT['KEY_ADD'])
    # USER.page += 1
    markup.add(btn1)
    return markup


def keybord_foto_nubrer(n):
    """Сколько фотографий выводить минимум или максимум"""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('1')
    btn3 = telebot.types.KeyboardButton(n)
    markup.add(btn1, btn3)
    return markup


def keybord_foto():
    """Кнопко опроса пользователя для фотографий Да/Нет"""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Да')
    btn2 = telebot.types.KeyboardButton('Нет')
    markup.add(btn1, btn2)
    return markup


def keybord_output():
    """Кнопко опроса пользователя для фотографий Да/Нет"""
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('ВЫВОД')
    markup.add(btn1)
    return markup
