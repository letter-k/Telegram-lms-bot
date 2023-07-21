from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from handlers.utils import login_required_fsm
from aiogram import Dispatcher, types
from keyboards import ClientKeyboard
from lms_synergy_library import LMS
from create_bot import db


class Auth(StatesGroup):
    user_id = State()
    email = State()
    password = State()


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Привет я synergy.bot, и предоставляю ваше расписание с сайта lms.synegy.ru",
        reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "❗ Действие отменено",
        reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
    )


async def auth_step(message: types.Message, state: FSMContext):
    await Auth.user_id.set()
    await state.update_data(user_id=message.from_user.id)
    await Auth.email.set()
    await message.answer(
        "📬 Введите email", reply_markup=await ClientKeyboard.kb_cancel()
    )


async def pass_step(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await Auth.password.set()
    await message.answer(
        "🔑 Введите пароль", reply_markup=await ClientKeyboard.kb_cancel()
    )


async def res_step(message: types.Message, state: FSMContext):
    msg = await message.answer(
        "⌛ Производится авторизация ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.update_data(password=message.text)
    user_data = await state.get_data()
    lms = LMS(user_data["email"], user_data["password"])
    if lms.verify():
        db.user_add(
            user_data["user_id"],
            user_data["email"],
            user_data["password"],
            lms.type_user,
        )
        amount_msg = lms.get_amount_messages()
        amount_notif = lms.get_amount_notifications()
        await msg.delete()
        await message.answer(
            f"✅ Авторизация прошла успешно\n\n📬 У вас {amount_msg} новых сообщений\n🔔 У вас {amount_notif} новых уведомлений"
        )
        await message.answer(
            "Для просмотра статистик используйте кнопки 👇",
            reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
        )
    else:
        await message.answer("❌ Авторизация не пройдена")
        await message.answer(
            "❗ Имя пользователя или пароль введены неверно",
            reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
        )
    await state.finish()


@login_required_fsm
async def cmd_exit(message: types.Message, state: FSMContext):
    await state.finish()
    db.del_all_info_user(message.from_user.id)
    await message.answer(
        "❗ Вы успешно вышли из аккаунта",
        reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
    )


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
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
    dp.register_message_handler(cmd_exit, Text(equals="Выйти"), state="*")
