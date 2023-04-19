import discord

from discord import AppCommandOptionType, app_commands


class ImageAttachment(app_commands.Transformer):
    @classmethod
    def type(cls) -> AppCommandOptionType:
        return AppCommandOptionType.attachment

    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str) -> discord.Attachment:
        if value is None:
            return

        image = await app_commands.transformers.passthrough_transformer(AppCommandOptionType.attachment).transform(interaction, value)
        _type = image.content_type
        if _type not in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
            raise app_commands.TransformerError(
                "Attached file was not an image.")

        return image
