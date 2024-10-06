from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from aiogram.types import Message


async def start_kb(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="➡️ Добавить в группу",
                                           url="https://t.me/KomaruProtectBot?startgroup=protect&admin=change_info+restrict_members+delete_messages+pin_messages+invite_users"))
    return builder.as_markup()

async def add_or_delete():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="➕ Добавить пользователя", callback_data="user_add"))
    builder.row(types.InlineKeyboardButton(text="➖ Удалить пользователя", callback_data="user_del"))
    return builder.as_markup()


async def lite_or_strong():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👁‍🗨 Lite база данных", callback_data=f"bd_lite"))
    builder.row(types.InlineKeyboardButton(text="🦾 Strong база данных", callback_data=f"bd_strong"))
    builder.row(types.InlineKeyboardButton(text="Обе", callback_data=f"bd_twice"))
    return builder.as_markup()

async def lite_or_strong_del():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👁‍🗨 Lite база данных", callback_data=f"del_lite"))
    builder.row(types.InlineKeyboardButton(text="🦾 Strong база данных", callback_data=f"del_strong"))
    builder.row(types.InlineKeyboardButton(text="Обе", callback_data=f"del_twice"))
    return builder.as_markup()


async def lite_or_strong_with_raid(user_id, raid_status):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👁‍🗨 Lite", callback_data=f"chose_lite_{user_id}"))
    builder.row(types.InlineKeyboardButton(text="🦾 Strong", callback_data=f"chose_strong_{user_id}"))
    toggle_raid_text = "❌ Выключить антирейд" if raid_status == "Включен" else "✅ Включить антирейд"
    builder.row(types.InlineKeyboardButton(text=toggle_raid_text, callback_data=f"toggle_raid_{user_id}"))
    return builder.as_markup()