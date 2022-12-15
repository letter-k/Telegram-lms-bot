from sqlalchemy import create_engine, Column, Integer, String, \
    MetaData, Table


class Database:
    """Класс для работы с базой данных"""

    metadata = MetaData()

    users = Table('users', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('email', String(50)),
                  Column('password', String(50)),
                  )

    def __init__(self, connstring):
        """Инициализация подключения к базе данных"""
        self.__connection = create_engine(connstring)
        self.metadata.create_all(self.__connection)

    async def userAdd(self, user_id, email, password):
        """ "Добавление пользователя"""
        self.__connection.execute(
            self.users.insert().values(
                id=user_id, email=email, password=password
            )
        )

    async def userDel(self, user_id):
        """Удаление пользователя"""
        self.__connection.execute(
            self.users.delete().where(
                self.users.c.id == user_id
            )
        )

    async def userExsist(self, user_id):
        """Проверка наличия пользователя"""
        return self.__connection.execute(
            self.users.select().where(
                self.users.c.id == user_id
            )
        ).fetchone()

    async def userInfo(self, user_id):
        """Получение информации о пользователе"""
        return self.__connection.execute(
            self.users.select().where(self.users.c.id == user_id)
        ).fetchone()

    async def AllUser(self):
        """Получение всех пользователей"""
        return self.__connection.execute(
            self.users.select()
        ).fetchall()
