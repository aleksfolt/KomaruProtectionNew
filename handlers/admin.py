from aiogram import types, F, Router
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto
from aiogram.filters import Command, StateFilter

import config
from database.db import add_user_to_db, remove_user_from_db
from kb import add_or_delete, lite_or_strong, lite_or_strong_del
from states import Form

admin_router = Router()


@admin_router.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.chat.type != "private":
        return
    if msg.from_user.id not in config.ADMINS:
        return

    await msg.reply("Админ панель:", reply_markup=await add_or_delete())


@admin_router.callback_query(F.data.startswith("user_"))
async def handler_premium(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "add":
        await callback.message.answer("Куда будем добавлять?", reply_markup=await lite_or_strong())
        await state.update_data(action="add")
        await state.set_state(Form.add_or_del)
    elif action == "del":
        await callback.message.answer("Откуда будем удалять?", reply_markup=await lite_or_strong_del())
        await state.update_data(action="del")
        await state.set_state(Form.add_or_del)



@admin_router.callback_query(F.data.startswith("bd_"))
async def handle_bd_callback(callback: types.CallbackQuery, state: FSMContext):
    db_type = callback.data.split("_")[1]
    await callback.message.answer("Введите user_id (user_id's) пользователя(ей) для удаления/добавления: ")

    await state.update_data(db_type=db_type)
    await state.set_state(Form.add_or_del)


@admin_router.callback_query(F.data.startswith("del_"))
async def handle_del_callback(callback: types.CallbackQuery, state: FSMContext):
    db_type = callback.data.split("_")[1]

    if db_type == "twice":
        await callback.message.answer("Введите user_id (user_id's) пользователя(ей) для удаления из обеих баз: ")
        await state.update_data(db_type="twice")
    else:
        await callback.message.answer(f"Введите user_id (user_id's) пользователя(ей) для удаления из базы {db_type}: ")
        await state.update_data(db_type=db_type)

    await state.set_state(Form.add_or_del)

@admin_router.message(Form.add_or_del)
async def process_user_to_del(message: types.Message, state: FSMContext):
    user_ids = message.text.split("\n")
    user_ids = [user_id.strip() for user_id in user_ids if user_id.strip()]

    data = await state.get_data()
    action = data.get("action")
    db_type = data.get("db_type")

    response = ""

    if action == "add":
        added_users, already_in_db = add_user_to_db(user_ids, db_type)
        if added_users:
            response += f"Пользователи {added_users} успешно добавлены в базу {db_type}.\n"
        if already_in_db:
            response += f"Пользователи {already_in_db} уже существуют в базе {db_type}."

    elif action == "del":
        if db_type == "twice":
            removed_lite, not_in_lite = remove_user_from_db(user_ids, "lite")
            removed_strong, not_in_strong = remove_user_from_db(user_ids, "strong")

            if removed_lite or removed_strong:
                response += "Пользователи успешно удалены:\n"
                if removed_lite:
                    response += f"Из Lite базы: {removed_lite}\n"
                if removed_strong:
                    response += f"Из Strong базы: {removed_strong}\n"
            if not_in_lite or not_in_strong:
                response += "Пользователи не найдены:\n"
                if not_in_lite:
                    response += f"В Lite базе: {not_in_lite}\n"
                if not_in_strong:
                    response += f"В Strong базе: {not_in_strong}"
        else:
            removed_users, not_in_db = remove_user_from_db(user_ids, db_type)
            if removed_users:
                response += f"Пользователи {removed_users} успешно удалены из базы {db_type}.\n"
            if not_in_db:
                response += f"Пользователи {not_in_db} не найдены в базе {db_type}."

    await message.answer(response)
    await state.clear()

