import discord
from itertools import groupby

from typing import List
from discord import app_commands
from discord.enums import AutoModRuleTriggerType
from bridget.model.infraction import Infraction

from utils.enums import PermissionLevel
from utils.fetchers import canister_fetch_repos, get_ios_cfw
from utils.services import guild_service, user_service


def transform_groups(groups):
    final_groups = []
    # groups = [g for _, g in groups.items()]
    for group in groups:
        if group.get("subgroup") is not None:
            for subgroup in group.get("subgroup"):
                subgroup["order"] = group.get("order")
                final_groups.append(subgroup)
        else:
            final_groups.append(group)

    return final_groups

def sort_versions(version):
    version = f'{version.get("osStr")} {version.get("version")}'
    v = version.split(' ')
    v[0] = list(map(int, v[1].split('.')))
    return v

async def warn_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    if not PermissionLevel.MOD == ctx.user:
        return []

    infractions: List[Infraction] = [infraction for infraction in user_service.get_infractions(int(
        ctx.namespace["member"].id)).infractions if infraction._type == "WARN" and not infraction.lifted]
    infractions.sort(key=lambda x: x._id, reverse=True)

    return [app_commands.Choice(name=f"#{infraction._id} - {infraction.punishment} points - {infraction.reason}", value=str(
        infraction._id)) for infraction in infractions if (not current or str(infraction._id).startswith(str(current)))][:25]

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

async def automod_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    if not PermissionLevel.MOD == ctx.user:
        return []

    rules = await ctx.guild.fetch_automod_rules()
    return [
        app_commands.Choice(name=str(rule.name), value=str(rule.id))
        for rule in rules if rule.trigger.type == AutoModRuleTriggerType.keyword and current.lower() in str(rule.name).lower()
    ]

