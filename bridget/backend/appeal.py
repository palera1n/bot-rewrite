import json
import discord

from aiohttp.web import Request, Response

from .utils import get_client_session
from utils.config import cfg
from cogs.appeals import backend_queue


class Appeal():
    def __init__(self, bot: discord.Client):
        self.bot = bot


    async def appeal(self, req: Request) -> Response:
        if not req.body_exists:
            return Response(status=400, body="No Request Body")

        try:
            data = json.loads(await req.content.read())
        except Exception as e:
            return Response(status=400, body=str(e))

        session = await get_client_session()
        headers = { 'authorization': f'{data["token_type"]} {data["access_token"]}' }
        try:
            async with session.get("https://discord.com/api/users/@me", headers=headers) as resp:
                if not resp.ok:
                    return Response(status=401, body="Not Authorized")
                userdat = json.loads(await resp.content.read())
        except:
            return Response(status=401, body="Not Authorized")


        embed = discord.Embed(title="Form Entry", color=discord.Color.green())
        embed.add_field(name="Username", value=userdat['username'], inline=False)
        embed.add_field(name="User ID", value=userdat['id'], inline=False)
        embed.add_field(name="Ban Reason", value=data['ban_reason'], inline=False)
        embed.add_field(name="Unban Reason", value=data['unban_reason'], inline=False)
        embed.add_field(name="Ban Date", value=data['ban_date'], inline=False)
        embed.add_field(name="Meow", value=data['meow'], inline=False)
        embed.add_field(name="Joined Appeals Server", value=data['joined_appeals'], inline=False)
        embed.add_field(name="DMs enabled", value=data['dms_enabled'], inline=False)
        await backend_queue.put(embed)

        return Response()
