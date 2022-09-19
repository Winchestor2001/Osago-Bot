from aiogram import executor

import aioschedule
import asyncio
import time

from handlers.admins.admins import register_admins_py
from handlers.users.auto_med_data import register_auto_med_data_py
from handlers.users.dk_data import register_dk_data_py
from handlers.users.karta_gai_data import register_karta_gai_data_py
from handlers.users.karta_gibdd_data import register_karta_gibdd_data_py
from handlers.users.kasko_bank_data import register_kasko_bank_data_py
from handlers.users.osago_data import register_osago_data_py
from handlers.users.search_solary_data import register_search_solary_data_py
from handlers.users.users import register_users_py, check_users_payment
from loader import dp, bot
import middlewares, filters, handlers
from utils.misc.save_data import save_products_to_db, save_users_to_db
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def scheduler():
    aioschedule.every(1).minutes.do(check_users_payment)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    # Уведомляет про запуск
    # await on_startup_notify(dispatcher)
    # u = await bot.get_chat(user_id=1635543672)
    # print(u)
    register_admins_py(dispatcher)
    register_users_py(dispatcher)
    register_osago_data_py(dispatcher)
    register_dk_data_py(dispatcher)
    register_auto_med_data_py(dispatcher)
    register_karta_gai_data_py(dispatcher)
    register_karta_gibdd_data_py(dispatcher)
    register_search_solary_data_py(dispatcher)
    register_kasko_bank_data_py(dispatcher)
    # await save_products_to_db()
    # await save_users_to_db()
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