async def filter_phrase_autocomplete(ctx: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    if not PermissionLevel.MOD == ctx.user:
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
    if not PermissionLevel.MOD == ctx.user:
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
    if not PermissionLevel.MOD == ctx.user:
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

async def repo_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    repos = await canister_fetch_repos()
    if repos is None:
        return []
    repos = [repo['slug'] for repo in repos if repo.get(
        "slug") and repo.get("slug") is not None]
    repos.sort()
    return [app_commands.Choice(name=repo, value=repo) for repo in repos if current.lower() in repo.lower()][:25]

async def ios_version_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    versions = await get_ios_cfw()
    if versions is None:
        return []

    versions = versions.get("ios")
    # versions = [v for _, v in versions.items()]
    versions.sort(key=lambda x: str(x.get("released")
                  or "1970-01-01"), reverse=True)
    return [app_commands.Choice(name=f"{v['osStr']} {v['version']} ({v.get('build')})", value=v["uniqueBuild"]) for v in versions if (current.lower() in v['version'].lower() or current.lower() in v.get('build').lower()) and not v['beta']][:25]


async def ios_beta_version_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    versions = await get_ios_cfw()
    if versions is None:
        return []

    versions = versions.get("ios")
    # versions = [v for _, v in versions.items()]
    versions.sort(key=lambda x: x.get("released")
                  or "1970-01-01", reverse=True)
    return [app_commands.Choice(name=f"{v['osStr']} {v['version']} ({v.get('build')})", value=v["uniqueBuild"]) for v in versions if (current.lower() in v['version'].lower() or current.lower() in v.get('build').lower()) and v['beta']][:25]


async def ios_on_device_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    cfw = await get_ios_cfw()
    if cfw is None:
        return []

    ios = cfw.get("ios")
    # ios = [i for _, i in ios.items()]
    devices = cfw.get("group")
    transformed_devices = transform_groups(devices)
    selected_device = interaction.namespace["device"]

    if selected_device is None:
        return []
    matching_devices = [
        d for d in transformed_devices if selected_device.lower() == d.get('name').lower() or any(selected_device.lower() == x.lower() for x in d.get("devices"))]

    if not matching_devices:
        return []

    matching_device = matching_devices[0].get("devices")[0]
    matching_ios = [version for version in ios if matching_device in version.get(
        'devices') and current.lower() in version.get('version').lower()]

    matching_ios.sort(key=sort_versions, reverse=True)

    return [app_commands.Choice(name=f'{version.get("osStr")} {version.get("version")}', value=version.get("uniqueBuild") or version.get("build")) for version in matching_ios][:25]


async def device_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    res = await get_ios_cfw()
    if res is None:
        return []

    all_devices = res.get("group")
    transformed_devices = transform_groups(all_devices)
    devices = [d for d in transformed_devices if (any(current.lower() in x.lower(
    ) for x in d.get('devices')) or current.lower() in d.get('name').lower())]

    devices.sort(key=lambda x: x.get('type') or "zzz")
    devices_groups = groupby(devices, lambda x: x.get('type'))

    devices = []
    for _, group in devices_groups:
        group = list(group)
        group.sort(key=lambda x: x.get('order'), reverse=True)
        devices.extend(group)

    all_devices = res.get("device")
    for device in devices:
        ident = device.get("devices")[0]
        # detailed = all_devices.get(ident)
        detailed = [ td for td in all_devices if td.get('identifer') == ident ]
        if detailed:
            detailed = detailed[0]
            released = detailed.get('released') or '-1'
            if isinstance(released, list):
                released = released[0]
            device['released'] = str(released)
        else:
            device['released'] = "-1"

    devices.sort(key=lambda x: x.get('released'), reverse=True)
    return [app_commands.Choice(name=device.get('name'), value=device.get("devices")[0] if device.get("devices") else device.get("name")) for device in devices][:25]


async def jailbreakable_device_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    res = await get_ios_cfw()
    if res is None:
        return []

    all_devices = res.get("group")
    transformed_devices = transform_groups(all_devices)
    devices = [d for d in transformed_devices if (any(current.lower() in x.lower(
    ) for x in d.get('devices')) or current.lower() in d.get('name').lower())]

    devices = [d for d in devices if any(x in d.get("type") for x in ['iPhone','iPod','iPad','Apple TV','Apple Watch','HomePod'])]

    devices.sort(key=lambda x: x.get('type') or "zzz")
    devices_groups = groupby(devices, lambda x: x.get('type'))

    devices = []
    for _, group in devices_groups:
        group = list(group)
        group.sort(key=lambda x: x.get('order'), reverse=True)
        devices.extend(group)

    all_devices = res.get("device")
    for device in devices:
        ident = device.get("devices")[0]
        # detailed = all_devices.get(ident)
        detailed = [ td for td in all_devices if td.get('identifer') == ident ]
        if detailed:
            detailed = detailed[0]
            released = detailed.get('released') or '-1'
            if isinstance(released, list):
                released = released[0]
            device['released'] = str(released)

        else:
            device['released'] = "-1"

    devices.sort(key=lambda x: x.get('released'), reverse=True)
    return [app_commands.Choice(name=device.get('name'), value=device.get("devices")[0] if device.get("devices") else device.get("name")) for device in devices][:25]


async def jb_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    apps = await get_ios_cfw()
    if apps is None:
        return []

    apps = apps.get("jailbreak")
    # apps = [jb for _, jb in apps.items()]
    apps.sort(key=lambda x: x["name"].lower())
    return [app_commands.Choice(name=app["name"], value=app["name"]) for app in apps if app["name"].lower().startswith(current.lower())][:25]


async def bypass_autocomplete(_: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    data = await get_ios_cfw()
    apps = data.get("bypass")
    # apps = [app for _, app in bypasses.items()]
    apps.sort(key=lambda x: x.get("name").lower())
    return [app_commands.Choice(name=app.get("name"), value=app.get("bundleId")) for app in apps if current.lower() in app.get("name").lower()][:25]

