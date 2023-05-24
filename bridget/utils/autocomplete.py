import discord

from typing import List
from discord import app_commands
from discord.enums import AutoModRuleTriggerType

from utils.config import cfg
from utils.enums import FilterBypassLevel
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

async def memes_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    memes = sorted([meme.name.lower() for meme in guild_service.get_guild().memes])
    return [app_commands.Choice(name=meme, value=meme)
            for meme in memes if current.lower() in meme.lower()][:25]

async def issues_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    issues = sorted([issue.name for issue in guild_service.get_guild().issues])
    return [app_commands.Choice(name=issue, value=issue)
            for issue in issues if current.lower() in issue.lower()][:25]

# TODO: Check if this is even used at all anymore
async def filter_bypass_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[int]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    levels = [ FilterBypassLevel.HELPER, FilterBypassLevel.MOD, FilterBypassLevel.RAID ]
    return [
        app_commands.Choice(name=str(level), value=int(level))
        for level in levels if current.lower() in str(level).lower()
    ]

async def automod_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    return [
        app_commands.Choice(name=str(rule.name), value=str(rule.id))
        for rule in rules if rule.trigger.type == AutoModRuleTriggerType.keyword and current.lower() in str(rule.name).lower()
    ]

async def filter_phrase_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    rule = [ x for x in rules if str(x.id) == ctx.namespace['rule'] ]
    if len(rule) == 0:
        return []
    rule = rule[0]

    filters = [ x for x in rule.trigger.keyword_filter ]

    return [app_commands.Choice(name=filter, value=filter)
            for filter in filters if current.lower() in filter[0].lower()][:25]

async def filter_regex_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    rule = [ x for x in rules if str(x.id) == ctx.namespace['rule'] ]
    if len(rule) == 0:
        return []
    rule = rule[0]

    filters = [ x for x in rule.trigger.regex_patterns ]

    return [app_commands.Choice(name=filter, value=filter)
            for filter in filters if current.lower() in filter[0].lower()][:25]

async def filter_whitelist_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    # TODO: Real permission check for mod+
    if ctx.user.id != cfg.owner_id:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    rule = [ x for x in rules if str(x.id) == ctx.namespace['rule'] ]
    if len(rule) == 0:
        return []
    rule = rule[0]

    filters = [ x for x in rule.trigger.allow_list ]

    return [app_commands.Choice(name=filter, value=filter)
            for filter in filters if current.lower() in filter[0].lower()][:25]

async def rule_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    channel = ctx.guild.get_channel(guild_service.get_guild().channel_rules)
    messages = [ x async for x in channel.history(limit=50, oldest_first=True) ]

    rules = [ x for x in messages if x.embeds ]
    return [app_commands.Choice(name=rule.embeds[0].title, value=str(rule.id))
            for rule in rules if current.lower() in rule.embeds[0].title.lower()][:25]

