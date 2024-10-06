import json
import aiofiles
import asyncio
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import ChatMemberUpdated
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound
from database.db import Session
from models import ChatConfig, RaidConfig
from text import raider_msg, raiders_msg
from states import raider_count, raid_alert_active, raid_start_time


ban_router = Router()

async def load_raiders():
    async with aiofiles.open('raiders.json', 'r') as file:
        raiders = json.loads(await file.read())

    async with aiofiles.open('kchat_raiders.json', 'r') as file:
        kchat_raiders = json.loads(await file.read())

    return raiders, kchat_raiders

@ban_router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def check_user(event: ChatMemberUpdated):
    global raid_alert_active, raid_start_time, raider_count
    new_member = event.new_chat_member.user
    chat_id = str(event.chat.id)

    if '@tgkillface' in new_member.first_name:
        await asyncio.sleep(2)
        await event.bot.ban_chat_member(chat_id=chat_id, user_id=new_member.id, until_date=None)
        raider_count += 1

        if raider_count > 2 and not raid_alert_active:
            raid_alert_active = True
            raid_start_time = datetime.now()
            await event.bot.send_message(
                chat_id=chat_id,
                text=raiders_msg,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

        if raid_alert_active:
            if datetime.now() > raid_start_time + timedelta(minutes=1):
                raid_alert_active = False
                raider_count = 0
            else:
                return

        if not raid_alert_active:
            if new_member.username:
                link = f"https://t.me/{new_member.username}"
            else:
                link = f"tg://user?id={new_member.id}"

            await event.bot.send_message(
                chat_id=chat_id,
                text=raider_msg.format(link=link),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        return

    session = Session()

    try:
        raid_config = session.query(RaidConfig).filter_by(chat_id=chat_id).one()
        raid_enabled = raid_config.raid_enabled
    except NoResultFound:
        raid_enabled = True

    if not raid_enabled:
        session.close()
        return

    try:
        chat_config = session.query(ChatConfig).filter_by(chat_id=chat_id).one()
        db_choice = chat_config.db_choice
    except NoResultFound:
        db_choice = 'lite'
    finally:
        session.close()

    raiders, kchat_raiders = await load_raiders()
    print(raiders, kchat_raiders)

    if db_choice == 'lite':
        raider_list = raiders
    elif db_choice == 'strong':
        raider_list = kchat_raiders

    if any(raider['user_id'] == str(new_member.id) for raider in raider_list.values()):
        member_status = await event.bot.get_chat_member(chat_id, new_member.id)
        if member_status.status == "member":
            await asyncio.sleep(2)
            await event.bot.ban_chat_member(chat_id=chat_id, user_id=new_member.id, until_date=None)
            raider_count += 1

            if raider_count > 2 and not raid_alert_active:
                raid_alert_active = True
                raid_start_time = datetime.now()
                await event.bot.send_message(
                    chat_id=chat_id,
                    text=raiders_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )

            if raid_alert_active:
                if datetime.now() > raid_start_time + timedelta(minutes=1):
                    raid_alert_active = False
                    raider_count = 0
                else:
                    return

            if not raid_alert_active:
                if new_member.username:
                    link = f"https://t.me/{new_member.username}"
                else:
                    link = f"tg://user?id={new_member.id}"

                await event.bot.send_message(
                    chat_id=chat_id,
                    text=raider_msg.format(link=link),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )