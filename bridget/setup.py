import asyncio
import os

import mongoengine

from model.guild import Guild


async def setup():
    print("STARTING SETUP...")
    guild = Guild()

    # you should have this setup in the .env file beforehand
    guild._id = int(os.environ.get("GUILD_ID"))

    # If you're re-running this script to update a value, set case_id
    # to the last unused case ID or else it will start over from 1!
    guild.case_id = 20

    # required for permissions framework!
    # put in the role IDs for your server here
    guild.role_administrator = 1096623117780140072
    # put in the role IDs for your server here
    guild.role_moderator = 1096623117763354713
    # put in the role IDs for your server here
    guild.role_birthday = 1096623117763354710
    guild.role_helper = 1096623117763354708  # put in the role IDs for your server here
    guild.role_dev = 123  # put in the role IDs for your server here
    # put in the role IDs for your server here
    guild.role_memberone = 1028693923008364586
    # put in the role IDs for your server here
    guild.role_memberedition = 1096623117746573377
    # put in the role IDs for your server here
    guild.role_memberpro = 1096623117746573376
    # put in the role IDs for your server here
    guild.role_memberplus = 1096623117746573375
    guild.role_memberultra = 123  # put in the role IDs for your server here

    # put in the channel IDs for your server here
    guild.channel_reports = 1096623118761599051
    # channel where geniuses can report to
    # put in the channel IDs for your server here
    guild.channel_mempro_reports = 1096623118761599052
    # channel where reactions will be logged
    # put in the channel IDs for your server here
    guild.channel_emoji_log = 1096623118761599050
    # channel for private mod logs
    # put in the channel IDs for your server here
    guild.channel_private = 1096623118761599049
    # channel where self-assignable roles will be posted
    # put in the channel IDs for your server here
    guild.channel_reaction_roles = 1028693665050263612
    # rules-and-info channel
    # put in the channel IDs for your server here
    guild.channel_rules = 1096623118526714007
    # channel for public mod logs
    # put in the channel IDs for your server here
    guild.channel_public = 1096623119009071235
    # optional, required for /issue command
    # put in the channel IDs for your server here
    guild.channel_common_issues = 1096623119009071237
    # #general, required for permissions
    # put in the channel IDs for your server here
    guild.channel_general = 1096623119009071243
    # required for filter
    # put in the channel IDs for your server here
    guild.channel_development = 1096623119214579813
    # required, #bot-commands channel
    # put in the channel IDs for your server here
    guild.channel_botspam = 1096623119214579812
    # optional, needed for booster #emote-suggestions channel
    guild.channel_booster_emoji = 123  # put in the channel IDs for your server here

    # you can fill these in if you want with IDs, or you ca use commands later
    # put in a channel if you want (ignored in logging)
    guild.logging_excluded_channels = []
    # put in a channel if you want (ignored in filter)
    guild.filter_excluded_channels = []
    # put guild ID to whitelist in invite filter if you want
    guild.filter_excluded_guilds = []

    # you can leave this as is if you don't want Blootooth (message mirroring system)
    guild.nsa_guild_id = 123

    guild.save()
    print("DONE")

if __name__ == "__main__":
    if os.environ.get("DB_CONNECTION_STRING") is None:
        mongoengine.register_connection(
            host=os.environ.get("DB_HOST"), port=int(os.environ.get("DB_PORT")), alias="default", name="bridget")
    else:
        mongoengine.register_connection(
            host=os.environ.get("DB_CONNECTION_STRING"), alias="default", name="bridget")
    res = asyncio.get_event_loop().run_until_complete(setup())
