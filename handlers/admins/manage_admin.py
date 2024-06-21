from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from peewee import DataError, IntegrityError

from database.connections import get_all_admins, delete_admin, add_admin
from filters.is_admin import IsAdmin
from keyboards.inline.admin import admin_manage_btn
from states.all_states import AdminStates
from utils.bot_context import add_admin_text
from utils.misc.useful_functions import get_admin_context

router = Router()


@router.callback_query(F.data == "admin:all_admins", IsAdmin())
async def handle_admin(call: CallbackQuery):
    data = call.data.split(":")[1]
    if data == "all_admins":
        admins = await get_all_admins()
        await call.message.delete()
        context = f"Админы: \n\n"
        btn = await admin_manage_btn(is_url=True, is_manage=True)
        for n, i in enumerate(admins, start=1):
            context += (f"{n}.<a href='tg://user?id={i['admin_id']}'>{i['admin_fullname']}</a> "
                        f"<i>({i['admin_username']})</i>\n")
        await call.message.answer(context, reply_markup=btn)


@router.callback_query(F.data.startswith("admin_manage:"), IsAdmin())
async def handle_admin_manage(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")[1]
    user_id = call.from_user.id
    if data == "back":
        await state.clear()
        # await call.message.delete()
        context, btn = await get_admin_context()
        await call.message.edit_text(context, reply_markup=btn)
    elif data == "plus":
        # await call.message.delete()
        btn = await admin_manage_btn()
        await call.message.edit_text(add_admin_text, reply_markup=btn)
        await state.set_state(AdminStates.add_admin_text)
    elif data == "minus":
        # await call.message.delete()
        btn = await admin_manage_btn(is_url=False)
        await call.message.edit_text("Выберите для удаления", reply_markup=btn)
    elif data.isdigit():
        if int(data) == user_id:
            await call.answer("Вы не можете удалить самого себя", show_alert=True)
            return
        await delete_admin(data)
        await call.answer("Успешно удален", show_alert=True)
        await call.message.delete()
        context, btn = await get_admin_context()
        await call.message.answer(context, reply_markup=btn)


@router.message(AdminStates.add_admin_text, IsAdmin())
async def add_admin_handler(message: Message, state: FSMContext):
    text = message.text
    data = text.split(" + ")
    if len(data) < 2:
        btn = await admin_manage_btn()
        await message.answer(add_admin_text, reply_markup=btn)
        return
    user_id, full_name = data[0], data[1]
    username = data[2] if len(data) == 3 else ""
    try:
        await add_admin(user_id, full_name, username)
    except DataError:
        await message.answer("Что-то пошло не так ❌")
        btn = await admin_manage_btn()
        await message.answer(add_admin_text, reply_markup=btn)
        return
    except IntegrityError:
        await message.answer("Такой админ уже есть ❌")
        btn = await admin_manage_btn()
        await message.answer(add_admin_text, reply_markup=btn)
        return

    # await message.delete()
    await message.answer("Успешно добавлен ✅")
    await state.clear()
    context, btn = await get_admin_context()
    await message.answer(context, reply_markup=btn)
