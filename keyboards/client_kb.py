from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

but_start = KeyboardButton('start')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(but_start)
