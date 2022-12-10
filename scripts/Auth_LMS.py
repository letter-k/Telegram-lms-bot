from requests import Session
from re import compile, sub
from bs4 import BeautifulSoup as bs
# from fake_useragent import UserAgent
# from fp.fp import FreeProxy
from aiohttp import ClientSession


class LMS:
    session = None

    def __init__(self, email, password):
        self.create_session(email, password)

    def __del__(self):
        self.session = None

    @classmethod
    def create_session(cls, email, password):
        cls.session = cls.__sign(email, password)

    @staticmethod
    def __sign(email, password):
        """Авторизация"""
        # user = UserAgent().random
        # proxy = FreeProxy(https=False, anonym=True).get()
        url = "https://lms.synergy.ru/user/login"
        url1 = "https://lms.synergy.ru/schedule/academ"

        # headers = {"User-Agent": user}

        # proxies = {
        #     'http': proxy
        # }

        data = {"popupUsername": email, "popupPassword": password}

        session = Session()
        # session.headers.update(headers)
        session.post(url, data=data)

        session.get(url1).text

        cookies_dict = [
            {
                "domain": key.domain,
                "name": key.name,
                "path": key.path,
                "value": key.value,
            }
            for key in session.cookies
        ]

        session2 = Session()

        for cookies in cookies_dict:
            session2.cookies.set(**cookies)

        resp = session2.get(url1)
        return resp

    @classmethod
    def get_soup(cls):
        """Получаем суп"""
        resp = cls.session
        soup = bs(resp.text, "html.parser")
        return soup

    @classmethod
    def get_name(cls):
        """Берем имя пользователя"""
        name = cls.get_soup().find("div", class_="user-name").text
        reg = compile("[^а-яА-ЯёЁ0-9 ]")
        name = reg.sub("", name).split(" ")

        for i in name:
            if i == "":
                name.remove(i)
            for x in name:
                if x == "":
                    name.remove(x)

        name = " ".join(name)
        return name

    @classmethod
    def get_notify(cls):
        """Берём уведомления"""
        try:
            notify = cls.get_soup().find("a", title="Уведомления").text
            reg = compile("[^а-яА-ЯёЁ0-9 ]")
            notify = reg.sub("", notify).replace(" ", "")
            return notify
        except AttributeError:
            return "0"

    @classmethod
    def get_message(cls):
        """Берём сообщения"""
        try:
            message = cls.get_soup().find("a", title="Личные сообщения").text
            reg = compile("[^а-яА-ЯёЁ0-9 ]")
            message = reg.sub("", message).replace(" ", "")
            return message
        except AttributeError:
            return "0"

    @classmethod
    def get_info_user(cls):
        """Получаем информацию о пользователе"""
        name = cls.get_name()
        notify = cls.get_notify()
        message = cls.get_message()
        data = {
            "name": name,
            "notify": notify, 
            "message": message
        }
        return data

    @classmethod
    def acc_verify(cls):
        """Проверка аккаунта"""
        try:
            cls.get_info_user()
            return True
        except AttributeError:
            return False

    @staticmethod
    def split_by_pattern(string, pattern):
        return list(filter(None, sub(pattern, r'@@\1', string).split('@@')))

    @classmethod
    def split_by_pattern2(cls, list):
        schedule = []
        for i in list:
            schedule.append((i[:11], cls.split_by_pattern(i[12:], r"(\d{2}:\d{2} \d{2}:\d{2})")))

        return schedule

    @classmethod
    def schedule(cls):
        """Получаем расписание"""
        schedule = cls.get_soup().find("table", class_="table-list v-scrollable").text
        schedule = schedule.replace("Время\nКурс\nМесто проведения\nВид занятия\nПреподаватель", "")
        reg = compile("[^а-яА-ЯёЁ0-9.: ]")
        schedule = reg.sub("", schedule).split(" ")

        for i in schedule:
            if i == "":
                schedule.remove(i)
            for x in schedule:
                if x == "":
                    schedule.remove(x)
        schedule = " ".join(schedule)
        schedule = cls.split_by_pattern(schedule, r'(([\d]{2}\.){2}[\d]{2})')
        schedule = cls.split_by_pattern2(schedule)

        return schedule

    @classmethod
    def get_schedule(cls):
        """Получаем расписание пользователя"""
        schedule = cls.schedule()
        if schedule == []:
            return "Расписание пустое"
        return schedule

    @classmethod
    def get_today_schedule(cls):
        """Получаем расписание на сегодня"""
        schedule = cls.get_schedule()
        try:
            return schedule[0]
        except IndexError:
            return "Сегодня нет пар"
    
    @classmethod
    def get_tomorrow_schedule(cls):
        """Получаем расписание на сегодня"""
        schedule = cls.get_schedule()
        try:
            return schedule[1]
        except IndexError:
            return "Сегодня нет пар"
