import logging
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f"Hello {message.from_user.full_name}")
