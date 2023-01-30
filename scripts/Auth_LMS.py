from requests import Response, Session
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import typing


class clean_data:
    @staticmethod
    def remove_many_spaces(string):
        return " ".join(string.split())

class LMS:
    _URL: typing.Final[str] = "https://lms.synergy.ru"
    _URL_LOGIN: typing.Final[str] = "%s/user/login" % _URL
    _URL_SCHEDULE: typing.Final[str] = "%s/schedule/academ" % _URL
    _URLS_LEANGUAGES: typing.Final[dict] = {
        "ru": "%s/user/lng/1" % _URL,
        "en": "%s/user/lng/2" % _URL
    }

    session: Session = None
    
    def __init__(self, login: str = "demo", password: str = "demo", proxy: dict = None, headers: dict = None, leanguage: str = "en") -> None:
        """Инициализация класса

        :param login: Логин
        :param password: Пароль
        :param proxy: Прокси
        :param headers: Заголовки
        :param leanguage: Язык

        :type login: str
        :type password: str
        :type proxy: dict
        :type headers: dict
        :type leanguage: str

        :return: None
        :rtype: None

        :Example:
        
        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_name()
        'Студент Демонстрационный'
        """

        self.login = login
        self.password = password
        self.proxy = proxy
        self.headers = headers
        self.leanguage = leanguage
        
        self.__sign()

    def __del__(self) -> None:
        """Закрывает сессию
        
        :return: None
        :rtype: None
        
        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> del lms
        """

        if self.session:
            self.session.close()

    def __sign(self) -> None:
        """Авторизация

        :return: None
        :rtype: None

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms._LMS__sign()
        """

        headers: dict = self.headers if self.headers else {"User-Agent": UserAgent().random}
        proxies: dict = self.proxy if self.proxy else {}

        data: dict = {"popupUsername": self.login, "popupPassword": self.password}

        self.session = Session()
        self.session.headers.update(headers)
        self.session.post(self._URL_LOGIN, data=data, proxies=proxies)
        self.session.get(self._URLS_LEANGUAGES[self.leanguage], proxies=proxies)

    @property
    def cookies(self) -> dict:
        """Возвращает куки

        :return: Куки
        :rtype: dict

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.cookies
        """

        return self.session.cookies.get_dict()

    @cookies.setter
    def cookies(self, cookies: dict) -> None:
        """Устанавливает куки

        :param cookies: Куки
        :type cookies: dict

        :return: None
        :rtype: None

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_cookies = {"PHPSESSID": "demo"}
        """

        self.session.cookies.update(cookies)

    def _get_soup_schedule(self) -> bs:
        """Возвращает bs4 объект с расписанием

        :return: bs4 объект с расписанием
        :rtype: bs4.BeautifulSoup

        :Example:
        
        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms._get_soup_schedule()

        <html>...</html>
        """

        session: Session = Session()

        session.get(self._URLS_LEANGUAGES[self.leanguage], cookies=self.cookies)

        response: Response = session.get(self._URL_SCHEDULE, cookies=self.cookies)

        return bs(response.text, "html.parser")

    def verify(self) -> bool:
        """Проверяет авторизацию

        :return: True, если авторизован, иначе False
        :rtype: bool

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.verify()

        True
        """

        soup: bs = self._get_soup_schedule()

        return soup.find("div", {"class": "user-name"}) is not None

    def get_name(self) -> str:
        """Возвращает имя

        :return: Имя
        :rtype: str

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_name()

        'Студент Демонстрационный'
        """

        soup: bs = self._get_soup_schedule()

        name: str = soup.find("div", {"class": "user-name"}).text

        return clean_data.remove_many_spaces(name)

    def get_amount_messages(self) -> int:
        """Возвращает количество непрочитанных сообщений

        :return: Количество непрочитанных сообщений
        :rtype: int

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_amount_messages()

        0
        """

        soup: bs = self._get_soup_schedule()

        amount_messages: str = soup.find("a", title="Личные сообщения")

        if amount_messages is None:
            return 0

        return int(clean_data.remove_many_spaces(amount_messages.text))

    def get_amount_notifications(self) -> int:
        """Возвращает количество непрочитанных уведомлений

        :return: Количество непрочитанных уведомлений
        :rtype: int

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_amount_notifications()

        0
        """

        soup: bs = self._get_soup_schedule()

        amount_notifications: str = soup.find("a", title="Уведомления")

        if amount_notifications is None:
            return 0

        return int(clean_data.remove_many_spaces(amount_notifications.text))

    def get_info(self) -> dict:
        """Возвращает информацию

        :return: Информация
        :rtype: dict

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_info()

        {
            "name": "Студент Демонстрационный",
            "amount_messages": 0,
            "amount_notifications": 0
        }
        """

        return {
            "name": self.get_name(),
            "amount_messages": self.get_amount_messages(),
            "amount_notifications": self.get_amount_notifications()
        }

    def get_schedule(self) -> dict:
        """Возвращает расписание
        
        :return: Расписание
        :rtype: list
        
        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_schedule()
        
        {
            "date": "2021-09-13" : {
                "time": "08:30 - 10:00",
                "name": "Математика",
                "classroom": "Ауд. 101",
                "type": "Лекция",
                "teacher": "Иванов И.И."
            }
        }
        """

        soup: bs = self._get_soup_schedule()

        table: bs = soup.find("table", {"class": "table-list v-scrollable"})
        shedule: dict = {}

        for tr in table.find("tbody").find_all("tr"):
            if len(tr.find_all("td")) == 1:
                return shedule
            if tr.find("th"):
                date: str = clean_data.remove_many_spaces(tr.find("th").text)
                shedule[date] = {}
            else:
                time: str = clean_data.remove_many_spaces(tr.find_all("td")[0].text)
                name: str = clean_data.remove_many_spaces(tr.find_all("td")[1].text)
                classroom: str = clean_data.remove_many_spaces(tr.find_all("td")[2].text)
                type_: str = clean_data.remove_many_spaces(tr.find_all("td")[3].text)
                teacher: str = clean_data.remove_many_spaces(tr.find_all("td")[4].text)

                shedule[date][time] = {
                    "name": name,
                    "classroom": classroom,
                    "type": type_,
                    "teacher": teacher
                }
                
        return shedule


if __name__ == "__main__":
    lms = LMS(login="demo", password="demo")
    print(lms.verify())
    print(lms.get_info())
    print(lms.get_schedule())
