from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
from create_bot import db
from keyboards import kb_client
from lms_synergy_library import LMS
from asyncio import sleep
from datetime import datetime as dt


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


async def cmd_schedule(message: types.Message):
    if not await db.userExsist(message.from_user.id):
        await message.answer(
            f"❗ Вы не авторизованны",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        msg = await message.answer("⌛ Идёт загрузка ⌛")
        info = await db.userInfo(message.from_user.id)
        lms = LMS(info["email"], info["password"], leanguage="ru")
        schedule = lms.get_schedule()
        date = correct_date.correct_date(dt.now().strftime("%d.%m.%y, %a"))
        if date in schedule:
            await msg.edit_text(f"📝 Расписание на сегодня")
            lessons, times = schedule[date], schedule[date].keys()
            for time in times:
                await message.answer(
                    "🕒 Начало пары: %s \n📚 Дисциплина: %s \n🏫 Аудитория: %s \n📝 Тип пары: %s \n👨‍🏫 Преподаватель: %s"
                    % (
                        time,
                        lessons[time]["name"],
                        lessons[time]["classroom"],
                        lessons[time]["type"],
                        lessons[time]["teacher"],
                    )
                )
                await sleep(0.5)
        else:
            await message.answer("У вас нет пар на сегодня")


async def cmd_info(message: types.Message):
    if not await db.userExsist(message.from_user.id):
        await message.answer(
            f"❗ Вы не авторизованны",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        msg = await message.answer("⌛ Идёт загрузка ⌛")
        info = await db.userInfo(message.from_user.id)
        lms = LMS(info["email"], info["password"], leanguage="ru")
        info = lms.get_info()
        await msg.edit_text(
            f"👤 Ваша информация\nВас зовут  {info['name']}\n\n📩 Сообщений: {info['amount_messages']}\n\n🔔 Уведомлений: {info['amount_notifications']}"
        )


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_schedule, Text(equals="Расписание на сегодня"))
    dp.register_message_handler(cmd_info, Text(equals="Информация"))
