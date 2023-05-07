from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers.utils import login_required, correct_date, login_required_fsm
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from keyboards import ClientKeyboard
from lms_synergy_library import LMS
from datetime import datetime as dt
from asyncio import sleep
from create_bot import db


class Msg(StatesGroup):
    msg = State()


@login_required
async def cmd_schedule(message: types.Message):
    msg = await message.answer("⌛ Идёт загрузка ⌛")
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    schedule = lms.get_schedule()
    date = correct_date.correct_date(dt.now().strftime("%d.%m.%y, %a"))
    if date in schedule:
        await msg.edit_text("📝 Расписание на сегодня")
        lessons, times = schedule[date], schedule[date].keys()
        if lms.type_user == "студент":
            for time in times:
                await message.answer(
                    "🕒 Начало пары: %s \n📚 Дисциплина: %s \n🏫 Аудитория: %s \n📝 Тип пары: %s \n👨‍🏫 Преподаватель: %s"
                    % (
                        time,
                        lessons[time]["name"],
                        lessons[time]["classroom"],
                        lessons[time]["type"],
                        lessons[time]["teacher"],
                    ),
                    reply_markup=await ClientKeyboard.kb_stats_student(),
                )
                await sleep(0.5)
        elif lms.type_user == "преподаватель":
            for time in times:
                await message.answer(
                    "🕒 Начало пары: %s \n📚 Дисциплина: %s \n👥 Группа: %s \n🏫 Аудитория: %s \n📝 Тип пары: %s"
                    % (
                        time,
                        lessons[time]["name"],
                        lessons[time]["group"],
                        lessons[time]["classroom"],
                        lessons[time]["type_lesson"],
                    ),
                    reply_markup=await ClientKeyboard.kb_stats_teacher(),
                )
                await sleep(0.5)
    else:
        await msg.edit_text("У вас нет пар на сегодня")


@login_required
async def cmd_info(message: types.Message):
    msg = await message.answer("⌛ Идёт загрузка ⌛")
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    info = lms.get_info()
    if lms.type_user == "студент":
        await msg.edit_text(
            f"👤 Ваша информация:\nВас зовут: {info['name']}\n\n📩 Сообщений: {info['amount_messages']}\n\n🔔 Уведомлений: {info['amount_notifications']}"
        )
    elif lms.type_user == "преподаватель":
        amount_unverified_work = lms.get_amount_unverified_work()
        await msg.edit_text(
            f"👤 Ваша информация:\nВас зовут: {info['name']}\n\n💼 Работ на проверку: {amount_unverified_work}\n\n📩 Сообщений: {info['amount_messages']}\n\n🔔 Уведомлений: {info['amount_notifications']}"
        )


@login_required_fsm
async def cmd_messages(message: types.Message, state: FSMContext):
    msg = await message.answer("⌛ Идёт загрузка ⌛")
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    messages = lms.get_unread_messages()
    db.del_all_messages_user(message.from_user.id)
    await Msg.msg.set()

    for m in messages:
        db.add_message(
            user_id=message.from_user.id,
            sender_name=m["sender_name"],
            subject=m["subject"],
            date=m["date"],
            url=m["url"],
        )

    if len(messages) > 0:
        await state.update_data(msg=0)
        await msg.delete()
        await message.answer(
            "%s\n\n отправитель: %s\n дата: %s"
            % (messages[0]["subject"], messages[0]["sender_name"], messages[0]["date"]),
            reply_markup=await ClientKeyboard.kb_message(messages[0]["url"]),
        )
    else:
        await state.finish()
        await msg.edit_text("📪 У вас нет новых сообщений 📪")


@login_required_fsm
async def cmd_exit_message(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer(
        "Вы в главном меню",
        reply_markup=await ClientKeyboard(call.from_user.id).kb_client(),
    )


@login_required_fsm
async def cmd_next_message(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg"] + 1
    await state.update_data(msg=msg)
    messages = await db.all_messages_user(call.from_user.id)
    if msg == len(messages):
        msg = 0
        await state.update_data(msg=msg)
        await call.message.edit_text(
            "%s\n\n отправитель: %s\n дата: %s"
            % (
                messages[msg]["subject"],
                messages[msg]["sender_name"],
                messages[msg]["date"],
            ),
            reply_markup=await ClientKeyboard.kb_message(messages[msg]["url"]),
        )
    else:
        await call.message.edit_text(
            "%s\n\n отправитель: %s\n дата: %s"
            % (
                messages[msg]["subject"],
                messages[msg]["sender_name"],
                messages[msg]["date"],
            ),
            reply_markup=await ClientKeyboard.kb_message(messages[msg]["url"]),
        )


@login_required_fsm
async def cmd_prev_message(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg"] - 1
    await state.update_data(msg=msg)
    messages = await db.all_messages_user(call.from_user.id)
    if msg == -1:
        msg = len(messages) - 1
        await state.update_data(msg=msg)
        await call.message.edit_text(
            "%s\n\n отправитель: %s\n дата: %s"
            % (
                messages[msg]["subject"],
                messages[msg]["sender_name"],
                messages[msg]["date"],
            ),
            reply_markup=await ClientKeyboard.kb_message(messages[msg]["url"]),
        )
    else:
        await call.message.edit_text(
            "%s\n\n отправитель: %s\n дата: %s"
            % (
                messages[msg]["subject"],
                messages[msg]["sender_name"],
                messages[msg]["date"],
            ),
            reply_markup=await ClientKeyboard.kb_message(messages[msg]["url"]),
        )


@login_required_fsm
async def cmd_next_ex_fsm(call: types.CallbackQuery, state: FSMContext):
    messages = await db.all_messages_user(call.from_user.id)
    await Msg.msg.set()
    await state.update_data(msg=0)

    if len(messages) > 0:
        await call.message.delete()
        await call.message.answer(
            "%s\n\n отправитель: %s\n дата: %s"
            % (messages[0]["subject"], messages[0]["sender_name"], messages[0]["date"]),
            reply_markup=await ClientKeyboard.kb_message(messages[0]["url"]),
        )

    else:
        await state.finish()
        await call.message.delete()
        await call.message.answer(
            "📪 У вас нет новых сообщений 📪",
            ClientKeyboard(call.from_user.id).kb_client(),
        )


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_schedule, Text(equals="Расписание на сегодня"))
    dp.register_message_handler(cmd_info, Text(equals="Информация"))
    dp.register_message_handler(cmd_messages, Text(equals="Сообщения"), state="*")
    dp.register_callback_query_handler(
        cmd_exit_message, Text(equals="exit_msg"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_next_message, Text(equals="next_msg"), state=Msg.msg
    )
    dp.register_callback_query_handler(
        cmd_prev_message, Text(equals="prev_msg"), state=Msg.msg
    )
    dp.register_callback_query_handler(
        cmd_next_ex_fsm, Text(equals="next_msg"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_next_ex_fsm, Text(equals="prev_msg"), state="*"
    )
