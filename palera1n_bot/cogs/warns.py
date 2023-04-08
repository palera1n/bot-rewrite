import mongoengine
import discord
from discord.ext import commands
import os
import datetime

class Warn(mongoengine.Document):
    user_id = mongoengine.IntField(required=True)
    reason = mongoengine.StringField(required=True)
    guild_id = mongoengine.IntField(required=True)
    moderator_id = mongoengine.IntField(required=True)
    timestamp = mongoengine.DateTimeField(required=True)

    case_id = mongoengine.IntField(required=True)

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.Cog.listener()
    async def on_ready(self):
        print("Warn cog is ready")

    @commands.has_permissions(kick_members=True)
    @discord.slash_command(guild_id=os.getenv("GUILD_ID"))
    async def warn(self, ctx, user: discord.Member, *, reason):
        case_id = len(Warn.objects(guild_id=ctx.guild.id))
        warn = Warn(user_id=user.id, reason=reason, guild_id=ctx.guild.id, moderator_id=ctx.author.id, timestamp=datetime.datetime.utcnow(), case_id=case_id)
        warn.save()
        embed = discord.Embed(
            title=f"Warned {user.name}",
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Case ID", value=case_id, inline=True)
        embed.set_thumbnail(url=str(user.display_avatar)) # str will make it a URL


        await ctx.respond(embed=embed)
    
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You do not have the required permissions to use this command.", ephemeral=True)

    

def setup(bot):
    bot.add_cog(WarnCog(bot))
