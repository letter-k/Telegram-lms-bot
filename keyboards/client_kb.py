from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Final
from create_bot import db


class ClientKeyboard:
    """Клавиатура для клиента"""

    __BTN_REG: Final[KeyboardButton] = KeyboardButton("Авторизация")
    __kb_reg: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    __kb_reg.add(__BTN_REG)

    __BTN_SCHEDULE: Final[KeyboardButton] = KeyboardButton("Расписание на сегодня")
    __BTN_MSG: Final[KeyboardButton] = KeyboardButton("Сообщения")
    __BTN_NOTIFY: Final[KeyboardButton] = KeyboardButton("Уведомления")
    __BTN_PER_CUR: Final[KeyboardButton] = KeyboardButton("Персональные кураторы")
    __BNT_NEWS: Final[KeyboardButton] = KeyboardButton("Новости")
    __BTN_INFO: Final[KeyboardButton] = KeyboardButton("Информация")
    __BTN_EXIT: Final[KeyboardButton] = KeyboardButton("Выйти")

    __BTN_CANCEL: Final[KeyboardButton] = KeyboardButton("Отмена")
    __kb_cancel: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
    __kb_cancel.add(__BTN_CANCEL)

    __BTN_NEXT_MSG: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "➡️", callback_data="next_msg"
    )
    __BTN_PREV_MSG: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "⬅️", callback_data="prev_msg"
    )
    __BTN_EXIT_MSG: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "❌", callback_data="exit_msg"
    )

    __BTN_NEXT_NOTIFY: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "➡️", callback_data="next_notify"
    )
    __BTN_PREV_NOTIFY: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "⬅️", callback_data="prev_notify"
    )
    __BTN_EXIT_NOTIFY: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "❌", callback_data="exit_notify"
    )

    __BTN_NEXT_NEWS: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "➡️", callback_data="next_news"
    )
    __BTN_PREV_NEWS: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "⬅️", callback_data="prev_news"
    )
    __BTN_EXIT_NEWS: Final[InlineKeyboardButton] = InlineKeyboardButton(
        "❌", callback_data="exit_news"
    )

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

        type_user: str = await db.get_type_user(self.__user_id)

        if type_user == "student":
            return await self.kb_stats_student()
        elif type_user == "teacher":
            return await self.kb_stats_teacher()

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
    async def kb_stats_student(cls) -> ReplyKeyboardMarkup:
        """Клавиатура для статистики студента

        :return: Клавиатура
        :rtype: ReplyKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> ClientKeyboard.kb_stats_student()
        """

        kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(
            cls.__BTN_SCHEDULE,
            cls.__BTN_MSG,
            cls.__BTN_NOTIFY,
            cls.__BTN_PER_CUR,
            cls.__BNT_NEWS,
            cls.__BTN_INFO,
            cls.__BTN_EXIT,
        )
        return kb

    @classmethod
    async def kb_stats_teacher(cls) -> ReplyKeyboardMarkup:
        """Клавиатура для статистики преподавателя

        :return: Клавиатура
        :rtype: ReplyKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> ClientKeyboard.kb_stats_teacher()
        """

        kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(
            cls.__BTN_SCHEDULE,
            cls.__BTN_MSG,
            cls.__BTN_NOTIFY,
            cls.__BNT_NEWS,
            cls.__BTN_INFO,
            cls.__BTN_EXIT,
        )
        return kb

    @classmethod
    async def kb_message(cls, url: str) -> InlineKeyboardMarkup:
        """Клавиатура для сообщения

        :param url: Ссылка на сообщение
        :type

        :return: Клавиатура
        :rtype: InlineKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> kb = ClientKeyboard(1)
        >>> kb.kb_message("https://t.me/...")
        """

        kb: InlineKeyboardMarkup = InlineKeyboardMarkup()
        kb.add(
            cls.__BTN_EXIT_MSG,
            cls.__BTN_PREV_MSG,
            cls.__BTN_NEXT_MSG,
            InlineKeyboardButton("Перейти к сообщению", url=url),
        )
        return kb

    @classmethod
    async def kb_notify(cls) -> InlineKeyboardMarkup:
        """Клавиатура для уведомления

        :return: Клавиатура
        :rtype: InlineKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> kb = ClientKeyboard(1)
        >>> kb.kb_notify()
        """

        kb: InlineKeyboardMarkup = InlineKeyboardMarkup()
        kb.add(
            cls.__BTN_EXIT_NOTIFY,
            cls.__BTN_PREV_NOTIFY,
            cls.__BTN_NEXT_NOTIFY,
        )
        return kb

    @classmethod
    async def kb_news(cls, url: str) -> InlineKeyboardMarkup:
        """Клавиатура для новости

        :param url: Ссылка на новость
        :type

        :return: Клавиатура
        :rtype: InlineKeyboardMarkup

        :Example:

        >>> from keyboards import ClientKeyboard
        >>> kb = ClientKeyboard(1)
        >>> kb.kb_news("https://t.me/...")
        """

        kb: InlineKeyboardMarkup = InlineKeyboardMarkup()
        kb.add(
            cls.__BTN_EXIT_NEWS,
            cls.__BTN_PREV_NEWS,
            cls.__BTN_NEXT_NEWS,
            InlineKeyboardButton("Подробнее", url=url),
        )
        return kb
