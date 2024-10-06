import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers.admin import admin_router
from handlers.autoban import ban_router
from handlers.handlers import router
from middlewares.throttling_middlewares import ThrottlingMiddleware


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(admin_router, router, ban_router)
    dp.message.middleware(ThrottlingMiddleware())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())