import base64
import discord
import io
import random

from discord import app_commands, Embed
from discord.ext import commands

from utils import Cog, send_error, send_success
from utils.autocomplete import rule_autocomplete
from utils.enums import PermissionLevel
from utils.menus import PFPButton, PFPView
from utils.services import guild_service, user_service


class Misc(Cog):
    spam_cooldown = commands.CooldownMapping.from_cooldown(3, 15.0, commands.BucketType.channel)

    @app_commands.autocomplete(title=rule_autocomplete)
    @app_commands.command()
    async def rule(self, ctx: discord.Interaction, title: str) -> None:
        """Posts a rule

        Args:
            ctx (discord.ctx): Context
            title (str): The title of the rule
        """

        try:
            channel = ctx.guild.get_channel(guild_service.get_guild().channel_rules)
            msg = await channel.fetch_message(int(title))

            await send_success(ctx, embed=msg.embeds[0], ephemeral=False)
        except:
            await send_error(ctx, "Could not find rule")

    @app_commands.command()
    async def userinfo(self, ctx: discord.Interaction, user: discord.Member = None) -> None:
        """Get info about a user.

        Args:
            ctx (discord.ctx): Context
            user (discord.Member, optional): User to get info of
        """

        if not user:
            user = ctx.user

        if not PermissionLevel.MOD.check(ctx) and user.id != ctx.user.id:
            raise commands.BadArgument(
                "You do not have permission to use this command.")

        usr = user_service.get_user(user.id)

        embed = Embed(title="User Information")
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.add_field(name="Username", value=f"{str(user)} ({user.mention})", inline=True)
        embed.add_field(name="Level", value=usr.level, inline=True)
        embed.add_field(name="XP", value=usr.xp, inline=True)

        roles = [r.mention for r in user.roles if r.name != "@everyone"]
        roles.reverse()
        embed.add_field(name="Roles", value=" ".join(roles), inline=False)

        embed.add_field(name="Join date", value=f"<t:{int(user.joined_at.timestamp())}> (<t:{int(user.joined_at.timestamp())}:R>)", inline=True)
        embed.add_field(name="Account creation date", value=f"<t:{int(user.created_at.timestamp())}> (<t:{int(user.created_at.timestamp())}:R>)", inline=True)

        await ctx.response.send_message(embed=embed)

    @app_commands.command()
    async def jumbo(self, ctx: discord.Interaction, emoji: str) -> None:
        """Post large version of a given emoji

        Args:
            ctx (discord.ctx): Context
            emoji (str): The emoji you want to get the large version of

        """

        # non-mod users will be ratelimited
        bot_chan = guild_service.get_guild().channel_botspam
        if not PermissionLevel.MOD.check(ctx) and ctx.channel_id != bot_chan:
            bucket = self.spam_cooldown.get_bucket(ctx)
            if bucket.update_rate_limit():
                raise commands.BadArgument("This command is on cooldown.")

        # is this a regular Unicode emoji?
        try:
            em = await commands.PartialEmojiConverter().convert(self, emoji)
        except commands.PartialEmojiConversionFailure:
            em = emoji
        if isinstance(em, str):
            emoji_url_file = None
            for emoji in ctx.guild.emojis:
                if emoji.name == em:
                    emoji_url_file = emoji.url
                    break
            if emoji_url_file is None:
                raise commands.BadArgument(
                    "Couldn't find a suitable emoji.")

            _file = discord.File(io.BytesIO(base64.b64decode(emoji_url_file)), filename='image.png')
            await ctx.response.send_message(file=_file)
        else:
            await ctx.response.send_message(em.url)

    @app_commands.command()
    async def avatar(self, ctx: discord.Interaction, user: discord.User = None) -> None:
        """Get avatar of another user or yourself.

        Args:
            ctx (discord.ctx): Context
            user (discord.Member, optional): The user to get the avatar of
        """

        if user is None:
            user = ctx.user

        embed = discord.Embed(title=f"{user}'s avatar")
        animated = ["gif", "png", "jpeg", "webp"]
        not_animated = ["png", "jpeg", "webp"]

        avatar = user.avatar or user.default_avatar

        def fmt(format_):
            return f"[{format_}]({avatar.replace(format=format_, size=4096)})"

        if user.display_avatar.is_animated():
            embed.description = f"View As\n {'  '.join([fmt(format_) for format_ in animated])}"
        else:
            embed.description = f"View As\n {'  '.join([fmt(format_) for format_ in not_animated])}"

        embed.set_image(url=avatar.replace(size=4096))
        embed.color = discord.Color.random()

        view = discord.utils.MISSING
        if isinstance(user, discord.Member) and user.guild_avatar is not None:
            view = PFPView(ctx, embed)
            view.add_item(PFPButton(ctx, user))

        whisper = False
        bot_chan = guild_service.get_guild().channel_botspam
        if not PermissionLevel.MOD.check(ctx) and ctx.channel_id != bot_chan:
            whisper = True

        await ctx.response.send_message(embed=embed, ephemeral=whisper, view=view)

    @app_commands.command(name="8ball")
    async def _8ball(self, ctx: discord.Interaction, question: str) -> None:
        """Ask a question and the bot will answer with Magic!

        Args:
            ctx (discord.ctx): Context
            question (str): Question to as
        """
        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                     "Don’t count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.", "My sources say no.",
                     "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.",
                     "Yes.", "Yes – definitely.", "You may rely on it.", "<:yes:1044717821399154840>"]

        whisper = False
        bot_chan = guild_service.get_guild().channel_botspam
        if not PermissionLevel.MOD.check(ctx) and ctx.channel_id != bot_chan:
            whisper = True

        response = random.choice(responses)
        embed = discord.Embed(color=discord.Color.blurple())
        embed.add_field(name="Question", value=discord.utils.escape_markdown(
            question), inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.response.send_message(embed=embed, ephemeral=whisper)
