from sqlalchemy import create_engine, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import Optional, List
from sqlalchemy.orm import backref
from sqlalchemy.orm import Mapped


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(50))
    type_user: Mapped[str] = mapped_column(String(50))

    messages: Mapped[List["Message"]] = relationship(
        "Message", cascade="all, delete-orphan", backref="parent"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", cascade="all, delete-orphan", backref="parent"
    )
    news: Mapped[List["News"]] = relationship(
        "News", cascade="all, delete-orphan", backref="parent"
    )

    def __init__(self, id: int, email: str, password: str, type_user: str) -> None:
        self.id = id
        self.email = email
        self.password = password
        self.type_user = type_user


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    sender_name: Mapped[str] = mapped_column(String(50))
    subject: Mapped[str] = mapped_column(String(200))
    date: Mapped[str] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(String(50))

    user: Mapped["User"] = relationship(
        "User", backref=backref("messages", cascade="all, delete-orphan")
    )

    def __init__(
        self, user_id: int, sender_name: str, subject: str, date: str, url: str
    ) -> None:
        self.user_id = user_id
        self.sender_name = sender_name
        self.subject = subject
        self.date = date
        self.url = url


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    discipline: Mapped[str] = mapped_column(String(255))
    teacher: Mapped[str] = mapped_column(String(255))
    event: Mapped[str] = mapped_column(String(255))
    current_score: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String(255))

    user: Mapped["User"] = relationship(
        "User", backref=backref("notifications", cascade="all, delete-orphan")
    )

    def __init__(
        self,
        user_id: int,
        discipline: str,
        teacher: str,
        event: str,
        current_score: str,
        message: str,
    ) -> None:
        self.user_id = user_id
        self.discipline = discipline
        self.teacher = teacher
        self.event = event
        self.current_score = current_score
        self.message = message


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String(100))
    link: Mapped[str] = mapped_column(String(255))

    user = relationship("User", backref=backref("news", cascade="all, delete-orphan"))

    def __init__(
        self, user_id: int, title: str, description: str, date: str, link: str
    ) -> None:
        self.user_id = user_id
        self.title = title
        self.description = description
        self.date = date
        self.link = link


