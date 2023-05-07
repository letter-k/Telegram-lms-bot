from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table


class Database:
    metadata: MetaData = MetaData()

    users: Table = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("email", String(50)),
        Column("password", String(50)),
        Column("type_user", String(50)),
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

        return self.__connection.execute(self.users.select()).fetchall()
