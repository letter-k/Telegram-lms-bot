from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    MetaData,
    Table,
    ForeignKey,
    BigInteger,
)


class Database:
    metadata: MetaData = MetaData()

    users: Table = Table(
        "users",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("email", String(50)),
        Column("password", String(50)),
        Column("type_user", String(50)),
    )

    messages: Table = Table(
        "messages",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("user_id", BigInteger, ForeignKey("users.id")),
        Column("sender_name", String(50)),
        Column("subject", String(200)),
        Column("date", String(50)),
        Column("url", String(50)),
    )

    notifications: Table = Table(
        "notifications",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("user_id", BigInteger, ForeignKey("users.id")),
        Column("discipline", String(50)),
        Column("teacher", String(50)),
        Column("event", String(50)),
        Column("current_score", String(50)),
        Column("message", String(50)),
    )

    def __init__(self, connstring: str = "sqlite:///database.db") -> None:
        """Инициализация подключения к базе данных

        :param connstring: Строка подключения к базе данных
        :type connstring: str

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        """

        self.__engine = create_engine(connstring)
        self.__connection = self.__engine.connect()
        self.metadata.create_all(self.__connection)

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
            self.users.insert().values(
                id=user_id, email=email, password=password, type_user=type_user
            )
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

        self.__connection.execute(self.users.delete().where(self.users.c.id == user_id))
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
                self.users.select().where(self.users.c.id == user_id)
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
            self.users.select().where(self.users.c.id == user_id)
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
            self.users.select().where(self.users.c.id == user_id)
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

        result: list = self.__connection.execute(self.users.select()).fetchall()

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
            self.messages.insert().values(
                user_id=user_id,
                sender_name=sender_name,
                subject=subject,
                date=date,
                url=url,
            )
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
            self.messages.select().where(self.messages.c.user_id == user_id)
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
            self.messages.select()
            .where(self.messages.c.user_id == user_id)
            .limit(count)
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
            self.messages.select()
            .where(self.messages.c.user_id == user_id)
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
            self.messages.delete().where(self.messages.c.user_id == user_id)
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
            self.notifications.insert().values(
                user_id=user_id,
                discipline=discipline,
                teacher=teacher,
                event=event,
                current_score=current_score,
                message=message,
            )
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
            self.notifications.select().where(self.notifications.c.user_id == user_id)
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
