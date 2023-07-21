from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from os import getenv
from scripts import Database
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=getenv("TOKEN"))
if getenv("TYPE_DATABASE") == "local":
    db = Database(getenv("CONNECTIONSTRING"))
elif getenv("TYPE_DATABASE") == "remote":
    db = Database(
        getenv("CONNECTIONSTRING"),
        {
            "ssl": {
                "cert": getenv("CERT"),
                "key": getenv("KEY"),
                "check_hostname": False,
            }
        },
    )

dp = Dispatcher(bot, storage=MemoryStorage())
