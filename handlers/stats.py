from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers.utils import correct_date, login_required_fsm
from handlers.utils import login_required_callback_fsm
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


class Notify(StatesGroup):
    notify = State()


class News(StatesGroup):
    news = State()


class Event(StatesGroup):
    disciplines = State()
    events = State()


@login_required_fsm
async def cmd_schedule(message: types.Message, state: FSMContext):
    await state.finish()
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    schedule = lms.get_schedule()
    date = correct_date.correct_date(dt.now().strftime("%d.%m.%y, %a"))
    if date in schedule:
        await msg.delete()
        await message.answer("📝 Расписание на сегодня")
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
        await msg.delete()
        await message.answer(
            "У вас нет пар на сегодня",
            reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
        )


@login_required_fsm
async def cmd_info(message: types.Message, state: FSMContext):
    await state.finish()
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    info = lms.get_info()
    if lms.type_user == "студент":
        await msg.delete()
        await message.answer(
            f"👤 Ваша информация:\nВас зовут: {info['name']}\n\n📩 Сообщений: {info['amount_messages']}\n\n🔔 Уведомлений: {info['amount_notifications']}",
            reply_markup=await ClientKeyboard.kb_stats_student(),
        )
    elif lms.type_user == "преподаватель":
        amount_unverified_work = lms.get_amount_unverified_work()
        await msg.delete()
        await message.answer(
            f"👤 Ваша информация:\nВас зовут: {info['name']}\n\n💼 Работ на проверку: {amount_unverified_work}\n\n📩 Сообщений: {info['amount_messages']}\n\n🔔 Уведомлений: {info['amount_notifications']}",
            reply_markup=await ClientKeyboard.kb_stats_teacher(),
        )


@login_required_fsm
async def cmd_messages(message: types.Message, state: FSMContext):
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
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
        await msg.delete()
        await state.finish()
        await message.answer(
            "📪 У вас нет новых сообщений 📪",
            reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
        )


@login_required_callback_fsm
async def cmd_exit_callback(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer(
        "Вы в главном меню",
        reply_markup=await ClientKeyboard(call.from_user.id).kb_client(),
    )


@login_required_callback_fsm
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


@login_required_callback_fsm
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


@login_required_callback_fsm
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
            reply_markup=await ClientKeyboard(call.from_user.id).kb_client(),
        )


@login_required_fsm
async def cmd_notifications(message: types.Message, state: FSMContext):
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    notifications = lms.get_notify()
    db.del_all_notify_user(message.from_user.id)
    await Notify.notify.set()

    for n in notifications:
        db.add_notify(
            user_id=message.from_user.id,
            discipline=n["discipline"],
            teacher=n["teacher"],
            event=n["event"],
            current_score=n["current_score"],
            message=n["message"],
        )

    if len(notifications) > 0:
        await state.update_data(notify=0)
        await msg.delete()
        await message.answer(
            "📚 %s\n\n 👨‍🏫 %s\n\n 📝 %s\n\n📊 Текущий балл: %s\n\n📄 %s"
            % (
                notifications[0]["discipline"],
                notifications[0]["teacher"],
                notifications[0]["event"],
                notifications[0]["current_score"],
                notifications[0]["message"],
            ),
            reply_markup=await ClientKeyboard.kb_notify(),
        )
    else:
        await msg.delete()
        await state.finish()
        await message.answer(
            "🔕 У вас нет новых уведомлений 🔕",
            reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
        )


