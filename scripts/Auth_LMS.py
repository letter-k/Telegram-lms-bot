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
        "en": "%s/user/lng/2" % _URL,
    }

    session: Session = None

    def __init__(
        self,
        login: str = "demo",
        password: str = "demo",
        proxy: dict = None,
        headers: dict = None,
        leanguage: str = "en",
    ) -> None:
        """Init LMS

        :param login: Login
        :param password: Login
        :param proxy: Proxy
        :param headers: Headers
        :param leanguage: Leanguage

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
        'Student Demonstratsionnyiy'
        """

        self.login = login
        self.password = password
        self.proxy = proxy
        self.headers = headers

        if leanguage not in self._URLS_LEANGUAGES:
            raise ValueError("Leanguage not found")
        self.leanguage = leanguage

        self.__sign()

    def __del__(self) -> None:
        """Close session

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
        """Auth

        :return: None
        :rtype: None

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms._LMS__sign()
        """

        headers: dict = (
            self.headers if self.headers else {"User-Agent": UserAgent().random}
        )
        proxies: dict = self.proxy if self.proxy else {}

        data: dict = {"popupUsername": self.login, "popupPassword": self.password}

        self.session = Session()
        self.session.headers.update(headers)
        self.session.post(self._URL_LOGIN, data=data, proxies=proxies)
        self.session.get(self._URLS_LEANGUAGES[self.leanguage], proxies=proxies)

    @property
    def cookies(self) -> dict:
        """Returns cookies

        :return: Cookies
        :rtype: dict

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.cookies
        """

        return self.session.cookies.get_dict()

    @cookies.setter
    def cookies(self, cookies: dict) -> None:
        """Set cookies

        :param cookies: Cookies
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
        """Returns soup schedule

        :return: Soup schedule
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
        """Verify auth

        :return: True or False
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
        """Returns name

        :return: Name
        :rtype: str

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_name()

        'Student Demonstratsionnyiy'
        """

        soup: bs = self._get_soup_schedule()

        name: str = soup.find("div", {"class": "user-name"}).text

        return clean_data.remove_many_spaces(name)

    def get_amount_messages(self) -> int:
        """Returns amount messages

        :return: Amount messages
        :rtype: int

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_amount_messages()

        0
        """

        titles: dict = {
            "ru": "Личные сообщения",
            "en": "Private messages",
        }

        soup: bs = self._get_soup_schedule()

        amount_messages: str = soup.find("a", title=titles[self.leanguage])

        if amount_messages is None:
            return 0

        return int(clean_data.remove_many_spaces(amount_messages.text))

    def get_amount_notifications(self) -> int:
        """Returns amount notifications

        :return: Amount notifications
        :rtype: int

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_amount_notifications()

        0
        """

        titles: dict = {
            "ru": "Уведомления",
            "en": "Notifications",
        }

        soup: bs = self._get_soup_schedule()

        amount_notifications: str = soup.find("a", title=titles[self.leanguage])

        if amount_notifications is None:
            return 0

        return int(clean_data.remove_many_spaces(amount_notifications.text))

    def get_info(self) -> dict:
        """Returns information about user

        :return: Information about user
        :rtype: dict

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_info()

        {
            "name": "Student Demonstratsionnyiy",
            "amount_messages": 0,
            "amount_notifications": 0
        }
        """

        return {
            "name": self.get_name(),
            "amount_messages": self.get_amount_messages(),
            "amount_notifications": self.get_amount_notifications(),
        }

    def get_schedule(self) -> dict:
        """Returns schedule

        :return: Schedule
        :rtype: list

        :Example:

        >>> from Auth_LMS import LMS
        >>> lms = LMS(login="demo", password="demo")
        >>> lms.get_schedule()

        {
            "date": "30.01.23, Mon" : {
                "time": "08:30 - 10:00",
                "name": "Linear Algebra",
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
                classroom: str = clean_data.remove_many_spaces(
                    tr.find_all("td")[2].text
                )
                type_: str = clean_data.remove_many_spaces(tr.find_all("td")[3].text)
                teacher: str = clean_data.remove_many_spaces(tr.find_all("td")[4].text)

                shedule[date][time] = {
                    "name": name,
                    "classroom": classroom,
                    "type": type_,
                    "teacher": teacher,
                }

        return shedule


if __name__ == "__main__":
    lms = LMS(login="demo", password="demo")
    print(lms.verify())
    print(lms.get_info())
    print(lms.get_schedule())
