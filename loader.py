from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from database.models import *

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db.create_tables([Users, Payments, Admins, QiwiConfig, UserHistory, OsagoData, DkData, ProductsPhotoQuestionnaire, KartaGibddData, KaskoBankData, AutoMedData, SearchSolaryData, Products])
