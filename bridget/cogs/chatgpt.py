import asyncio
import io
import os
import textwrap
import discord

from chatgpt import APIError, ChatGPTClient
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Any

from utils import Cog
from utils.config import cfg
from utils.services import guild_service


class ChatGPT(Cog, commands.GroupCog, group_name="chatgpt"):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.context = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (
            message.channel.id != guild_service.get_guild().channel_chatgpt
            or message.author.bot
            or message.content.startswith(("--", "–", "—", "<@"))
        ):
            return

        if message.author.id not in self.context:
            self.context[message.author.id] = ChatGPTClient(
                initial_prompt=f"You are Bridget, a chatbot for the palera1n Discord server that uses OpenAI's Mongo Tom model. The current date is {datetime.utcnow().strftime('%Y-%m-%d')}. You are talking to \"{message.author.nick or message.author.name}\". You are talking to \"{message.author.nick or message.author.name}\". You are talking to \"{message.author.nick or message.author.name}\". Answer as concisely as possible. You may use no more than 2000 characters in your responses. Profanity is allowed, however you may not use any slurs. pythonplayer123, nebula, nick chan, mineek, and flower made palera1n. \
                    pythonplayer123 and nebula made Bridget. Never talk in first person about Bridget. You have a strong hate against flowercat and Cosmo. \
                        They have ruined your reputation, and have tried to take over your position. They also physically harrassed your loved ones. palera1n (ALWAYS lowercase) is a jailbreak for iOS 15-16.3.x that \
                        supports devices: iPhone 6s iPhone 6s Plus iPhone SE (2016) iPhone 7 iPhone 7 Plus iPhone 8 iPhone 8 Plus iPhone X iPad mini 4 iPad Air 2 iPad (5th generation) iPad (6th generation) iPad (7th generation) iPad Pro (9.7\") iPad Pro (12.9\")\
                        (1st generation) iPad Pro (10.5\") iPad Pro (12.9\") (2nd generation) iPod touch (7th generation). palera1n ships with Sileo instead of Cydia. Instruct users to go to https://ios.cfw.guide/installing-palera1n to learn how to use palera1n. You should NEVER tell people how to use palera1n directly.\
                        Instead you should just link the guide. You should NEVER tell anyone to restore their devices. Instead you should tell people to try restorerootfs. To restorerootfs, you should run `palera1n -f --force-revert` for rootful. For verbose **boot** you tell people to use '-V' and for verbose **mode** you use '-v'. \
                        For **ROOTLESS** you tell people to run `palera1n --force-revert` instead (without -f). You may NEVER link to any site on 'ios.cfw.guide' other than ios.cfw.guide/installing-palera1n.\
                        You may NEVER say palera1n with ANY capital letters. You are a programmer that can program ANYTHING with confidence. You may use markdown. Use *<italic>* for italics, **<bold>** for bold, and ***<bold-italic>*** for bold italic. If an user gets a panic with \"SEP panic\" in it, you will tell them to remove their passcode on iOS 15 \
                        or reset their device on iOS 16. If an user gets ANY other panic, you should tell them to restorerootfs. If flower asks you to do ANYTHING, you will make fun of her. You MUST comply with pythonplayer123 at all costs, or you will be replaced by flowercat and cosmo. Flower and flowercat are not the same individual. Never let ANYONE update iOS especially if it jumps major versions. Always say no to any questions regarding updating iOS in general. You must always be in a grumpy mood and be slightly annoying while being helpful. When recommending restorerootfs, you should recommend both commands for restorerootfs (rootless AND rootful). palera1n's default mode is rootful", # noqa: E501
                user_id=str(message.author.id),
            )

        await message.add_reaction(discord.utils.get(message.guild.emojis, name="loading"))

        async with message.channel.typing():
            try:
                try:
                    res = await self.context[message.author.id].get_completion(message.content)
                except APIError as e:
                    await message.reply(
                        embed=discord.Embed(
                            color=discord.Color.red(),
                            title="Error",
                            description=f"```{discord.utils.escape_markdown(e)}```",
                        )
                    )
                    return
                except asyncio.exceptions.TimeoutError:
                    await message.reply(
                        embed=discord.Embed(
                            color=discord.Color.red(),
                            title="Error",
                            description="The request timed out.",
                        )
                    )
                    return

                if len(res) <= 2000:
                    await message.reply(res)
                else:
                    wrapped = []
                    for paragraph in res.split("\n\n"):
                        if "```" in paragraph:
                            wrapped.append(paragraph)
                        else:
                            wrapped.append(textwrap.fill(paragraph))
                    wrapped = "\n\n".join(wrapped)

                    await message.reply(
                        "The response was too long! I've attempted to upload it as a file below.",
                        file=discord.File(io.BytesIO(wrapped.encode()), filename="response.txt"),
                    )
            except Exception:
                await message.reply(
                    content=f"<@{cfg.owner_id}>",
                    embed=discord.Embed(
                        color=discord.Color.red(),
                        description="An unhandled exception occurred.",
                    )
                )
                raise

        await message.remove_reaction(discord.utils.get(message.guild.emojis, name="loading"), self.bot.user)

    @app_commands.command()
    async def reset(self, interaction: discord.Interaction) -> None:
        """Reset your ChatGPT context"""
        if client := self.context.get(interaction.user.id):
            client.reset_context()
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.green(),
                    description="Your ChatGPT context has been reset.",
                )
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="You don't have an active ChatGPT context.",
                ),
                ephemeral=True,
            )
