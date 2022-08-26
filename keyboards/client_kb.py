from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


but_reg = KeyboardButton("Авторизация")
kb_reg = ReplyKeyboardMarkup(resize_keyboard=True)
kb_reg.add(but_reg)


but_schedule = KeyboardButton("Расписание на сегодня")
but_exit = KeyboardButton("Выйти")
kb_stats = ReplyKeyboardMarkup(resize_keyboard=True)
kb_stats.add(but_schedule).add(but_exit)


async def kb_client(Krivda):
    if not Krivda:
        return kb_reg
    else:
        return kb_stats


but_cancel = KeyboardButton("Отмена")

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
kb_cancel.add(but_cancel)
