import datetime


class UserMessenger:
    """Класс для хранение важной информации"""

    def __init__(self):
        self.dict_city = None
        self.selected_hotels = None
        self.consent = False
        self.get_start = None
        self.get_end = None
        self.cheking = None
        self.dict_data_hotel = {}
        self.today = datetime.datetime.today()
        self.hotel_counter = 0
        self.page = 1
        self.booking_date = None

    def get_date(self, text):
        """Определение правильности вводимых надых по дате"""
        _t = text.split('.')
        _get_start = datetime.date(int(_t[2]), int(_t[1]), int(_t[0]))
        _today = datetime.date(self.today.year, self.today.month, self.today.day)
        if _today > _get_start:
            return None
        else:
            return _get_start
