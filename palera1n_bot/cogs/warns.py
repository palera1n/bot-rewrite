import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
import discord
from discord.ext import commands

Base = declarative_base()

class Warn(Base):
    __tablename__ = 'warns'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    server_id = Column(String)
    reason = Column(String)

class Warns(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        engine = create_engine('sqlite:///dbs/warns.db', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    @commands.command(name="warn", help="Warn a user for a reason")
    async def warn(self, ctx, user: discord.User, reason: str):
        """Warns the specified user with the given reason"""
        server_id = str(ctx.guild.id)
        user_id = str(user.id)

        warn = Warn(user_id=user_id, server_id=server_id, reason=reason)
        self.session.add(warn)
        self.session.commit()

        warncount = self.session.query(Warn).filter(Warn.user_id == user_id, Warn.server_id == server_id).count()

        await ctx.send(f"{user.name} has been warned: {reason} (Now at {warncount} warnings)")
        if warncount == 1:
            await (await user.create_dm()).send(f"{user.mention} please note that warns are permanant\nYou will be kicked at 8 warns and 10 warns will result in a ban")
        elif warncount == 8: 
            await ctx.guild.kick(user, reason="8 warnings")
        elif warncount == 10:
            await ctx.guild.ban(user, reason="10 warnings")

    @commands.command(name="warnings", help="View warnings for a user")
    async def warnings(self, ctx, user: discord.User):
        """Displays all warnings for the specified user"""
        server_id = str(ctx.guild.id)
        user_id = str(user.id)

        warnings = self.session.query(Warn).filter(Warn.user_id == user_id, Warn.server_id == server_id).all()

        if not warnings:
            await ctx.send(f"{user.name} has no warnings")
        else:
            response = f"Warnings for {user.name}:\n"
            for warn in warnings:
                response += f"{warn.reason}\n"
            await ctx.send(response)

async def setup(bot):
    await bot.add_cog(Warns(bot))
