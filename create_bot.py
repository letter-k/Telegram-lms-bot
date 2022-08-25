from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from os import getenv
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=getenv('TOKEN'))

dp = Dispatcher(bot, storage=MemoryStorage())
