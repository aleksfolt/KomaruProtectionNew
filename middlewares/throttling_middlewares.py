from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, ttl: int = 2):
        self.cache = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]):
        user_id = event.from_user.id

        if user_id in self.cache:
            return

        self.cache[user_id] = None

        return await handler(event, data)