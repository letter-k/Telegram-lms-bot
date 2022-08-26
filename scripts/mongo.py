import pymongo


class Database:
    def __init__(self, connstring):
        """Инициализация подключения к базе данных"""
        self.__connection = pymongo.MongoClient(connstring)
        self.__dbUser = self.__connection["test"]
        self.__collUser = self.__dbUser["users"]

    async def userAdd(self, user_id, email, password):
        """ "Добавление пользователя"""
        self.__collUser.insert_one(
            {"_id": user_id, "email": email, "password": password}
        )

    async def userDel(self, user_id):
        """Удаление пользователя"""
        self.__collUser.delete_one({"_id": user_id})

    async def userExsist(self, user_id):
        """Проверка наличия пользователя"""
        return self.__collUser.find_one({"_id": user_id})

    async def userInfo(self, user_id):
        """Получение информации о пользователе"""
        return self.__collUser.find_one({"_id": user_id})

    async def AllUser(self):
        """Получение всех пользователей"""
        return self.__collUser.find()
