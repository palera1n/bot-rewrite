import asyncio
import os
import mongoengine

from model.guild import Guild


async def setup() -> None:
    print("STARTING SETUP...")
    guild = Guild()

    # you should have this setup in the .env file beforehand
    guild._id = int(os.environ.get("GUILD_ID"))

    # If you're re-running this script to update a value, set case_id
    # to the last unused case ID or else it will start over from 1!
    guild.case_id = 71

    guild.role_administrator = 1096623117780140072
    guild.role_moderator = 1096623117763354713
    guild.role_birthday = 1096623117763354710
    guild.role_helper = 1096623117763354708
    guild.role_dev = 123
    guild.role_memberone = 1028693923008364586
    guild.role_memberedition = 1096623117746573377
    guild.role_memberpro = 1096623117746573376
    guild.role_memberplus = 1096623117746573375
    guild.role_memberultra = 123
    guild.role_reportping = 1096623117746573374

    guild.channel_reports = 1096623118761599051
    guild.channel_mempro_reports = 1096623118761599052
    guild.channel_emoji_log = 1096623118761599050
    guild.channel_private = 1096623118761599049
    guild.channel_reaction_roles = 1028693665050263612
    guild.channel_rules = 1096623118526714007
    guild.channel_public = 1096623119009071235
    guild.channel_common_issues = 1096623119009071237
    guild.channel_general = 1096623119009071243
    guild.channel_development = 1096623119214579813
    guild.channel_botspam = 1096623119214579812
    guild.channel_chatgpt = 1097876598428008528
    guild.channel_msg_logs = 1097434149649924107
    guild.channel_support = 1097617990515691532

    guild.logging_excluded_channels = []
    guild.filter_excluded_channels = []
    guild.filter_excluded_guilds = []

    guild.save()
    print("DONE")

if __name__ == "__main__":
    if os.environ.get("DB_CONNECTION_STRING") is None:
        mongoengine.register_connection(
            host=os.environ.get("DB_HOST"),
            port=int(
                os.environ.get("DB_PORT")),
            alias="default",
            name="bridget")
    else:
        mongoengine.register_connection(
            host=os.environ.get("DB_CONNECTION_STRING"),
            alias="default",
            name="bridget")
    res = asyncio.get_event_loop().run_until_complete(setup())
