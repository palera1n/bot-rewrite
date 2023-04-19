import discord

from discord import AutoModRule, app_commands
from discord.ext import commands
from typing import List, Optional

from utils import Cog, send_error, send_success
from utils.autocomplete import filter_bypass_autocomplete, filter_phrase_autocomplete, filter_regex_autocomplete, filter_whitelist_autocomplete
from utils.enums import FilterBypassLevel, PermissionLevel


class FiltersGroup(Cog, commands.GroupCog, group_name="filter"):
    @PermissionLevel.HELPER
    @app_commands.autocomplete(bypass=filter_bypass_autocomplete)
    @app_commands.command()
    async def add(self, ctx: discord.Interaction, bypass: int, phrase: str = None, regex: str = None, whitelist: str = None) -> None:
        """Add a new filtered word

        Args:
            ctx (discord.ctx): Context
            bypass (int): The level required to bypass the filter
            phrase (str): The word or phrase to filter
            regex (str): The regular expression to filter
            whitelist (str): The word or phrase to whitelist
        """

        # fetch rule
        rules = await ctx.guild.fetch_automod_rules()
        rule = FilterBypassLevel(bypass).find_rule_for_bypass(rules)

        if rule is None:
            await send_error(ctx, "AutoMod rule not found!", delete_after=3)
            return

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

    @PermissionLevel.HELPER
    @app_commands.command()
    async def list(self, ctx: discord.Interaction) -> None:
        """List filtered words

        Args:
            ctx (discord.ctx): Context
        """

        # fetch rules and prepare embed
        rules = await ctx.guild.fetch_automod_rules()
        embed = discord.Embed(title="Filtered Word List")

        for rule in rules:
            # add the filtered words, regexs and whitelists to the embed
            ruledict = rule.to_dict()
            words = '\n'.join(ruledict['trigger_metadata']['keyword_filter']) + '\n'
            words += '\n'.join(f'`/{x}/`' for x in ruledict['trigger_metadata']['regex_patterns']) + '\n'
            words += '\n'.join(f'**{x}** (whitelisted)' for x in ruledict['trigger_metadata']['allow_list'])
            embed.add_field(name=rule.name, value=words)

        # send the embed
        await send_success(ctx, embed=embed)

    @PermissionLevel.HELPER
    @app_commands.autocomplete(bypass=filter_bypass_autocomplete, phrase=filter_phrase_autocomplete, regex=filter_regex_autocomplete, whitelist=filter_whitelist_autocomplete)
    @app_commands.command()
    async def remove(self, ctx: discord.Interaction, bypass: int, phrase: str = None, regex: str = None, whitelist: str = None) -> None:
        """Remove a filtred word

        Args:
            ctx (discord.ctx): Context
            bypass (int): The level required to bypass the filter
            phrase (str): The word or phrase to un-filter
            regex (str): The regular expression to un-filter
            whitelist (str): The word or phrase to un-whitelist
        """

        # fetch rule
        rules = await ctx.guild.fetch_automod_rules()
        rule = FilterBypassLevel(bypass).find_rule_for_bypass(rules)

        if rule is None:
            await send_error(ctx, "AutoMod rule not found!", delete_after=3)
            return

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

