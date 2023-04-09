import discord
from discord.ext import commands
import os
from utils.checks.check_invokee import check_invokee
from model import Case, Cases


class WarnCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        print("Warn cog is ready")

    @commands.has_permissions(kick_members=True)
    @discord.slash_command(guild_id=os.getenv("GUILD_ID"))
    async def warn(self, ctx, user: discord.Member, *,
                   reason: str = "No reason provided.", punishment: int = 1):
        check = await check_invokee(ctx, ctx.author, self.bot)
        if check is False:
            await ctx.respond("You do not have the required permissions \
                              to use this command. This may be due to calling \
                              this on yourself", ephemeral=True)
            return
        case_id = len(Case.objects(guild_id=ctx.guild.id))
        warn = Case(_type="WARN", mod_id=ctx.author.id,
                    mod_tag=ctx.author.name, user_id=user.id,
                    user_tag=user.name, reason=reason, punishment=punishment)
        warn.save()
        embed = discord.Embed(
            title=f"Warned {user.name}",
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention,
                        inline=True)
        embed.add_field(name="Case ID", value=case_id, inline=True)
        embed.set_thumbnail(url=str(user.display_avatar))

        await ctx.respond(embed=embed)

    @discord.slash_command(guild_id=os.getenv("GUILD_ID"))
    async def warns(self, ctx, user: discord.Member):
        warns = Cases.objects(user_id=user.id, guild_id=ctx.guild.id)
        unrevoked_warns = [warn for warn in warns if not warn.is_revoked]
        embed = discord.Embed(
                title=f"Warns for {user.name}: {len(unrevoked_warns)}",
                color=discord.Colour.blurple(),
        )
        for warn in warns:
            embed.add_field(name=f"Case ID: {warn.case_id}", value=f"Reason: \
                    {warn.reason}\nModerator: \
                    {ctx.guild.get_member(warn.moderator_id).mention}\n\
                    Timestamp: {warn.timestamp}\nRevoked: \
                    {'yes' if warn.is_revoked else 'no'}", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.has_permissions(kick_members=True)
    @discord.slash_command(guild_id=os.getenv("GUILD_ID"))
    async def removewarn(self, ctx, case_id: int):
        check = await check_invokee(ctx, ctx.author, self.bot)
        if check is False:
            await ctx.respond("You do not have the required permissions\
                    to use this command. This may be due to calling \
                    this on yourself", ephemeral=True)
            return
        warn = Case.objects(case_id=case_id, guild_id=ctx.guild.id).first()
        if warn is None:
            await ctx.respond("That case ID does not exist.", ephemeral=True)
            return
        warn.is_revoked = True
        warn.save()
        await ctx.respond(f"Warn with case ID {case_id} has been removed.")

    @warn.error
    @removewarn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have the required permissions to \
                    use this command.", ephemeral=True)


def setup(bot):
    bot.add_cog(WarnCog(bot))