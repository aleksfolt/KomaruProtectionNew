from aiogram import types, F, Router
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.types import Message, InputMediaPhoto, ChatMemberAdministrator, ChatMemberOwner
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.exc import NoResultFound

import text
from config import start_image
from database.db import Session, ChatConfig, RaidConfig
from kb import start_kb, lite_or_strong_with_raid
from text import dont_set, help_msg

router = Router()

async def has_promote_rights(message: types.Message) -> bool:
    admins = await message.bot.get_chat_administrators(chat_id=message.chat.id)

    for admin in admins:
        if admin.user.id == message.from_user.id:
            if isinstance(admin, types.ChatMemberAdministrator) and admin.can_promote_members:
                return True
            if isinstance(admin, types.ChatMemberOwner):
                return True

    return False

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer_photo(
        photo=start_image,
        caption=text.start_msg,
        reply_markup=await start_kb(msg),
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(Command("menu"))
async def menu_handler(msg: types.Message):
    if msg.chat.type == "private":
        await msg.answer("❌ Данная коамнда работает только в группах!", reply_markup=await start_kb(msg))
        return
    if await has_promote_rights(msg):
        session = Session()
        chat_id = str(msg.chat.id)

        try:
            chat_config = session.query(ChatConfig).filter_by(chat_id=chat_id).one()
            current_choice = chat_config.db_choice
        except NoResultFound:
            current_choice = "не установлено"

        try:
            raid_config = session.query(RaidConfig).filter_by(chat_id=chat_id).one()
            raid_status = "Включен" if raid_config.raid_enabled else "Выключен"
        except NoResultFound:
            raid_status = "Выключен"
        finally:
            session.close()

        await msg.reply(
            f"⚙️ Текущий выбор базы данных: {current_choice}.\n"
            f"👁 Антирейд: {raid_status}.",
            reply_markup=await lite_or_strong_with_raid(msg.from_user.id, raid_status)
        )
    else:
        await msg.reply(text=text.dont_have_rights)

@router.callback_query(F.data.startswith("raid_"))
async def handle_raid_toggle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chat_id = str(callback.message.chat.id)

    if callback.data.endswith(str(user_id)):
        session = Session()
        action = callback.data.split("_")[1]

        try:
            raid_config = session.query(RaidConfig).filter_by(chat_id=chat_id).one()
            raid_config.raid_enabled = (action == "on")
        except NoResultFound:
            raid_config = RaidConfig(chat_id=chat_id, raid_enabled=(action == "on"))
            session.add(raid_config)

        session.commit()
        session.close()

        if action == "on":
            await callback.answer("Антирейд включен!", show_alert=True)
        else:
            await callback.answer("Антирейд отключен!", show_alert=True)

        await callback.message.delete()
    else:
        await callback.answer("Эта кнопка не для вас!", show_alert=True)


@router.callback_query(F.data.startswith("chose_") | F.data.startswith("toggle_raid_"))
async def handle_db_and_raid_choice(callback: types.CallbackQuery):
    session = Session()
    chat_id = str(callback.message.chat.id)
    user_id = callback.data.split("_")[-1]

    if int(user_id) != callback.from_user.id:
        await callback.answer("Эта кнопка не для вас!", show_alert=True)
        return

    try:
        if callback.data.startswith("chose_"):
            choice = callback.data.split("_")[1]

            if choice == "strong":
                await callback.message.delete()
                confirm_kb = InlineKeyboardBuilder()
                confirm_kb.row(types.InlineKeyboardButton(text="Подтвердить выбор Strong",
                                                          callback_data=f"confirm_strong_{user_id}"))
                confirm_kb.row(types.InlineKeyboardButton(text="Отмена", callback_data=f"cancel_choice_{user_id}"))
                await callback.message.answer(text=text.alert_msg, reply_markup=confirm_kb.as_markup(),
                                              parse_mode=ParseMode.MARKDOWN)
            else:
                try:
                    chat_config = session.query(ChatConfig).filter_by(chat_id=chat_id).one()
                    chat_config.db_choice = choice
                except NoResultFound:
                    chat_config = ChatConfig(chat_id=chat_id, db_choice=choice)
                    session.add(chat_config)
                session.commit()
                await callback.message.edit_text(
                    f"⚙️ База данных {choice} установлена! Добро пожаловать в безопасный чат."
                )

        elif callback.data.startswith("toggle_raid_"):
            try:
                raid_config = session.query(RaidConfig).filter_by(chat_id=chat_id).one()
                raid_config.raid_enabled = not raid_config.raid_enabled
                raid_status = "Включен" if raid_config.raid_enabled else "Выключен"
            except NoResultFound:
                raid_config = RaidConfig(chat_id=chat_id, raid_enabled=True)
                session.add(raid_config)
                raid_status = "Включен"

            session.commit()
            await callback.message.edit_text(f"👁 Антирейд: {raid_status}.")
    finally:
        session.close()
        await callback.answer("Выбор обновлен.", show_alert=True)


@router.callback_query(F.data.startswith("confirm_strong_"))
async def handle_confirm_strong(callback: types.CallbackQuery):
    session = Session()
    chat_id = str(callback.message.chat.id)
    user_id = callback.data.split("_")[-1]

    if int(user_id) != callback.from_user.id:
        await callback.answer("Эта кнопка не для вас!", show_alert=True)
        return

    try:
        chat_config = session.query(ChatConfig).filter_by(chat_id=chat_id).one()
        chat_config.db_choice = "strong"
    except NoResultFound:
        chat_config = ChatConfig(chat_id=chat_id, db_choice="strong")
        session.add(chat_config)

    session.commit()
    session.close()

    await callback.message.edit_text("⚙️ База данных Strong установлена! Будьте осторожны 😊.")
    await callback.answer("База данных Strong подтверждена.", show_alert=True)


@router.callback_query(F.data.startswith("cancel_choice_"))
async def handle_cancel_choice(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[-1]

    if int(user_id) != callback.from_user.id:
        await callback.answer("Эта кнопка не для вас!", show_alert=True)
        return
    await callback.message.delete()
    await callback.answer("Выбор отменен.", show_alert=True)

@router.message(Command("help"))
async def help_handler(msg: Message):
    await msg.reply(
        text=help_msg,
        parse_mode=ParseMode.MARKDOWN
    )
