import discord

from typing import List
from discord import app_commands

from utils.config import cfg
from utils.enums import FilterBypassLevel, PermissionLevel
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

async def filter_phrase_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    rule = FilterBypassLevel(ctx.namespace['bypass']).find_rule_for_bypass(rules)

    if rule is None:
        return []

    filters = [ x for x in rule.trigger.keyword_filter ]

    return [app_commands.Choice(name=filter, value=filter)
            for filter in filters if current.lower() in filter[0].lower()][:25]

async def filter_regex_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    rule = FilterBypassLevel(ctx.namespace['bypass']).find_rule_for_bypass(rules)

    if rule is None:
        return []

    filters = [ x for x in rule.trigger.regex_patterns ]

    return [app_commands.Choice(name=filter, value=filter)
            for filter in filters if current.lower() in filter[0].lower()][:25]

async def filter_whitelist_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    rule = FilterBypassLevel(ctx.namespace['bypass']).find_rule_for_bypass(rules)

    if rule is None:
        return []

    filters = [ x for x in rule.trigger.allow_list ]

    return [app_commands.Choice(name=filter, value=filter)
            for filter in filters if current.lower() in filter[0].lower()][:25]

