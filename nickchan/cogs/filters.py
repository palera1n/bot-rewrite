import discord

from discord import Embed, app_commands
from discord.ext import commands
from typing import Optional

from utils import Cog, send_error, send_success
from utils.menus import Menu
from utils.autocomplete import automod_autocomplete, filter_phrase_autocomplete, filter_regex_autocomplete, filter_whitelist_autocomplete
from utils.enums import PermissionLevel


def format_filter_page(_, entries, current_page, all_pages) -> Embed:
    embed = discord.Embed(
        title='Filtered words', color=discord.Color.blurple())
    for filter in entries:
        embed.add_field(name=filter[0], value=filter[1])
    embed.set_footer(
        text=f"Page {current_page} of {len(all_pages)}")
    return embed


class FiltersGroup(Cog, commands.GroupCog, group_name="filter"):
    @PermissionLevel.MOD
    @app_commands.autocomplete(rule=automod_autocomplete)
    @app_commands.command()
    async def add(self, ctx: discord.Interaction, rule: str, phrase: str = None, regex: str = None, whitelist: str = None) -> None:
        """Add a new filtered word

        Args:
            ctx (discord.ctx): Context
            rule (str): The AutoMod rule to add the filter to
            phrase (str): The word or phrase to filter
            regex (str): The regular expression to filter
            whitelist (str): The word or phrase to whitelist
        """

        # fetch rule
        rules = await ctx.guild.fetch_automod_rules()
        rule = [ x for x in rules if str(x.id) == rule ]
        if len(rule) == 0:
            await send_error(ctx, "AutoMod rule not found!", delete_after=3)
            return
        rule = rule[0]

        # extract the trigger to modify it
        trig = rule.trigger

        if phrase is not None:
            trig.keyword_filter.append(phrase)

        if regex is not None:
            trig.regex_patterns.append(regex)

        if whitelist is not None:
            trig.allow_list.append(whitelist)

        # edit the rule trigger
        await rule.edit(trigger=trig, reason="Filtered word/regex/whitelist has been added")
        await send_success(ctx, "Filter has been edited.", delete_after=3)

    @PermissionLevel.MOD
    @app_commands.autocomplete(rule=automod_autocomplete)
    @app_commands.command()
    async def list(self, ctx: discord.Interaction, rule: Optional[str] = None) -> None:
        """List filtered words

        Args:
            ctx (discord.ctx): Context
            rule (str): Show only one AutoMod rule
        """

        # fetch rules and prepare embed
        rules = await ctx.guild.fetch_automod_rules()

        filters = []
        for am_rule in rules:
            if rule is not None and str(am_rule.id) != rule:
                continue

            # add the filtered words, regexs and whitelists to the embed
            ruledict = am_rule.to_dict()
            if ruledict is None or 'trigger_metadata' not in ruledict or ruledict['trigger_metadata'] is None:
                continue

            # keywords
            if 'keyword_filter' in ruledict['trigger_metadata']:
                for word in ruledict['trigger_metadata']['keyword_filter']:
                    filters.append((discord.utils.escape_markdown(word), am_rule.name))
            # regexs
            if 'regex_patterns' in ruledict['trigger_metadata']:
                for x in ruledict['trigger_metadata']['regex_patterns']:
                    xr = x.replace("`", "\\`")
                    filters.append((f'`/{xr}/`', am_rule.name))
            # whitelists
            if 'allow_list' in ruledict['trigger_metadata']:
                for x in ruledict['trigger_metadata']['allow_list']:
                    filters.append((f'**{discord.utils.escape_markdown(x)}** (whitelisted)', am_rule.name))

        _filters = sorted(filters)
        if len(_filters) == 0:
            raise commands.BadArgument("There are no filters defined.")

        menu = Menu(
            ctx,
            filters,
            per_page=12,
            page_formatter=format_filter_page,
            whisper=True)
        await menu.start()

    @PermissionLevel.MOD
    @app_commands.autocomplete(rule=automod_autocomplete, phrase=filter_phrase_autocomplete, regex=filter_regex_autocomplete, whitelist=filter_whitelist_autocomplete)
    @app_commands.command()
    async def remove(self, ctx: discord.Interaction, rule: str, phrase: str = None, regex: str = None, whitelist: str = None) -> None:
        """Remove a filtred word

        Args:
            ctx (discord.ctx): Context
            rule (str): The AutoMod rule to remove the filter from
            phrase (str): The word or phrase to un-filter
            regex (str): The regular expression to un-filter
            whitelist (str): The word or phrase to un-whitelist
        """

        # fetch rule
        rules = await ctx.guild.fetch_automod_rules()
        rule = [ x for x in rules if str(x.id) == rule ]
        if len(rule) == 0:
            await send_error(ctx, "AutoMod rule not found!", delete_after=3)
            return
        rule = rule[0]

        # extract the trigger to modify it
        trig = rule.trigger

        try:
            if phrase is not None:
                trig.keyword_filter.remove(phrase)

            if regex is not None:
                trig.regex_patterns.remove(regex)

            if whitelist is not None:
                trig.allow_list.remove(whitelist)
        except ValueError:
            await send_error(ctx, "The requested filter(s) could not be found in the AutoMod rule", delete_after=3)
            return

        # edit the rule trigger
        await rule.edit(trigger=trig, reason="Filtered word/regex/whitelist has been removed")
        await send_success(ctx, "Filter has been edited.", delete_after=3)

