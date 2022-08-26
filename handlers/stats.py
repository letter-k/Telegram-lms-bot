from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
from create_bot import db
from keyboards import kb_client
from scripts import LMS


async def cmd_schedule(message: types.Message):
    if not await db.userExsist(message.from_user.id):
        await message.answer(
            f"❗ Вы не авторизованны",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        msg = await message.answer("⌛ Идёт загрузка ⌛")
        info = await db.userInfo(message.from_user.id)
        schedule = await LMS.get_schedule(info["email"], info["password"])
        await msg.edit_text(f"📈 Ваша статистика\n\n{schedule[0][0]}")


async def cmd_exit(message: types.Message):
    if not await db.userExsist(message.from_user.id):
        await message.answer(
            f"❗ Вы не авторизованны",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        await db.userDel(message.from_user.id)
        await message.answer(
            "❗ Вы успешно вышли из аккаунта",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_schedule, Text(equals="Расписание на сегодня"))
    dp.register_message_handler(cmd_exit, Text(equals="Выйти"))
