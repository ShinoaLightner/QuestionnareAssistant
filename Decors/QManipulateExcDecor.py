import asyncio
import datetime
from aiohttp import ClientConnectorError
from disnake import DiscordServerError
from mysql.connector import OperationalError


class LoopException:
    def __init__(self):
        self.timer = [30, 60, 180, 300]

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            for try_, time in enumerate(self.timer):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionResetError, OperationalError, DiscordServerError, ClientConnectorError) as exc:
                    with open('QManipulateError.log', 'a+') as f:
                        f.write(f"[{datetime.datetime.now()}]: Function '{func.__name__}' raised "
                                f"'{exc.__class__.__name__}' on attempt {try_ + 1}\n")
                    await asyncio.sleep(time)
        return wrapper
