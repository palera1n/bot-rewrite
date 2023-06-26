import asyncio
import aiohttp_cors
import discord
import threading

from aiohttp import web

from .appeal import Appeal
from .utils import make_client_session
from utils.config import cfg


def thread_run(runner) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', cfg.backend_port)
    loop.create_task(make_client_session())
    loop.run_until_complete(site.start())
    loop.run_forever()


def aiohttp_server(bot: discord.Client) -> web.AppRunner:
    app = web.Application()
    appeal = Appeal(bot)
    app.add_routes([
        web.post('/bridget/appeal', appeal.appeal)
    ])

    cors = aiohttp_cors.setup(app, defaults={
       "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*"
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    return web.AppRunner(app)

def run(bot: discord.Client) -> None:
    t = threading.Thread(target=thread_run, args=(aiohttp_server(bot),), daemon=True)
    t.start()
