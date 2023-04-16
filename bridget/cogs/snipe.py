import discord

from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cache = {}
        self.cache_max = 1000

    @commands.Cog.listener()
    async def on_message_edit(self, message: discord.Message, new_message: discord.Message) -> None:
        if message.author.bot:
            return

        if len(self.cache) >= self.cache_max:
            self.cache.pop(0)

        try:
            self.cache[message.channel.id]
        except KeyError:
            self.cache[message.channel.id] = []

        self.cache[message.channel.id].append(message)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        try:
            self.cache[message.channel.id]
        except KeyError:
            self.cache[message.channel.id] = []

        self.cache[message.channel.id].append(message)

    @commands.Cog.listener()
    async def on_automod_action(self, exectution: discord.AutoModAction) -> None:
        if isinstance(exectution.action.type, discord.AutoModRuleActionType.block_message):
            if len(self.cache) >= self.cache_max:
                self.cache.pop(0)

            message = exectution.action.message
            try:
                self.cache[message.channel.id]
            except KeyError:
                self.cache[message.channel.id] = []

            self.cache[message.channel.id].append(message)
    
    
    @commands.command()
    async def snipe(self, ctx: commands.Context, message: int=-1) -> None:
        """Snipe a message"""
        
        if not self.cache:
            await ctx.reply(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="No messages to snipe.",
                ),
            )
            return
        
        message = self.cache[ctx.channel.id].pop(message)
        embed = discord.Embed(
            color=discord.Color.green(),
            description=message.content,
        )
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        embed.set_footer(text=f"Sent in #{message.channel.name}")
        await ctx.reply(embed=embed)
