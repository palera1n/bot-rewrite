import discord
import pgpy
import io

from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils import Cog, send_error, send_success
from model import User, PGPKey
from utils.modals import PGPKeyModal
from utils.services import user_service

class PGPKeys(Cog, commands.GroupCog, group_name="pgpkeys"):
    @app_commands.command()
    async def add(self, ctx: discord.Interaction, keyfile: discord.Attachment) -> None:
        # await ctx.response.send_modal(modal)
        # await modal.wait()
        # if not modal.key:
        #     return
        
        db_user = user_service.get_user(ctx.user.id)

        key = await keyfile.read()
        
        if len(key) == 0:
            return
        try:
            parsed_key = pgpy.PGPKey()
            parsed_key.parse(key)
            keyobject = PGPKey()
            keyobject.key = bytes(key)
            keyobject.key_signature = str(parsed_key.fingerprint)
            keyobject.full_name = str(parsed_key.userids[0].name)
            keyobject.email = str(parsed_key.userids[0].email)
            keyobject.user = ctx.user.id
            keyobject._id = ctx.user.id
        except pgpy.errors.PGPError:
            send_error(ctx, "Invalid PGP key!")

        keyobject.save()
        pgpkeys = PGPKey.objects(_id=ctx.user.id).all()
        embed = discord.Embed(title="PGP key added")
        embed.description = f"Added PGP key with fingerprint `{keyobject.key_signature}` to your account."
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def remove(self, ctx: discord.Interaction, signature: str) -> None:
        db_user = user_service.get_user(ctx.user.id)
        key = PGPKey.objects(_id=ctx.user.id, key_signature=signature).first()
        if not key:
            await ctx.response.send_message("PGP key not found!", ephemeral=True)
            return
        db_user.save()
        embed = discord.Embed(title="PGP key removed")
        embed.description = f"Removed PGP key with fingerprint `{key.key_signature}` from your account."
        key.delete()
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def list(self, ctx: discord.Interaction, user: Optional[discord.User]) -> None:
        if user == None:
            user: discord.User = ctx.user
        keys = PGPKey.objects(_id=ctx.user.id).all()
        embed = discord.Embed(title="PGP keys")
        if not keys:
            await send_error(ctx, f"{user.display_name} doesn't have any keys added")
            return
        embed.description = f"Here are all the PGP keys {user.display_name} has added to {user.display_name}'s account."
        for key in keys:
            try:
                embed.add_field(name=key.key_signature, value=f"Full name: {key.full_name}\nEmail: {key.email}\nFingerprint: {key.key_signature}", inline=False)
            except:
                continue
        
        await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    async def get(self, ctx: discord.Interaction, signature: str) -> None:
        key = PGPKey.objects(key_signature=signature).first()
        if not key:
            await ctx.response.send_message("PGP key not found!", ephemeral=True)
            return
        
        embed = discord.Embed(title="PGP key")
        embed.description = f"Here is the PGP key with fingerprint `{key.key_signature}`."
        embed.add_field(name=key.key_signature, value=f"Full name: {key.full_name}\nEmail: {key.email}\nFingerprint: {key.key_signature}", inline=False)
        await ctx.response.send_message(embed=embed, ephemeral=True, file=discord.File(io.BytesIO(bytes(str(pgpy.PGPKey.from_blob(key.key)[0].pubkey), encoding="UTF-8")), filename=f"{key.key_signature}.asc"))


