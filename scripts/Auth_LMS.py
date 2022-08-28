from requests import Session

# import re
from re import compile, findall, split
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


class LMS:
    def __init__(self):
        pass

    @staticmethod
    async def get_name(soup):
        """Берем имя пользователя"""
        name = soup.find("div", class_="user-name").text
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

    @staticmethod
    async def get_notify(soup):
        """Берём уведомления"""
        try:
            notify = soup.find("a", title="Уведомления").text
            reg = compile("[^а-яА-ЯёЁ0-9 ]")
            notify = reg.sub("", notify).replace(" ", "")
            return notify
        except AttributeError:
            return "0"

    @staticmethod
    async def get_message(soup):
        """Берём сообщения"""
        try:
            message = soup.find("a", title="Личные сообщения").text
            reg = compile("[^а-яА-ЯёЁ0-9 ]")
            message = reg.sub("", message).replace(" ", "")
            return message
        except AttributeError:
            return "0"

    @staticmethod
    async def sign(email, password):
        """Авторизация"""
        user = UserAgent().random
        url = "https://lms.synergy.ru/user/login"
        url1 = "https://lms.synergy.ru/schedule/academ"

        headers = {"User-Agent": user}

        data = {"popupUsername": email, "popupPassword": password}

        session = Session()
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

        session2 = Session()

        for cookies in cookies_dict:
            session2.cookies.set(**cookies)

        resp = session2.get(url1, headers=headers)
        return resp

    @classmethod
    async def acc_verify(cls, email, password):
        """Проверка аккаунта"""
        try:
            soup = await cls.get_soup(email, password)
            await cls.get_info_user(soup)
            return True
        except AttributeError:
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
    async def get_soup_info(cls, email, password):
        """Получаем информацию о пользователе полсе авторизации"""
        soup = await cls.get_soup(email, password)
        return await cls.get_info_user(soup)

    @staticmethod
    async def processing_schedule_step2(string):
        """Обрабатываем расписание"""
        return findall(
            r"(([0-9][0-9]:[0-9][0-9] [0-9][0-9]:[0-9][0-9])\s*.\w+.\w+.\w+.\w+.\w+.\w+.\w+.\w+.)",
            string,
        )

    @classmethod
    async def processing_schedule(cls, string):
        """Обрабатываем расписание"""
        string = [string]
        content = []
        schedule = []

        for element in string:
            content += split("(пн|вт|ср|чт|пт|сб|вт)\s+", element)

        try:
            content.remove("")
        except ValueError:
            pass

        for i, x in enumerate(content):
            if i % 2 != 0:
                content[i] = await cls.processing_schedule_step2(x)
                schedule.append([content[i - 1], content[i]])

        return schedule

    @classmethod
    async def schedule(cls, soup):
        """Получаем расписание"""
        schedule = soup.find("table", class_="table-list v-scrollable").text
        reg = compile("[^а-яА-ЯёЁ0-9.: ]")
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
