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
        self.today = datetime.date.today()
        self.max_today = self.today + datetime.timedelta(days=30)
        self.hotel_counter = 0
        self.page = 1
        self.booking_date = None
        self.test = None

    def get_date(self, text):
        """Определение правильности вводимых надых по дате"""
        try:
            _t = text.split('.')
            _get_start = datetime.date(int(_t[2]), int(_t[1]), int(_t[0]))
        except AttributeError:
            _get_start = datetime.date(text.year, text.month, text.day)
        _today = datetime.date(self.today.year, self.today.month, self.today.day)
        _max_date = datetime.date(self.max_today.year, self.max_today.month, self.max_today.day)
        if _max_date > _get_start > _today:
            return _get_start
        else:
            return None