class Database:
    def __init__(self, connstring: Optional[str] = "sqlite:///database.db"):
        """Инициализация базы данных

        :param connstring: строка подключения, defaults to "sqlite:///database.db"
        :type connstring: str, optional

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        """

        self.engine = create_engine(connstring)
        self.__connection = self.engine.connect()
        Base.metadata.create_all(self.engine)

    def __del__(self):
        self.__connection.close()

    def user_add(self, user_id: int, email: str, password: str, type_user: str) -> None:
        """Добавление пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :param email: Email пользователя
        :type email: str

        :param password: Пароль пользователя
        :type password: str

        :param type_user: Тип пользователя
        :type type_user: str

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.user_add(1, "demo", "demo", "student")
        """

        self.__connection.execute(
            User.__table__.insert(),
            [
                {
                    "id": user_id,
                    "email": email,
                    "password": password,
                    "type_user": type_user,
                }
            ],
        )
        self.__connection.commit()

    def user_del(self, user_id: int) -> None:
        """Удаление пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.user_del(1)
        """

        self.__connection.execute(User.__table__.delete().where(User.id == user_id))
        self.__connection.commit()

    async def user_exsist(self, user_id: int) -> bool:
        """Проверка наличия пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: True - пользователь существует, False - пользователь не существует
        :rtype: bool

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.user_exsist(1)

        True
        """

        return (
            self.__connection.execute(
                User.__table__.select().where(User.id == user_id)
            ).fetchone()
            is not None
        )

    async def get_type_user(self, user_id: int) -> str:
        """Получение типа пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: Возвращает тип пользователя
        :rtype: str

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.get_type_user(1)

        "student"
        """

        return self.__connection.execute(
            User.__table__.select().where(User.id == user_id)
        ).fetchone()[3]

    async def user_info(self, user_id: int) -> dict:
        """Получение информации о пользователе

        :param user_id: ID пользователя
        :type user_id: int

        :return: Возвращает информацию о пользователе
        :rtype: dict

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.user_info(1)

        {
            "id": 1,
            "email": "demo",
            "password": "demo",
            "type_user": "student"
        }
        """

        result: tuple = self.__connection.execute(
            User.__table__.select().where(User.id == user_id)
        ).fetchone()

        return {"id": result[0], "email": result[1], "password": result[2]}

    async def all_user(self) -> list:
        """Получение всех пользователей

        :return: Возвращает список всех пользователей
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.all_user()

        [
            {
                "id": 1,
                "email": "demo",
                "password": "demo",
                "type_user": "student"
            },
            {
                "id": 2,
                "email": "demo2",
                "password": "demo2",
                "type_user": "student"
            }
        ]
        """

        result: list = self.__connection.execute(User.__table__.select()).fetchall()

        return [
            {"id": i[0], "email": i[1], "password": i[2], "type_user": i[3]}
            for i in result
        ]

    def add_message(
        self, user_id: int, sender_name: str, subject: str, date: str, url: str
    ) -> None:
        """Добавление сообщения

        :param user_id: ID пользователя
        :type user_id: int

        :param sender_name: Имя отправителя
        :type sender_name: str

        :param subject: Тема сообщения
        :type subject: str

        :param date: Дата сообщения
        :type date: str

        :param url: Ссылка на сообщение
        :type url: str

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.add_message(1, "demo", "demo", "demo", "demo")
        """

        self.__connection.execute(
            Message.__table__.insert(),
            [
                {
                    "user_id": user_id,
                    "sender_name": sender_name,
                    "subject": subject,
                    "date": date,
                    "url": url,
                }
            ],
        )
        self.__connection.commit()

    async def all_messages_user(self, user_id: int) -> list:
        """Получение всех сообщений пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: Возвращает список всех сообщений пользователя
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.all_messages_user(1)

        [
            {
                "id": 1,
                "user_id": 1,
                "sender_name": "demo",
                "subject": "demo",
                "date": "demo",
                "url": "demo"
            },
        ]
        """

        result: list = self.__connection.execute(
            Message.__table__.select().where(Message.user_id == user_id)
        ).fetchall()

        return [
            {
                "id": i[0],
                "user_id": i[1],
                "sender_name": i[2],
                "subject": i[3],
                "date": i[4],
                "url": i[5],
            }
            for i in result
        ]

    async def many_messages_user(self, user_id: int, count: int) -> list:
        """Получение нескольких сообщений пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :param count: Количество сообщений
        :type count: int

        :return: Возвращает список нескольких сообщений пользователя
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.many_messages_user(1, 1)

        [
            {
                "id": 1,
                "user_id": 1,
                "sender_name": "demo",
                "subject": "demo",
                "date": "demo",
                "url": "demo"
            },
        ]
        """

        result: list = self.__connection.execute(
            Message.__table__.select().where(Message.user_id == user_id).limit(count)
        ).fetchall()

        return [
            {
                "id": i[0],
                "user_id": i[1],
                "sender_name": i[2],
                "subject": i[3],
                "date": i[4],
                "url": i[5],
            }
            for i in result
        ]

    async def slice_messages_user(self, user_id: int, start: int, end: int) -> list:
        """Получение нескольких сообщений пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :param start: Начало среза
        :type start: int

        :param end: Конец среза
        :type end: int

        :return: Возвращает список нескольких сообщений пользователя
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.slice_messages_user(1, 0, 1)

        [
            {
                "id": 1,
                "user_id": 1,
                "sender_name": "demo",
                "subject": "demo",
                "date": "demo",
                "url": "demo"
            },
        ]
        """

        result: list = self.__connection.execute(
            Message.__table__.select()
            .where(Message.user_id == user_id)
            .slice(start, end)
        ).fetchall()

        return [
            {
                "id": i[0],
                "user_id": i[1],
                "sender_name": i[2],
                "subject": i[3],
                "date": i[4],
                "url": i[5],
            }
            for i in result
        ]

    def del_all_messages_user(self, user_id: int) -> None:
        """Удаление всех сообщений пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.del_all_messages_user(1)
        """

        self.__connection.execute(
            Message.__table__.delete().where(Message.user_id == user_id)
        )
        self.__connection.commit()

    def add_notify(
        self,
        user_id: int,
        discipline: str,
        teacher: str,
        event: str,
        current_score: str,
        message: str,
    ) -> None:
        """Добавление уведомления

        :param user_id: ID пользователя
        :type user_id: int

        :param discipline: Дисциплина
        :type discipline: str

        :param teacher: Преподаватель
        :type teacher: str

        :param event: Мероприятие
        :type event: str

        :param current_score: Текущая оценка
        :type current_score: str

        :param message: Сообщение
        :type message: str

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.add_notify(1, "demo", "demo", "demo", "demo", "demo")
        """

        self.__connection.execute(
            Notification.__table__.insert(),
            [
                {
                    "user_id": user_id,
                    "discipline": discipline,
                    "teacher": teacher,
                    "event": event,
                    "current_score": current_score,
                    "message": message,
                }
            ],
        )
        self.__connection.commit()

    async def all_notify_user(self, user_id: int) -> list:
        """Получение всех уведомлений пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: Возвращает список всех уведомлений пользователя
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.all_notify_user(1)

        [
            {
                "id": 1,
                "user_id": 1,
                "discipline": "demo",
                "teacher": "demo",
                "event": "demo",
                "current_score": "demo",
                "message": "demo"
            },
        ]
        """

        result: list = self.__connection.execute(
            Notification.__table__.select().where(Notification.user_id == user_id)
        ).fetchall()

        return [
            {
                "id": i[0],
                "user_id": i[1],
                "discipline": i[2],
                "teacher": i[3],
                "event": i[4],
                "current_score": i[5],
                "message": i[6],
            }
            for i in result
        ]

    def del_all_notify_user(self, user_id: int) -> None:
        """Удаление всех уведомлений пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.del_all_notify_user(1)
        """

        self.__connection.execute(
            Notification.__table__.delete().where(Notification.user_id == user_id)
        )
        self.__connection.commit()

    def add_news_user(
        self, user_id: int, title: str, description: str, date: str, link: str
    ) -> None:
        """Добавление новости

        :param user_id: ID пользователя
        :type user_id: int

        :param title: Заголовок
        :type title: str

        :param description: Описание
        :type description: str

        :param date: Дата
        :type date: str

        :param link: Ссылка
        :type link: str

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.add_news_user(1, "demo", "demo", "demo", "demo")
        """

        self.__connection.execute(
            News.__table__.insert(),
            [
                {
                    "user_id": user_id,
                    "title": title,
                    "description": description,
                    "date": date,
                    "link": link,
                }
            ],
        )
        self.__connection.commit()

    async def all_news_user(self, user_id: int) -> list:
        """Получение всех новостей пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: Возвращает список всех новостей пользователя
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.all_news_user(1)

        [

            {
                "id": 1,
                "user_id": 1,
                "title": "demo",
                "description": "demo",
                "date": "demo",
                "link": "demo"
            },
        ]
        """

        result: list = self.__connection.execute(
            News.__table__.select().where(News.user_id == user_id)
        ).fetchall()

        return [
            {
                "id": i[0],
                "user_id": i[1],
                "title": i[2],
                "description": i[3],
                "date": i[4],
                "link": i[5],
            }
            for i in result
        ]

    def del_all_news_user(self, user_id: int) -> None:
        """Удаление всех новостей пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.del_all_news_user(1)
        """

        self.__connection.execute(
            News.__table__.delete().where(News.user_id == user_id)
        )
        self.__connection.commit()

    def del_all_info_user(self, user_id: int) -> None:
        """Удаление всех данных пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.del_all_info_user(1)
        """

        self.__connection.execute(
            Message.__table__.delete().where(Message.user_id == user_id)
        )
        self.__connection.execute(
            Notification.__table__.delete().where(Notification.user_id == user_id)
        )
        self.__connection.execute(
            News.__table__.delete().where(News.user_id == user_id)
        )
        self.__connection.execute(User.__table__.delete().where(User.id == user_id))
        self.__connection.commit()
