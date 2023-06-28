import aiohttp
import asyncio

from typing import Optional
from discord import BanEntry


client_session: Optional[aiohttp.ClientSession] = None

async def make_client_session() -> None:
    global client_session
    client_session = aiohttp.ClientSession()

async def get_client_session() -> aiohttp.ClientSession:
    global client_session
    if client_session is None:
        client_session = aiohttp.ClientSession()
    return client_session


class EventTS(asyncio.Event):
    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self) -> None:
        self._loop.call_soon_threadsafe(super().clear)


class AppealRequest:
    id: int
    completion: EventTS
    result: BanEntry

    def __init__(self, id: int):
        self.id = id
        self.completion = EventTS()

