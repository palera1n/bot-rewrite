import base64
import discord
import io
import random

from discord import Color, app_commands, Embed
from discord.ext import commands
from discord.utils import format_dt

from utils import Cog, send_error, send_success
from utils.autocomplete import rule_autocomplete
from utils.enums import PermissionLevel
from utils.errors import MissingPermissionsError
from utils.menus import Menu, PFPButton, PFPView
from utils.services import guild_service, user_service
from utils.utils import determine_emoji, get_warnpoints, pun_map


class InfractionFormatter:
    def __init__(self, user):
        self.user = user

    def format_infractions_page(self, ctx: discord.Interaction, entries: dict, current_page: int, all_pages: list) -> Embed:
        page_count = 0

        user = self.user
        u = user_service.get_user(user.id)

        for page in all_pages:
            for infraction in page:
                page_count += 1
        embed = discord.Embed(
            title=f'Infractions - {get_warnpoints(u)} warn points', color=discord.Color.blurple())
        embed.set_author(name=user, icon_url=user.display_avatar)
        for infraction in entries:
            timestamp = infraction.date
            formatted = f"{format_dt(timestamp, style='F')} ({format_dt(timestamp, style='R')})"
            if infraction._type == "WARN" or infraction._type == "LIFTWARN":
                if infraction.lifted:
                    embed.add_field(name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id} [LIFTED]',
                                    value=f'**Points**: {infraction.punishment}\n**Reason**: {infraction.reason}\n**Lifted by**: {infraction.lifted_by_tag}\n**Lift reason**: {infraction.lifted_reason}\n**Warned on**: {formatted}', inline=True)
                elif infraction._type == "LIFTWARN":
                    embed.add_field(name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id} [LIFTED (legacy)]',
                                    value=f'**Points**: {infraction.punishment}\n**Reason**: {infraction.reason}\n**Moderator**: {infraction.mod_tag}\n**Warned on**: {formatted}', inline=True)
                else:
                    embed.add_field(name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id}',
                                    value=f'**Points**: {infraction.punishment}\n**Reason**: {infraction.reason}\n**Moderator**: {infraction.mod_tag}\n**Warned on**: {formatted}', inline=True)
            elif infraction._type == "MUTE" or infraction._type == "REMOVEPOINTS":
                embed.add_field(name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id}',
                                value=f'**{pun_map[infraction._type]}**: {infraction.punishment}\n**Reason**: {infraction.reason}\n**Moderator**: {infraction.mod_tag}\n**Time**: {formatted}', inline=True)
            elif infraction._type in pun_map:
                embed.add_field(name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id}',
                                value=f'**Reason**: {infraction.reason}\n**Moderator**: {infraction.mod_tag}\n**{pun_map[infraction._type]} on**: {formatted}', inline=True)
            else:
                embed.add_field(name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id}',
                                value=f'**Reason**: {infraction.reason}\n**Moderator**: {infraction.mod_tag}\n**Time**: {formatted}', inline=True)
        embed.set_footer(
            text=f"Page {current_page} of {len(all_pages)} - newest infractions first ({page_count} total infractions)")
        return embed


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

        if not PermissionLevel.MOD == ctx.user and user.id != ctx.user.id:
                MissingPermissionsError.throw([f"<@&{guild_service.get_guild().role_moderator}>"])

        usr = user_service.get_user(user.id)
        infractions = user_service.get_infractions(user.id).infractions

        embed = Embed(title="User Information")
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.add_field(name="Username", value=f"{str(user)} ({user.mention})", inline=True)
        embed.add_field(
            name="Level", value=usr.level if not usr.is_clem else "CLEMMED", inline=True)
        embed.add_field(
            name="XP", value=usr.xp if not usr.is_clem else "CLEMMED", inline=True)
        embed.add_field(
            name="Punishments", value=f"{get_warnpoints(usr)} warn point(s)\n{len(infractions)} infraction(s)", inline=True)

        if len(infractions) > 0:
            text = []
            i = 0
            for inf in reversed(infractions):
                punishment = inf.punishment if inf._type != "WARN" else f'{inf.punishment} points'
                text.append(f"**{inf._type}** - {punishment} - {inf.reason} - <t:{int(inf.date.timestamp())}:R>")
                i += 1
                if i >= 3:
                    break
            embed.add_field(
                name="Infractions", value='\n'.join(text), inline=False)

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
        if not PermissionLevel.MOD == ctx.user and ctx.channel_id != bot_chan:
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

        def fmt(format_) -> str:
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
        if not PermissionLevel.MOD == ctx.user and ctx.channel_id != bot_chan:
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
        if not PermissionLevel.MOD == ctx.user and ctx.channel_id != bot_chan:
            whisper = True

        response = random.choice(responses)
        embed = discord.Embed(color=discord.Color.blurple())
        embed.add_field(name="Question", value=discord.utils.escape_markdown(
            question), inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.response.send_message(embed=embed, ephemeral=whisper)

    @app_commands.command()
    async def infractions(self, ctx: discord.Interaction, user: discord.Member = None) -> None:
        """Show your or another user's infractions

        Args:
            ctx (discord.ctx): Context
            user (discord.Member, optional): User to get infractions of
        """

        if not user:
            user = ctx.user

        whisper = False
        bot_chan = guild_service.get_guild().channel_botspam
        if not PermissionLevel.MOD == ctx.user and ctx.channel_id != bot_chan:
            whisper = True

        if not PermissionLevel.MOD == ctx.user and user.id != ctx.user.id:
            MissingPermissionsError.throw([f"<@&{guild_service.get_guild().role_moderator}>"])

        results = user_service.get_infractions(user.id)
        if len(results.infractions) == 0:
            await send_error(ctx, f'{user.mention} has no infractions.', delete_after=5)
            return 

        # filter out unmute infractions because they are irrelevant
        infractions = [infraction for infraction in results.infractions if infraction._type != "UNMUTE"]
        # reverse so newest infractions are first
        infractions.reverse()

        fmt = InfractionFormatter(user)

        menu = Menu(ctx, infractions, per_page=10,
                    page_formatter=fmt.format_infractions_page, whisper=whisper)
        await menu.start()

    @app_commands.command()
    async def warnpoints(self, ctx: discord.Interaction, member: discord.Member = None) -> None:
        """Show your or another member's warnpoints

        Args:
            ctx (discord.ctx): Context
            member (discord.Member, optional): Member to get warnpoints of
        """

        if not member:
            member = ctx.user

        if not PermissionLevel.MOD == ctx.user and member.id != ctx.user.id:
                MissingPermissionsError.throw([f"<@&{guild_service.get_guild().role_moderator}>"])

        usr = user_service.get_user(member.id)

        embed = Embed(title="Warn Points")
        embed.color = Color.orange()
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name="Member", value=f"{member.mention}\n{str(member)}\n({member.id})", inline=True)
        embed.add_field(
            name="Warn Points", value=f"{get_warnpoints(usr)}", inline=True)

        await ctx.response.send_message(embed=embed)

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if len(message.attachments) == 1 and message.attachments[0].filename == "Adjustments.plist":
            await message.reply(
                file=discord.File(
                    fp=io.BytesIO(await message.attachments[0].read()),
                    filename="image.jpg",
                ),
                mention_author=False,
            )