@login_required_callback_fsm
async def cmd_next_notify(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    notify = data["notify"] + 1
    await state.update_data(notify=notify)
    notifications = await db.all_notify_user(call.from_user.id)
    if notify == len(notifications):
        notify = 0
        await state.update_data(notify=notify)
        await call.message.edit_text(
            "📚 %s\n\n 👨‍🏫 %s\n\n 📝 %s\n\n📊 Текущий балл: %s\n\n📄 %s"
            % (
                notifications[notify]["discipline"],
                notifications[notify]["teacher"],
                notifications[notify]["event"],
                notifications[notify]["current_score"],
                notifications[notify]["message"],
            ),
            reply_markup=await ClientKeyboard.kb_notify(),
        )
    else:
        await call.message.edit_text(
            "📚 %s\n\n 👨‍🏫 %s\n\n 📝 %s\n\n📊 Текущий балл: %s\n\n📄 %s"
            % (
                notifications[notify]["discipline"],
                notifications[notify]["teacher"],
                notifications[notify]["event"],
                notifications[notify]["current_score"],
                notifications[notify]["message"],
            ),
            reply_markup=await ClientKeyboard.kb_notify(),
        )


@login_required_callback_fsm
async def cmd_prev_notify(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    notify = data["notify"] - 1
    await state.update_data(notify=notify)
    notifications = await db.all_notify_user(call.from_user.id)
    if notify == -1:
        notify = len(notifications) - 1
        await state.update_data(notify=notify)
        await call.message.edit_text(
            "📚 %s\n\n 👨‍🏫 %s\n\n 📝 %s\n\n📊 Текущий балл: %s\n\n📄 %s"
            % (
                notifications[notify]["discipline"],
                notifications[notify]["teacher"],
                notifications[notify]["event"],
                notifications[notify]["current_score"],
                notifications[notify]["message"],
            ),
            reply_markup=await ClientKeyboard.kb_notify(),
        )
    else:
        await call.message.edit_text(
            "📚 %s\n\n 👨‍🏫 %s\n\n 📝 %s\n\n📊 Текущий балл: %s\n\n📄 %s"
            % (
                notifications[notify]["discipline"],
                notifications[notify]["teacher"],
                notifications[notify]["event"],
                notifications[notify]["current_score"],
                notifications[notify]["message"],
            ),
            reply_markup=await ClientKeyboard.kb_notify(),
        )


@login_required_callback_fsm
async def cmd_next_ex_fsm_notify(call: types.CallbackQuery, state: FSMContext):
    notifications = await db.all_notify_user(call.from_user.id)
    await Notify.notify.set()
    await state.update_data(notify=0)

    if len(notifications) > 0:
        await call.message.edit_text(
            "📚 %s\n\n 👨‍🏫 %s\n\n 📝 %s\n\n📊 Текущий балл: %s\n\n📄 %s"
            % (
                notifications[0]["discipline"],
                notifications[0]["teacher"],
                notifications[0]["event"],
                notifications[0]["current_score"],
                notifications[0]["message"],
            ),
            reply_markup=await ClientKeyboard.kb_notify(),
        )
    else:
        await state.finish()
        await call.message.delete()
        await call.message.answer(
            "🔕 У вас нет новых уведомлений 🔕",
            reply_markup=await ClientKeyboard(call.from_user.id).kb_client(),
        )


@login_required_fsm
async def cmd_news(message: types.Message, state: FSMContext):
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    news = lms.get_news()
    db.del_all_news_user(message.from_user.id)
    await News.news.set()

    for new in news:
        db.add_news_user(
            user_id=message.from_user.id,
            title=new["title"],
            description=new["description"],
            date=new["date"],
            link=new["link"],
        )

    if len(news) > 0:
        await state.update_data(news=0)
        await msg.delete()
        await message.answer(
            "📰 %s\n\n📅 %s\n\n📄 %s"
            % (
                news[0]["title"],
                news[0]["date"],
                news[0]["description"],
            ),
            reply_markup=await ClientKeyboard.kb_news(news[0]["link"]),
        )
    else:
        await msg.delete()
        await state.finish()
        await message.answer(
            "📰 Новостей нет 📰",
            reply_markup=await ClientKeyboard(message.from_user.id).kb_client(),
        )


@login_required_callback_fsm
async def cmd_next_news(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    news = data["news"] + 1
    await state.update_data(news=news)
    user_news = await db.all_news_user(call.from_user.id)
    if news == len(user_news):
        news = 0
        await state.update_data(news=news)
        await call.message.edit_text(
            "📰 %s\n\n📅 %s\n\n📄 %s"
            % (
                user_news[news]["title"],
                user_news[news]["date"],
                user_news[news]["description"],
            ),
            reply_markup=await ClientKeyboard.kb_news(user_news[news]["link"]),
        )
    else:
        await call.message.edit_text(
            "📰 %s\n\n📅 %s\n\n📄 %s"
            % (
                user_news[news]["title"],
                user_news[news]["date"],
                user_news[news]["description"],
            ),
            reply_markup=await ClientKeyboard.kb_news(user_news[news]["link"]),
        )


@login_required_callback_fsm
async def cmd_prev_news(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    news = data["news"] - 1
    await state.update_data(news=news)
    user_news = await db.all_news_user(call.from_user.id)
    if news == -1:
        news = len(user_news) - 1
        await state.update_data(news=news)
        await call.message.edit_text(
            "📰 %s\n\n📅 %s\n\n📄 %s"
            % (
                user_news[news]["title"],
                user_news[news]["date"],
                user_news[news]["description"],
            ),
            reply_markup=await ClientKeyboard.kb_news(user_news[news]["link"]),
        )
    else:
        await call.message.edit_text(
            "📰 %s\n\n📅 %s\n\n📄 %s"
            % (
                user_news[news]["title"],
                user_news[news]["date"],
                user_news[news]["description"],
            ),
            reply_markup=await ClientKeyboard.kb_news(user_news[news]["link"]),
        )


@login_required_callback_fsm
async def cmd_next_ex_fsm_news(call: types.CallbackQuery, state: FSMContext):
    news = await db.all_news_user(call.from_user.id)
    await News.news.set()
    await state.update_data(news=0)

    if len(news) > 0:
        await call.message.edit_text(
            "📰 %s\n\n📅 %s\n\n📄 %s"
            % (
                news[0]["title"],
                news[0]["date"],
                news[0]["description"],
            ),
            reply_markup=await ClientKeyboard.kb_news(news[0]["link"]),
        )
    else:
        await state.finish()
        await call.message.edit_text("📰 Новостей нет 📰")


@login_required_fsm
async def cmd_personal_curators(message: types.Message, state: FSMContext):
    await state.finish()
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    curators = lms.get_pesonal_curators()
    if len(curators) > 0:
        await msg.delete()
        await message.answer("Ваши кураторы:")
        for curator in curators:
            phones = "".join(["📞 %s\n" % phone for phone in curator["phones"]])

            emails = "".join(["📧 %s\n" % email for email in curator["emails"]])

            await message.answer(
                "👨‍🏫 %s\n\n%s\n%s"
                % (
                    curator["name"],
                    phones,
                    emails,
                ),
                reply_markup=await ClientKeyboard.kb_stats_student(),
            )
    else:
        await msg.delete()
        await message.answer(
            "У вас нет персональных кураторов",
            reply_markup=await ClientKeyboard.kb_stats_student(),
        )


@login_required_fsm
async def cmd_tutors(message: types.Message, state: FSMContext):
    await state.finish()
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    tutors = lms.get_tutors()
    if len(tutors) > 0:
        await msg.delete()
        await message.answer("Ваши тьюторы:")
        for tutor in tutors:
            phones = "".join(["📞 %s\n" % phone for phone in tutor["phones"]])

            emails = "".join(["📧 %s\n" % email for email in tutor["emails"]])

            await message.answer(
                "👨‍🏫 %s\n\n%s\n%s"
                % (
                    tutor["name"],
                    phones,
                    emails,
                ),
                reply_markup=await ClientKeyboard.kb_stats_student(),
            )
    else:
        await msg.delete()
        await message.answer(
            "У вас нет тьюторов", reply_markup=await ClientKeyboard.kb_stats_student()
        )


@login_required_fsm
async def cmd_mark(message: types.Message, state: FSMContext):
    await state.finish()
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    mark = lms.get_marks()
    if mark:
        await msg.delete()
        await message.answer(
            "Ваши отметки:", reply_markup=await ClientKeyboard.kb_stats_student()
        )
        for i in mark:
            await message.answer(
                f"📍 {i['discipline']} - {i['type_discipline']}\n👨‍🏫 {i['teacher']}\n📅 {i['date_discipline']}\n⏰ {i['time_discipline']}\n✏️ Отметка: {i['mark']}"
            )
            await sleep(0.5)
    else:
        await msg.delete()
        await message.answer(
            "У вас сегодня нет отметок",
            reply_markup=await ClientKeyboard.kb_stats_student(),
        )


@login_required_fsm
async def cmd_disciplines(message: types.Message, state: FSMContext):
    await Event.disciplines.set()
    msg = await message.answer(
        "⌛ Идёт загрузка ⌛", reply_markup=types.ReplyKeyboardRemove()
    )
    info = await db.user_info(message.from_user.id)
    lms = LMS(info["email"], info["password"], language="ru")
    events = lms.get_events()
    await state.update_data(events=events)
    disciplines_keys = []
    for i in events:
        disciplines_keys.append(*i)
    await state.update_data(disciplines=disciplines_keys)
    await Event.events.set()
    await msg.delete()
    await message.answer(
        "Выбери дисциплины 👇",
        reply_markup=await ClientKeyboard.kb_disciplines(disciplines_keys),
    )


@login_required_fsm
async def cmd_events(message: types.Message, state: FSMContext):
    text = message.text
    user_data = await state.get_data()

    if text not in user_data["disciplines"]:
        return await message.answer(
            "Такой дисциплины нет",
            reply_markup=await ClientKeyboard.kb_disciplines(user_data["disciplines"]),
        )

    num_event = 0
    for i, k in enumerate(user_data["events"]):
        if list(k.keys())[0] == text:
            num_event = i
            break

    event = user_data["events"][num_event]
    for i in event[text]["events"]:
        await message.answer(
            f"📍 {i['name']}\n\n👉 Максимальный балл: {i['max_grade']}\n👉 Текущий балл: {i['result'].replace('-', '0')}\n\n🔒 {i['access']}"
        )
        await sleep(0.5)

    current_grade = event[text]["current_grade"]

    if not current_grade:
        current_grade = 0

    await message.answer(
        f"📍 Всего: {current_grade}",
        reply_markup=await ClientKeyboard.kb_disciplines(user_data["disciplines"]),
    )


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(
        cmd_schedule, Text(equals="Расписание на сегодня"), state="*"
    )
    dp.register_message_handler(cmd_info, Text(equals="Информация"), state="*")
    dp.register_message_handler(cmd_messages, Text(equals="Сообщения"), state="*")
    dp.register_callback_query_handler(
        cmd_exit_callback, Text(equals="exit_msg"), state="*"
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
    dp.register_message_handler(
        cmd_notifications, Text(equals="Уведомления"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_exit_callback, Text(equals="exit_notify"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_next_notify, Text(equals="next_notify"), state=Notify.notify
    )
    dp.register_callback_query_handler(
        cmd_prev_notify, Text(equals="prev_notify"), state=Notify.notify
    )
    dp.register_callback_query_handler(
        cmd_next_ex_fsm_notify, Text(equals="next_notify"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_next_ex_fsm_notify, Text(equals="prev_notify"), state="*"
    )
    dp.register_message_handler(cmd_news, Text(equals="Новости"), state="*")
    dp.register_callback_query_handler(
        cmd_exit_callback, Text(equals="exit_news"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_next_news, Text(equals="next_news"), state=News.news
    )
    dp.register_callback_query_handler(
        cmd_prev_news, Text(equals="prev_news"), state=News.news
    )
    dp.register_callback_query_handler(
        cmd_next_ex_fsm_news, Text(equals="next_news"), state="*"
    )
    dp.register_callback_query_handler(
        cmd_next_ex_fsm_news, Text(equals="prev_news"), state="*"
    )
    dp.register_message_handler(
        cmd_personal_curators, Text(equals="Персональные кураторы"), state="*"
    )
    dp.register_message_handler(cmd_tutors, Text(equals="Тьюторы"), state="*")
    dp.register_message_handler(cmd_mark, Text(equals="Отметка"), state="*")
    dp.register_message_handler(cmd_disciplines, Text(equals="Дисциплины"), state="*")
    dp.register_message_handler(cmd_events, state=Event.events)
