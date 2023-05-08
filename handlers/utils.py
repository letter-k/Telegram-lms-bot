from aiogram.dispatcher import FSMContext
from keyboards import ClientKeyboard
from aiogram import types
from create_bot import db


def login_required(func):
    async def wrapper(message: types.Message):
        if not await db.user_exsist(message.from_user.id):
            await message.answer(
                "❗ Вы не авторизованны",
                reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
            )
        else:
            await func(message)

    return wrapper


def login_required_fsm(func):
    async def wrapper(message: types.Message, state: FSMContext):
        if not await db.user_exsist(message.from_user.id):
            await state.finish()
            await message.answer(
                "❗ Вы не авторизованны",
                reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
            )
        else:
            await func(message, state)

    return wrapper


def login_required_callback(func):
    async def wrapper(query: types.CallbackQuery):
        if not await db.user_exsist(query.from_user.id):
            await query.answer("❗ Вы не авторизованны")
        else:
            await func(query)

    return wrapper


def login_required_callback_fsm(func):
    async def wrapper(query: types.CallbackQuery, state: FSMContext):
        if not await db.user_exsist(query.from_user.id):
            await state.finish()
            await query.answer("❗ Вы не авторизованны")
        else:
            await func(query, state)

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
