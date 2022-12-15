from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
from create_bot import db
from keyboards import kb_client
from scripts import LMS
from asyncio import sleep
from datetime import datetime as dt


async def cmd_schedule(message: types.Message):
    if not await db.userExsist(message.from_user.id):
        await message.answer(
            f"❗ Вы не авторизованны",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        msg = await message.answer("⌛ Идёт загрузка ⌛")
        info = await db.userInfo(message.from_user.id)
        lms = LMS(info["email"], info["password"])
        schedule = lms.get_today_schedule()
        await msg.edit_text(f"Ваше расписание")
        for x, i in enumerate(schedule):
            if x == 0:
                if not i[:-6] == dt.today().strftime("%d.%m"):
                    await msg.answer("Сегодня у вас нет пар")
                    break
                await message.answer(
                    i, reply_markup=await kb_client(await db.userExsist(message.from_id))
                )
            elif x == 1:
                for y in i:
                    await message.answer(
                        y, reply_markup=await kb_client(await db.userExsist(message.from_id))
                    )


async def cmd_info(message: types.Message):
    if not await db.userExsist(message.from_user.id):
        await message.answer(
            f"❗ Вы не авторизованны",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        msg = await message.answer("⌛ Идёт загрузка ⌛")
        info = await db.userInfo(message.from_user.id)
        lms = LMS(info["email"], info["password"])
        info = lms.get_info_user()
        await msg.edit_text(
            f"👤 Ваша информация\nВас зовут  {info['name']}\n\n📩 Сообщений: {info['message']}\n\n🔔 Уведомлений: {info['notify']}"
        )


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_schedule, Text(equals="Расписание на сегодня"))
    dp.register_message_handler(cmd_info, Text(equals="Информация"))
