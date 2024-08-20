from aiogram import Router, F
from aiogram.types import Message
from utils.bot_context import *


router = Router()


@router.message(F.text == "💥Телеграм канал")
async def telegram_channel_handler(message: Message):
    await message.answer(channel_text)


@router.message(F.text == "☎️ Обратная связь")
async def bot_handler(message: Message):
    await message.answer(support_text)
