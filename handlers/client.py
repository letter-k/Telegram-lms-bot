from aiogram.dispatcher.filters import Text
from aiogram import Dispatcher, types
from keyboards import kb_client


async def cmd_start(message: types.Message):
    await message.answer(f"Hello", reply_markup=kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_start, Text(equals='start'))
