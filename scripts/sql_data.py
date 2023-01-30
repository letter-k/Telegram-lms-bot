from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table


class Database:
    metadata: MetaData = MetaData()

    users: Table = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("email", String(50)),
        Column("password", String(50)),
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

    async def userAdd(self, user_id: int, email: str, password: str) -> None:
        """Добавление пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :param email: Email пользователя
        :type email: str

        :param password: Пароль пользователя
        :type password: str

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.userAdd(1, "demo", "demo")
        """

        self.__connection.execute(
            self.users.insert().values(id=user_id, email=email, password=password)
        )
        self.__connection.commit()

    async def userDel(self, user_id: int) -> None:
        """Удаление пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.userDel(1)
        """

        self.__connection.execute(self.users.delete().where(self.users.c.id == user_id))
        self.__connection.commit()

    async def userExsist(self, user_id: int) -> bool:
        """Проверка наличия пользователя

        :param user_id: ID пользователя
        :type user_id: int

        :return: True - пользователь существует, False - пользователь не существует
        :rtype: bool

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.userExsist(1)

        True
        """

        return (
            self.__connection.execute(
                self.users.select().where(self.users.c.id == user_id)
            ).fetchone()
            is not None
        )

    async def userInfo(self, user_id: int) -> dict:
        """Получение информации о пользователе

        :param user_id: ID пользователя
        :type user_id: int

        :return: Возвращает информацию о пользователе
        :rtype: dict

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.userInfo(1)

        {
            "id": 1,
            "email": "demo",
            "password": "demo"
        }
        """

        result: tuple = self.__connection.execute(
            self.users.select().where(self.users.c.id == user_id)
        ).fetchone()

        return {"id": result[0], "email": result[1], "password": result[2]}

    async def AllUser(self) -> list:
        """Получение всех пользователей

        :return: Возвращает список всех пользователей
        :rtype: list

        :Example:

        >>> from sql_data import Database
        >>> db = Database()
        >>> db.AllUser()

        [
            {
                "id": 1,
                "email": "demo",
                "password": "demo"
            },
            {
                "id": 2,
                "email": "demo2",
                "password": "demo2"
            }
        ]
        """

        return self.__connection.execute(self.users.select()).fetchall()
