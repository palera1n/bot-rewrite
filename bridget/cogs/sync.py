import asyncio
import aiohttp
import discord
import os
import requests
import time
import logging

from discord.ext import commands

from utils import Cog
from utils.config import cfg
from utils import enums
from utils.services import guild_service


class Sync(Cog):
    async def get_bearer(self) -> dict:  # Sorry, can't provide explicit types, `dict` is the best i can do
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://discord.com/api/v10/oauth2/token',
                data=aiohttp.FormData(
                    {'grant_type': 'client_credentials', 'scope': 'applications.commands.permissions.update'}
                ),
                auth=aiohttp.BasicAuth(os.environ.get("CLIENT_ID"), os.environ.get("CLIENT_SECRET")),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            ) as resp:
                return await resp.json()

    @commands.command()
    async def sync(self, ctx: commands.Context) -> None:
        """Sync slash commands"""

        if ctx.author.id != cfg.owner_id:
            await ctx.reply(
                embed=discord.Embed(
                    color=discord.Color.red(),
                    description="You are not allowed to use this command.",
                ),
            )
            return

        ctx.reply(
            embed=discord.Embed(color=discord.Color.blurple(), description="Syncing commands, this will take a while")
        )

        async with ctx.typing():
            await self.bot.tree.sync(guild=discord.Object(id=cfg.guild_id)) # causes the infinte sync sometimes
            await self.bot.tree.sync() # this too
            try:
                token = await self.get_bearer()
                bearer = token['access_token']
                headers = {'Authorization': f'Bearer {bearer}'}
                # async with aiohttp.ClientSession(headers=headers) as session:
                #     async with session.get(f"https://discord.com/api/v10/applications/{os.environ.get('CLIENT_ID')}/guilds/{os.environ.get('GUILD_ID')}/commands", headers=headers) as resp:
                #         command_list = await resp.json()
                #         print(command_list)
                #         for command in command_list:
                #             try:
                #                 print(command)
                #                 async with session.put(f"https://discord.com/api/v10/applications/{os.environ.get('CLIENT_ID')}/guilds/{os.environ.get('GUILD_ID')}/commands/{command.id}/permissions", headers=headers):
                #                     pass
                #             except Exception as e:
                #                 print(e)
                resp = requests.get(
                    f"https://discord.com/api/v10/applications/{self.bot.application_id}/commands",
                    headers={'Authorization': f'Bot {os.environ.get("TOKEN")}'},
                )
                command_list = resp.json()
                logging.log(resp.headers, level="DEBUG")
                logging.log(command_list, level="DEBUG")
                for command in command_list:
                    while True:
                        try:
                            # print(command)
                            dpy_cmd = self.bot.tree.get_command(command['name'])
                            try:
                                cmdtype = dpy_cmd.extras['PermLevel']
                            except:
                                cmdtype = enums.PermissionLevel.EVERYONE
                            toid = 0
                            if cmdtype == enums.PermissionLevel.EVERYONE:
                                break
                            elif cmdtype >= enums.PermissionLevel.ADMIN:
                                payload = {
                                    'permissions': [{'id': os.environ.get('GUILD_ID'), 'type': 1, 'permission': False}]
                                }
                            else:
                                toid = getattr(guild_service.get_guild(), str(cmdtype))
                                payload = {
                                    'permissions': [
                                        {'id': toid, 'type': 1, 'permission': True},
                                        {'id': os.environ.get('GUILD_ID'), 'type': 1, 'permission': False},
                                    ]
                                }

                            print(payload)

                            r = requests.put(
                                f"https://discord.com/api/v10/applications/{self.bot.application_id}/guilds/{os.environ.get('GUILD_ID')}/commands/{command['id']}/permissions",
                                headers=headers,
                                json=payload,
                            )
                            if r.status_code == 429:
                                logging.log('got ratelimited, sleeping for 10 seconds')
                                time.sleep(10)
                            elif r.status_code == 400:
                                raise Exception(f"got 400, response json: {r.json()}")
                            elif not r.ok:
                                pass
                            else:
                                break

                        except Exception as e:
                            raise e

            except Exception as e:
                await ctx.reply(
                    embed=discord.Embed(
                        color=discord.Color.green(),
                        description="Synced slash commands, but failed to set permissions",
                    ),
                    delete_after=5,
                )
                print(e)
                await asyncio.sleep(8)
                await ctx.message.delete()
                raise e

        await ctx.reply(
            embed=discord.Embed(
                color=discord.Color.green(),
                description="Synced slash commands.",
            ),
            delete_after=5,
        )

        await asyncio.sleep(5)
        await ctx.message.delete()
