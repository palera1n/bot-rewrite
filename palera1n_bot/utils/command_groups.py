import discord


def get_modactions_group():
    return discord.SlashCommandGroup("modactions", "Subgroup containing all modactions")


modactions_group = get_modactions_group()
