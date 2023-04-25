from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
from keyboards import kb_client, kb_cancel
from create_bot import db
from lms_synergy_library import LMS
from handlers.utils import login_required


class Auth(StatesGroup):
    user_id = State()
    email = State()
    password = State()


async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет я synergy.bot, и предоставляю ваше расписание с сайта lms.synegy.ru",
        reply_markup=await kb_client(await db.userExsist(message.from_id)),
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "❗ Действие отменено",
        reply_markup=await kb_client(await db.userExsist(message.from_id)),
    )


async def auth_step(message: types.Message, state: FSMContext):
    await Auth.user_id.set()
    await state.update_data(user_id=message.from_user.id)
    await Auth.email.set()
    await message.answer("📬 Введите email", reply_markup=kb_cancel)


async def pass_step(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await Auth.password.set()
    await message.answer("🔑 Введите пароль", reply_markup=kb_cancel)


async def res_step(message: types.Message, state: FSMContext):
    msg = await message.answer("⌛ Производится авторизация ⌛")
    await state.update_data(password=message.text)
    user_data = await state.get_data()
    lms = LMS(user_data["email"], user_data["password"])
    if lms.verify():
        await db.userAdd(
            user_data["user_id"], user_data["email"], user_data["password"]
        )
        await msg.edit_text("✅ Авторизация прошла успешно")
        await message.answer(
            "Для просмотра статистик используйте кнопки 👇",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    else:
        await msg.edit_text("❌ Авторизация не пройдена")
        await message.answer(
            "❗ Имя пользователя или пароль введены неверно",
            reply_markup=await kb_client(await db.userExsist(message.from_id)),
        )
    await state.finish()


@login_required
async def cmd_exit(message: types.Message):
    await db.userDel(message.from_user.id)
    await message.answer(
        "❗ Вы успешно вышли из аккаунта",
        reply_markup=await kb_client(await db.userExsist(message.from_id)),
    )


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start")
    dp.register_message_handler(cmd_cancel, commands="Отмена", state="*")
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*"
    )
    dp.register_message_handler(auth_step, Text(equals="Авторизация"), state="*")
    dp.register_message_handler(
        pass_step, state=Auth.email, content_types=types.ContentTypes.TEXT
    )
    dp.register_message_handler(
        res_step, state=Auth.password, content_types=types.ContentTypes.TEXT
    )
    dp.register_message_handler(cmd_exit, Text(equals="Выйти"))
