import requests
import re
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


class LMS:
    def __init__(self):
        pass

    @staticmethod
    async def get_name(soup):
        """Берем имя пользователя"""
        name = soup.find("div", class_="user-name").text
        reg = re.compile("[^а-яА-ЯёЁ0-9 ]")
        name = reg.sub("", name).split(" ")

        for i in name:
            if i == "":
                name.remove(i)
            for x in name:
                if x == "":
                    name.remove(x)

        name = " ".join(name)
        return name

    @staticmethod
    async def get_notify(soup):
        """Берём уведомления"""
        notify = soup.find("a", title="Уведомления").text
        reg = re.compile("[^а-яА-ЯёЁ0-9 ]")
        notify = reg.sub("", notify).replace(" ", "")
        return notify

    @staticmethod
    async def get_message(soup):
        """Берём сообщения"""
        message = soup.find("a", title="Личные сообщения").text
        reg = re.compile("[^а-яА-ЯёЁ0-9 ]")
        message = reg.sub("", message).replace(" ", "")
        return message

    @staticmethod
    async def sign(email, password):
        """Авторизация"""
        user = UserAgent().random
        url = "https://lms.synergy.ru/user/login"
        url1 = "https://lms.synergy.ru/schedule/academ"

        headers = {"User-Agent": user}

        data = {"popupUsername": email, "popupPassword": password}

        session = requests.Session()
        session.headers.update(headers)
        response = session.post(url, data=data)

        profile_responce = session.get(url1, headers=headers).text

        cookies_dict = [
            {
                "domain": key.domain,
                "name": key.name,
                "path": key.path,
                "value": key.value,
            }
            for key in session.cookies
        ]

        session2 = requests.Session()

        for cookies in cookies_dict:
            session2.cookies.set(**cookies)

        resp = session2.get(url1, headers=headers)
        return resp

    @classmethod
    async def acc_verify(cls, email, password):
        """Проверка аккаунта"""
        resp = await cls.sign(email, password)
        if resp.status_code == 200:
            return True
        else:
            return False

    @classmethod
    async def get_soup(cls, email, password):
        """Получаем суп"""
        resp = await cls.sign(email, password)
        soup = bs(resp.text, "html.parser")
        return soup

    @classmethod
    async def get_info_user(cls, soup):
        """Получаем информацию о пользователе"""
        info_user = soup.find("div", id="user-profile")
        name = await cls.get_name(info_user)
        notify = await cls.get_notify(soup)
        message = await cls.get_message(soup)
        data = {"name": name, "notify": notify, "message": message}
        return data

    @classmethod
    async def get_get_soup_info(cls, email, password):
        """Получаем информацию о пользователе полсе авторизации"""
        soup = await cls.get_soup(email, password)
        return await cls.get_info_user(soup)

    @staticmethod
    async def processing_schedule(string):
        return re.findall(
            r"(([0-9][0-9]:[0-9][0-9] [0-9][0-9]:[0-9][0-9])\s*.\w+.\w+.\w+.\w+.\w+.\w+.\w+.\w+.)",
            string,
        )

    @classmethod
    async def schedule(cls, soup):
        """Получаем расписание"""
        schedule = soup.find("table", class_="table-list v-scrollable").text
        reg = re.compile("[^а-яА-ЯёЁ0-9.: ]")
        schedule = reg.sub("", schedule).split(" ")

        for i in schedule:
            if i == "":
                schedule.remove(i)
            for x in schedule:
                if x == "":
                    schedule.remove(x)
        schedule = schedule[3:]
        schedule = " ".join(schedule)
        schedule = await cls.processing_schedule(schedule)

        return schedule

    @classmethod
    async def get_schedule(cls, email, password):
        """Получаем расписание пользователя"""
        soup = await cls.get_soup(email, password)
        schedule = await cls.schedule(soup)
        return schedule
