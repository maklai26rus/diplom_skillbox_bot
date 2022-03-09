import sqlite3

from bd_hotel.hotel_bd.handler_request import *

BD = 'bd_hotel/hotel_bd/HotelBD.db'


class HotelBd:
    """Хранилище БД и обратка БД

    Класс создает бд с таблицами
    CREATE TABLE CITY
    CREATE TABLE HOTEL
    CREATE TABLE USER


    CITY хранит в себе параметра ГОРОД destinationId caption

    HOTEL хранит в себе Город, Отель, destinationId, url_foto

    USER

    Для экономиии запросов была создана БД с основными характеристиками для API
    Если города нет в БД создает запрос на сайт для получение его данных, при следующих запросов сначала проверяет БД на
    город и выдается данные.

    Такаяже ситуация и с HOTEL. БД заполняется по запросам. графа url foto обновляется только после запроса пользвотеля
    получить фото нужного отеля.

    Такая манипуляция помогает мимилизировать кол-во запросов на сайт


    """

    def __init__(self):
        self.data_city = None
        self.dict_data_hotel = None
        self._input_city = ''
        self.number_of_hotels = []
        self.bool_foto = False

    def checking_bd(self):
        """Функция Создание БД таблиц
        Проверка если таблица или нет.
        Если таблица есть то функция отработает спокойно
        Если же таблица отсуствует то будет созданые нужные поля

        """
        __check_table1 = """SELECT * FROM CITY"""
        __check_table2 = """SELECT * FROM HOTEL"""
        __check_table3 = """SELECT * FROM USER"""

        def com_si():
            """после проверки созадет таблицу"""
            command_siti = """CREATE TABLE CITY (
                    "ID"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "Город"	TEXT NOT NULL,
                    "destinationId"	INTEGER NOT NULL,
                    "caption"	TEXT)"""
            return command_siti

        def com_ho():
            """после проверки созадет таблицу"""
            command_hotel = """CREATE TABLE HOTEL (
                    "ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "Город"	TEXT NOT NULL,
                    "Отель"	TEXT NOT NULL,
                    "destinationId"	NUMERIC NOT NULL UNIQUE,
                    "url_foto"	TEXT
                    )"""
            return command_hotel

        def com_us():
            """после проверки созадет таблицу"""
            command_user = """CREATE TABLE USER (
                    "ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "user"	TEXT,
                    "command"	TEXT,
                    "city"	TEXT,
                    "hotel"	TEXT,
                    "booking_date"	TEXT,
                    "date"	TEXT)"""
            return command_user

        if self.read_bd(__check_table1) is None:
            self.read_bd(com_si())
            print('Была создана Таблица CITY')
        if self.read_bd(__check_table2) is None:
            self.read_bd(com_ho())
            print('Была создана Таблица HOTEL')
        if self.read_bd(__check_table3) is None:
            self.read_bd(com_us())
            print('Была создана Таблица USER')

    def fillings_city(self, text_json):
        """Функция заполнения таблицы Город"""
        __d = request_processing_city(text_json)
        self._fill_data_city(__d)

    def fillings_hotel(self, text_json):
        """Функция заполнения таблицы Отель"""
        __d = request_processing_hotel(text_json)
        self._fill_data_hotel(__d)

    def _fill_data_city(self, data_dict):
        """Запись данныхв таблицу City для хранения истории"""
        id_data = 0
        for i in data_dict:
            command = f"""SELECT * FROM CITY WHERE destinationId='{data_dict[i][1]}'"""
            if self.read_bd(command):
                pass
            else:
                command_max_id = """SELECT MAX(ID) FROM City """
                try:
                    max_id = self.read_bd(command_max_id)
                    id_data = max_id[0][0] + 1
                except TypeError:
                    id_data = 1

                command_save = f"""INSERT INTO CITY VALUES ('{id_data}','{data_dict[i][0]}','{data_dict[i][1]}','{data_dict[i][2]}')"""
                self.read_bd(command_save, save=True)

    def _fill_data_hotel(self, data_dict):
        """Запись данныхв таблицу HOTEL для хранения истори"""
        id_data = 0

        for i in data_dict:
            _hotel_none = None
            command = f"""SELECT * FROM HOTEL WHERE destinationId='{data_dict[i][2]}'"""
            if self.read_bd(command):
                pass
            else:
                command_max_id = """SELECT MAX(ID) FROM HOTEL """
                try:
                    max_id = self.read_bd(command_max_id)
                    id_data = max_id[0][0] + 1
                except TypeError:
                    id_data = 1
                command_save = f"""INSERT INTO HOTEL VALUES ('{id_data}','{data_dict[i][0]}','{data_dict[i][1]}',
                                '{data_dict[i][2]}','{'Еще не обновил url фотографий'}')"""
                self.read_bd(command_save, save=True)

    def _fill_data_user(self, data_dict):
        """Запись данныхв таблицу USER для хранения истори"""
        id_data = 0
        for i in data_dict:
            command = f"""SELECT * FROM USER WHERE destinationId='{data_dict[i][1]}'"""
            if self.read_bd(command):
                pass
            else:
                command_max_id = """SELECT MAX(ID) FROM USER """
                try:
                    max_id = self.read_bd(command_max_id)
                    id_data = max_id[0][0] + 1
                except TypeError:
                    id_data = 1

                command_save = f"""INSERT INTO USER VALUES ('{id_data}','{data_dict[i][0]}','{data_dict[i][1]}',
                                '{data_dict[i][2]}, '{data_dict[i][3]}')"""
                self.read_bd(command_save, save=True)

    def read_bd(self, command, save=False):
        """
        Получает команду на чтения команды
        save нужен для  сохранения изменения
        """

        try:
            sqlite_connection = sqlite3.connect(BD)
            cursor = sqlite_connection.cursor()
            cursor.execute(command)
            record = cursor.fetchall()
            _list = list(map(list, record))
            if save:
                sqlite_connection.commit()
            cursor.close()
            return _list
        except (sqlite3.Error, IndexError) as error:
            print(f"Ошибка при подключении к {BD} - ", error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()

    def checking_for_city(self, city):
        """Проверка на город.
        Если есть возращает даные по городу
        Если нет, то пустоту"""
        command_city = f"""SELECT * FROM CITY WHERE Город = "{city}" """
        __d = self.read_bd(command_city)
        if __d:
            return __d

    def request_city(self, input_city):
        """Проводим запрос в БД если имеется данные возращает по нему
        Если же нет то делает запрос на сайт для получение актуальной информации"""
        # __data_city = None
        __data_city = self.checking_for_city(input_city)
        if not __data_city:
            try:
                __dc = request_url_city(input_city)
                self.fillings_city(__dc)
                __data_city = self.checking_for_city(input_city)
            except TypeError:
                pass

        self.data_city = __data_city
        return __data_city

    def request_hotel_data(self, dict_city, start_date, end_date, text, page=1):

        """Пополняем базу данных отелев
        request_hotel_highprice : От самого дорого отеля к дешевому
        request_hotel_lowprice : От дешевого к дорогому
        request_hotel_bestdeal : Получаем данные самый близкий к центру города
        """

        if text == '/highprice':

            json_file = get_hotel_text(dict_city[0][2], start_date, end_date, sortOrder='PRICE_HIGHEST_FIRST',
                                       pageNumber=page)
        elif text == '/bestdeal':
            json_file = get_hotel_text(dict_city[0][2], start_date, end_date, sortOrder="DISTANCE_FROM_LANDMARK",
                                       pageNumber=page)
        else:
            json_file = get_hotel_text(dict_city[0][2], start_date, end_date, pageNumber=page)

        self.fillings_hotel(json_file)
        return request_processing_hotel(json_file)

    def request_hotel(self, nember_hotel, dict_data_hotel):
        """Сбор данных по нужному кол-ву отелей
        nember_hotel кол-во выводимых отелей
        dict_data_hotel полный словарь отелей
        :return number_of_hotels Возращает list выброное кол-во отелей
        """
        number_of_hotels = [dict_data_hotel[v] for v in range(nember_hotel)]
        return number_of_hotels

    def request_foto(self, number_of_hotels):
        """Заполнение таблицы hotel поле url foto
        number_of_hotels = ['Уфа', 'Гостевые комнаты «Ардерия»', 768899648, '3,8 км', '$17']
        Если отель иммеет такое поле url_foto='Еще не обновил url фотографий'
        То обновляет его добовляе url фотографий с этого отеля

        """
        for i in number_of_hotels:
            command_id_url = f"""SELECT * FROM HOTEL WHERE destinationId='{i[2]}' and url_foto='Еще не обновил url фотографий'"""
            if self.read_bd(command_id_url):
                _fid = request_foto_hotel(i[2])
                _listurl = request_foto_data(_fid)
                up = f"""UPDATE HOTEL SET url_foto = "{_listurl}" WHERE destinationId={i[2]}"""
                self.read_bd(up, save=True)

    def price_range(self, number_of_hotels):
        """
        проверка на минимум максимум цен
        то количвосто отелей которе выбрал пользователь
        пример приходящий данных
        number_of_hotels = {0: ['Омск', ' «Ибис Сибирь-Омск»', 322603, '3,0 км', '$64']}

        :return:
        """
        price = [int(v[4].replace('$', '')) for v in number_of_hotels.values()]
        return price

    def range_of_distance(self, number_of_hotels):
        """
        проверка на минимум максимум растояний
        то количвосто отелей которе выбрал пользователь
        пример приходящий данных
        number_of_hotels = [['Уфа', 'Гостевые комнаты «Ардерия»', 768899648, '3,8 км', '$17']]

        :return:
        """
        distance = [float(v[3].replace('км', '').replace(',', '.')) for v in number_of_hotels.values()]
        return distance

    def logging(self, message=None, date=None, command=None, city=None, hotel=None, booking_date=None):
        command_max_id = """SELECT MAX(ID) FROM USER """
        try:
            max_id = self.read_bd(command_max_id)
            id_data = max_id[0][0] + 1
        except TypeError:
            id_data = 1

        command_save = f"""INSERT INTO USER VALUES ('{id_data}',{message.from_user.id},'{command}','{city}', 
                                                    '{hotel}','{str(booking_date)}','{str(date)}')"""
        self.read_bd(command_save, save=True)

    def get_foto(self, number_of_hotels):
        """Достаем из БД имеющие url фотографии, переобразуем текст в список. удаляем не нужные элементы
        и добоваляем в number_of_hotels список фотографий
        number_of_hotels ['Омск', ' «Ибис Сибирь-Омск»', 322603, '3,0 км', '$64']
        """
        command_id = f"""SELECT * FROM HOTEL WHERE destinationId='{number_of_hotels[2]}'"""
        _foto_list = self.read_bd(command_id)[0][4].replace('[', '').replace(']', '').replace(',', '').split()
        number_of_hotels.append(_foto_list)
        return number_of_hotels

    def url_hotel(self, id_hotel):
        # url = f'https://ru.hotels.com/ho{id_hotel}/?q-check-in=2022-02-03&q-check-out=2022-02-04&q-rooms=1&q-room-0-adults=2&q-room-0-children=0&sort-order=BEST_SELLER&WOD=4&WOE=5&MGT=1&ZSX=0&SYE=3&YGF=1'
        url = f'https://ru.hotels.com/ho{id_hotel}'
        return url
