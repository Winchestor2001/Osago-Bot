from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.connections import get_all_admins, count_users, get_bot_configs
from filters.is_admin import IsAdmin
from keyboards.inline.admin import admin_menu_btn, admin_manage_btn
from utils.misc.useful_functions import get_admin_context

router = Router()


@router.message(Command(commands=["admin"]), IsAdmin())
async def intro_admin(message: Message):
    user_id = message.from_user.id
    admins_data = await get_all_admins()
    admins = [item['admin_id'] for item in admins_data if item.get("admin_id")]
    if user_id in admins:
        context, btn = await get_admin_context()
        await message.answer(context, reply_markup=btn)


@router.callback_query(F.data.startswith("admin:"), IsAdmin())
async def handle_admin(call: CallbackQuery):
    data = call.data.split(":")[1]
    if data == "all_admins":
        admins = await get_all_admins()
        await call.message.delete()
        context = f"Админы: \n\n"
        btn = await admin_manage_btn()
        for n, i in enumerate(admins, start=1):
            context += (f"{n}.<a href='tg://user?id={i['admin_id']}'>{i['admin_fullname']}</a> "
                        f"<i>({i['admin_username']})</i>\n")
        await call.message.answer(context, reply_markup=btn)


@router.callback_query(F.data.startswith("admin_manage:"), IsAdmin())
async def handle_admin_manage(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    if data == "back":
        # await call.message.delete()
        context, btn = await get_admin_context()
        await call.message.edit_text(context, reply_markup=btn)
    elif data == "plus":
        pass
    elif data == "minus":
        pass
