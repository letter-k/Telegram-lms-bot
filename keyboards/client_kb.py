from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from create_bot import db


class ClientKeyboard:
    """Клавиатура для клиента"""

    __btn_reg: KeyboardButton = KeyboardButton("Авторизация")
    __kb_reg: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    __kb_reg.add(__btn_reg)

    __btn_schedule: KeyboardButton = KeyboardButton("Расписание на сегодня")
    __btn_info: KeyboardButton = KeyboardButton("Информация")
    __btn_exit: KeyboardButton = KeyboardButton("Выйти")
    __kb_stats: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    __kb_stats.add(__btn_schedule).add(__btn_info).add(__btn_exit)

    __btn_cancel: KeyboardButton = KeyboardButton("Отмена")
    __kb_cancel: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    __kb_cancel.add(__btn_cancel)

    def __init__(self, user_id: int):
        """Инициализация

        :param user_id: ID пользователя
        :type user_id: int

        :return: None
        :rtype: None
        """

        self.__user_id = user_id

    async def kb_client(self) -> ReplyKeyboardMarkup:
        """Клавиатура для клиента

        :return: Клавиатура
        :rtype: ReplyKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> kb = ClientKeyboard(1)
        >>> kb.kb_client()
        """

        exists: bool = await db.user_exsist(self.__user_id)

        if not exists:
            return self.__kb_reg
        return self.__kb_stats

    @classmethod
    async def kb_cancel(cls) -> ReplyKeyboardMarkup:
        """Клавиатура для отмены

        :return: Клавиатура
        :rtype: ReplyKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> ClientKeyboard.kb_cancel()
        """

        return cls.__kb_cancel

    @classmethod
    async def kb_reg(cls) -> ReplyKeyboardMarkup:
        """Клавиатура для регистрации

        :return: Клавиатура
        :rtype: ReplyKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> ClientKeyboard.kb_reg()
        """

        return cls.__kb_reg

    @classmethod
    async def kb_stats(cls) -> ReplyKeyboardMarkup:
        """Клавиатура для статистики

        :return: Клавиатура
        :rtype: ReplyKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> ClientKeyboard.kb_stats()
        """

        return cls.__kb_stats
