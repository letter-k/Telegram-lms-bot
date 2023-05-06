from aiogram import types
from keyboards import kb_client
from create_bot import db


def login_required(func):
    async def wrapper(message: types.Message):
        if not await db.user_exsist(message.from_user.id):
            await message.answer(
                "❗ Вы не авторизованны",
                reply_markup=await kb_client(await db.user_exsist(message.from_id)),
            )
        else:
            await func(message)

    return wrapper


class correct_date:
    @staticmethod
    def correct_date(date: str) -> str:
        """Корректировка даты

        :param date: Дата
        :type date: str

        :return: Корректированная дата
        :rtype: str

        :Example:

        >>> from scripts import correct_date
        >>> correct_date.correct_date("01.01.21, Mon")
        "01.01.21, пн"
        """

        day_of_week = {
            "пн": "Mon",
            "вт": "Tue",
            "ср": "Wed",
            "чт": "Thu",
            "пт": "Fri",
            "сб": "Sat",
            "вс": "Sun",
            "Mon": "пн",
            "Tue": "вт",
            "Wed": "ср",
            "Thu": "чт",
            "Fri": "пт",
            "Sat": "сб",
            "Sun": "вс",
        }

        date = date.split(", ")
        date[1] = day_of_week[date[1]]
        date = ", ".join(date)

        return date
