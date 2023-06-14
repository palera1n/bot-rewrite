import asyncio
import discord

from discord.ext import commands
from discord.utils import format_dt
from typing import Generator, List

from utils.services import user_service
from utils.config import cfg
from utils.enums import PermissionLevel
from utils import pun_map, determine_emoji


def chunks(lst: list, n: int) -> Generator:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class Appeals(commands.Cog):
    def __init__(self, bot: commands.Bot):
        if cfg.ban_appeal_guild_id == -1 or cfg.ban_appeal_mod_role == -1:
            asyncio.run(bot.remove_cog(self))
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.guild.id != cfg.ban_appeal_guild_id:
            return
        main_guild = self.bot.get_guild(cfg.guild_id)
        main_guild_member = main_guild.get_member(member.id)
        if main_guild_member is None:
            return

        if not PermissionLevel.MOD == main_guild_member:
            try:
                await member.send(embed=discord.Embed(description=f"You cannot join {member.guild} unless you are banned!", color=discord.Color.orange()))
            except:
                pass

            await member.kick(reason="You are not allowed to join this server.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if message.guild.id != cfg.ban_appeal_guild_id:
            return
        if not message.webhook_id:
            return
        if not message.embeds:
            return

        embed = message.embeds[0]
        unban_username = embed.fields[0].value
        unban_id = embed.fields[1].value

        try:
            unban_id_parsed = int(unban_id)
            appealer = await self.bot.fetch_user(unban_id_parsed)
        except:
            appealer = None

        thread = await message.create_thread(name=f"{unban_username} ({unban_id})")
        mods_to_ping = " ".join(member.mention for member in message.guild.get_role(
            cfg.ban_appeal_mod_role).members)

        embeds_to_send = []
        if appealer is not None:
            # await thread.send(embed=await self.generate_userinfo(appealer))
            embeds_to_send.append(await self.generate_userinfo(appealer))
            infractions_embeds = await self.generate_infractions(appealer)
            if infractions_embeds is not None:
                # await thread.send(embeds=infractions_embeds)
                embeds_to_send.extend(infractions_embeds)
            else:
                # await thread.send(embed=discord.Embed(color=discord.Color.green(), description="No infractions found for this user."))
                embeds_to_send.append(discord.Embed(
                    color=discord.Color.green(), description="No infractions found for this user."))
            if message.guild.get_member(appealer.id) is not None:
                embeds_to_send.append(discord.Embed(
                    description=f"{appealer.mention} is in the unban appeals server!", color=discord.Color.green()))
                # await thread.send(embed=discord.Embed(f"{appealer.mention} is in the unban appeals server!", color=discord.Color.green()))
            else:
                embeds_to_send.append(discord.Embed(
                    description=f"{appealer} did not join the unban appeals server!", color=discord.Color.red()))
                # await thread.send(embed=discord.Embed(f"{appealer} did not join the unban appeals server!", color=discord.Color.red()))

            embeds_chunks = list(chunks(embeds_to_send, 10))
            for chunk in embeds_chunks:
                await thread.send(embeds=chunk)
        else:
            await thread.send(embed=discord.Embed(description=f"Hmm, I couldn't find {unban_username} ({unban_id}) from Discord's API. Maybe this is not a valid user!", color=discord.Color.red()))

        m = await thread.send(mods_to_ping, embed=discord.Embed(description=f"Please vote with whether or not you want to unban this user!", color=discord.Color.orange()), allowed_mentions=discord.AllowedMentions(roles=True))
        await m.add_reaction("🔺")
        await m.add_reaction("🔻")
        await m.add_reaction("❌")
        await m.pin()

        await thread.send(unban_id)

    async def generate_userinfo(self, appealer: discord.User) -> discord.Embed:
        results = user_service.get_user(appealer.id)

        embed = discord.Embed(title=f"User Information",
                              color=discord.Color.blue())
        embed.set_author(name=appealer)
        embed.set_thumbnail(url=appealer.display_avatar)
        embed.add_field(name="Username",
                        value=f'{appealer} ({appealer.mention})', inline=True)
        embed.add_field(
            name="Level", value=results.level if not results.is_clem else "CLEMMED", inline=True)
        embed.add_field(
            name="XP", value=results.xp if not results.is_clem else "CLEMMED", inline=True)
        embed.add_field(
            name="Punishments", value=f"{results.warn_points} warn points\n{len(user_service.get_infractions(appealer.id).infractions)} infractions", inline=True)

        embed.add_field(name="Account creation date",
                        value=f"{format_dt(appealer.created_at, style='F')} ({format_dt(appealer.created_at, style='R')})", inline=True)
        return embed

    async def generate_infractions(self, appealer: discord.User) -> List[discord.Embed]:
        results = user_service.get_infractions(appealer.id)
        if not results.infractions:
            return None
        infractions = [infraction for infraction in results.infractions if infraction._type != "UNMUTE"]
        # reverse so newest infractions are first
        infractions.reverse()

        infractions_chunks = list(chunks(infractions, 10))

        embeds = []
        for i, entries in enumerate(infractions_chunks):
            embed = discord.Embed(
                title=f'Infractions - Page {i + 1}', color=discord.Color.blurple())
            embed.set_author(name=appealer, icon_url=appealer.display_avatar)
            for infraction in entries:
                timestamp = infraction.date
                formatted = f"{format_dt(timestamp, style='F')} ({format_dt(timestamp, style='R')})"
                if infraction._type == "WARN" or infraction._type == "LIFTWARN":
                    if infraction.lifted:
                        embed.add_field(
                            name=f'{determine_emoji(infraction._type)} Infraction #{infraction._id} [LIFTED]', value=f'**Points**: {infraction.punishment}\n**Reason**: {infraction.reason}\n**Lifted by**: {infraction.lifted_by_tag}\n**Lift reason**: {infraction.lifted_reason}\n**Warned on**: {formatted}', inline=True)
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
            embeds.append(embed)
        return embeds

