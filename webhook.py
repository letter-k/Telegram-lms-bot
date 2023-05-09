from aiohttp import web
from lms_synergy_library import LMS
from datetime import datetime as dt
from handlers.utils import correct_date
from asyncio import sleep
from keyboards import ClientKeyboard
from datetime import timedelta
from aiohttp.web import Request, Response
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot
from scripts import Database


load_dotenv()

app = web.Application()

bot = Bot(token=getenv("TOKEN"))
db = Database(getenv("CONNECTIONSTRING"))


async def send_schedule(request: Request):
    users = await db.all_user()
    for user in users:
        lms = LMS(user["email"], user["password"], language="ru")
        schedule = lms.get_schedule()
        date = correct_date.correct_date(dt.now().strftime("%d.%m.%y, %a"))
        await bot.send_message(user["id"], "Расписание на сегодня:")

        if date in schedule:
            lessons, times = schedule[date], schedule[date].keys()
            if lms.type_user == "студент":
                for time in times:
                    await bot.send_message(
                        user["id"],
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
                    await bot.send_message(
                        user["id"],
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
            await bot.send_message(user["id"], "У вас нет пар на сегодня")

    return Response(text="Successfull sended!")


async def send_schedule_tomorrow(request: Request):
    users = await db.all_user()
    for user in users:
        lms = LMS(user["email"], user["password"], language="ru")
        schedule = lms.get_schedule()
        date_tommorow = correct_date.correct_date(
            (dt.now() + timedelta(days=1)).strftime("%d.%m.%y, %a")
        )
        await bot.send_message(user["id"], "Расписание на завтра:")

        if date_tommorow in schedule:
            lessons, times = schedule[date_tommorow], schedule[date_tommorow].keys()
            if lms.type_user == "студент":
                for time in times:
                    await bot.send_message(
                        user["id"],
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
                    await bot.send_message(
                        user["id"],
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
            await bot.send_message(user["id"], "У вас нет пар на завтра")

    return Response(text="Successfull sended!")


app.router.add_post("/schedule_today", send_schedule)
app.router.add_post("/schedule_tomorrow", send_schedule_tomorrow)

if __name__ == "__main__":
    web.run_app(app, host=getenv("HOST"), port=getenv("PORT"))
