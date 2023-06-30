import asyncio
import json
import discord

from aiohttp.web import Request, Response
from datetime import datetime, timedelta

from utils.services import user_service
from .utils import AppealRequest, get_client_session
from cogs.appeals import backend_queue, backend_requests


class Appeal():
    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def appeal(self, req: Request) -> Response:
        if not req.body_exists:
            return Response(status=400, body="No Request Body")

        try:
            data = json.loads(await req.content.read())
        except:
            return Response(status=400, body='Error parsing JSON body')

        session = await get_client_session()
        headers = { 'authorization': f'{data["token_type"]} {data["access_token"]}' }
        try:
            async with session.get("https://discord.com/api/users/@me", headers=headers) as resp:
                if not resp.ok:
                    return Response(status=401, body="Not Authorized")
                userdat = json.loads(await resp.content.read())
        except:
            return Response(status=401, body="Not Authorized")


        user = user_service.get_user(userdat['id'])
        if not user.is_banned:
            # check for non-registered ban
            areq = AppealRequest(userdat['id'])
            # put the request
            await backend_requests.put(areq)
            # wait for response
            await areq.completion.wait()
            areq.completion.clear()
            if areq.result is None:
                    return Response(status=400, body='You are not banned!')

        if user.ban_count > 3:
            return Response(status=400, body='You have reached the ban appeal limit!')

        if user.last_ban_date is not None:
            if datetime.now().date() - user.last_ban_date < timedelta(days=90) and user.ban_count > 1:
                time = datetime.now().date() - user.last_ban_date
                return Response(status=400, body=f'You have to wait another {90 - time.days} day(s) before appealing your ban!')

        if user.is_appealing:
            return Response(status=400, body='Your appeal is currently pending!')

        if user.last_appeal_date is not None:
            if datetime.now().date() - user.last_appeal_date < timedelta(days=90):
                time = datetime.now().date() - user.last_appeal_date
                return Response(status=400, body=f'You have to wait another {90 - time.days} day(s) between appeals!')

        user.last_appeal_date = datetime.now().date()
        user.is_appealing = True
        user.save()

        print("appeal submitted")

        embed = discord.Embed(title="Form Entry", color=discord.Color.green())
        embed.add_field(name="Username", value=userdat['username'], inline=False)
        embed.add_field(name="User ID", value=userdat['id'], inline=False)
        embed.add_field(name="Ban Reason", value=data['ban_reason'], inline=False)
        embed.add_field(name="Unban Reason", value=data['unban_reason'], inline=False)
        embed.add_field(name="Ban Date", value=data['ban_date'] if data['has_ban_date'] else '<unspecified>', inline=False)
        embed.add_field(name="Justification", value=data['justification'], inline=False)
        embed.add_field(name="Joined Appeals Server", value=data['joined_appeals'], inline=False)
        embed.add_field(name="DMs enabled", value=data['dms_enabled'], inline=False)
        embed.add_field(name="Last Ban Date", value=user.last_ban_date if user.last_ban_date is not None else '<not found>', inline=False)
        embed.add_field(name="Last Appeal Date", value=user.last_appeal_date if user.last_appeal_date is not None else '<not found>', inline=False)
        await backend_queue.put(embed)

        return Response()

