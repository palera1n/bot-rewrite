import discord

from typing import List
from discord import app_commands

from utils.config import cfg
from utils.services import guild_service, user_service


async def warn_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    cases: List[Case] = [case for case in user_service.get_cases(int(
        ctx.namespace["member"].id)).cases if case._type == "WARN" and not case.lifted]
    cases.sort(key=lambda x: x._id, reverse=True)

    return [app_commands.Choice(name=f"#{case._id} - {case.punishment} points - {case.reason}", value=str(
        case._id)) for case in cases if (not current or str(case._id).startswith(str(current)))][:25]


async def tags_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    tags = sorted([tag.name.lower() for tag in guild_service.get_guild().tags])
    return [app_commands.Choice(name=tag, value=tag)
            for tag in tags if current.lower() in tag.lower()][:25]
