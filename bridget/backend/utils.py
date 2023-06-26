import aiohttp

from typing import Optional


client_session: Optional[aiohttp.ClientSession] = None

async def make_client_session() -> None:
    global client_session
    client_session = aiohttp.ClientSession()

async def get_client_session() -> aiohttp.ClientSession:
    global client_session
    if client_session is None:
        client_session = aiohttp.ClientSession()
    return client_session
