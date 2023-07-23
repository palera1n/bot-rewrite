# TODO: write migrate.py

import asyncio
import mongoengine
import os
import discord

import girmodel

from bridget import model
from utils import services
from typing import *

girfilter: List[girmodel.FilterWord] = []
girraid = []

class MigrateClient(discord.Client):
    async def on_ready(self):
        print("Migrating filter!")

        rules = await self.get_guild(services.guild_id).fetch_automod_rules()
        for filter in girfilter:
            try:
                guild: model.Guild = self.get_guild(int(services.guild_id))
                if guild == None:
                    continue
                rule = self.get_guild(int(services.guild_id)).get_role(filter.bypass)
                if filter.notify:
                    rule = [ x for x in rules if rule.name in x.name and rule.name.endswith('🚨') ]
                else:
                    rule = [ x for x in rules if rule.name in x.name and not rule.name.endswith('🚨')]
                if len(rule) == 0:
                    return
                rule = rule[0]

                # extract the trigger to modify it
                trig = rule.trigger


                phrase = filter.word
                trig.keyword_filter.append(phrase)

                # edit the rule trigger
                await rule.edit(trigger=trig, reason="Filtered word/regex/whitelist has been added (Migration)")
            except:
                continue

        print("Migrating AntiRaid!")

        raidrule = []

        for rule in rules:
            if discord.AutoModRuleActionType.timeout in rule.actions:
                raidrule = rule

        for filter in girraid:
            trig = rule.trigger


            phrase = filter.word
            trig.keyword_filter.append(phrase)

            # edit the rule trigger
            await raidrule.edit(trigger=trig, reason="Filtered word/regex/whitelist has been added (Migration)")

        print("Disconnecting!")
        await self.close()


async def migrate() -> None:
    global girfilter, girraid
    print("Hello!")
    print("We need you to answer a few questions to start the migration process ")
    setup_did = input("Did you run 'pdm run setup'? (y/n) ")
    if setup_did.lower() != 'y':
        print("Please run it, then run this again")
        return

    srv_connect = input(
        "Please enter your MongoDB connection string for the GIRRewrite database (eg. mongodb://localhost:27017) "
    )

    print("Migrating database!")


    print("Connecting to the GIR database!")
    mongoengine.connect("botty", host=srv_connect)


    print("Caching tags and memes!")

    girtags = girmodel.Guild.objects(_id=os.getenv("GUILD_ID")).first().tags
    girmemes = girmodel.Guild.objects(_id=os.getenv("GUILD_ID")).first().memes

    print("Caching cases!")

    gircases = girmodel.Cases.objects(_id=os.getenv("GUILD_ID")).first().cases

    print("Caching giveaways!")

    girgiveaways = girmodel.Giveaway.objects(_id=os.getend("GUILD_ID"))

    print("Caching users!")

    girusers = girmodel.User.objects(_id=os.getend("GUILD_ID"))

    print("Caching filter!")

    girfilter = girmodel.Guild.objects(_id=os.getenv("GUILD_ID")).first().filter_words

    print("Caching AntiRaid filter!")
    girraid = girmodel.Guild.objects(_id=os.getenv("GUILD_ID")).first().raid_phrases

    mongoengine.disconnect()
    
    mongoengine.connect("bridget", host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT")))

    for tag in girtags:
        ntag = model.Tag()
        ntag.name = tag.name
        ntag.content = tag.content
        ntag.added_by_tag = tag.added_by_tag
        ntag.added_by_id = tag.added_by_id
        ntag.added_date = tag.added_date
        ntag.use_count = tag.use_count
        ntag.image = tag.image
        ntag.button_links = tag.button_links
        ntag.save()

    for meme in girmemes:
        ntag = model.Tag()
        ntag.name = meme.name
        ntag.content = meme.content
        ntag.added_by_tag = meme.added_by_tag
        ntag.added_by_id = meme.added_by_id
        ntag.added_date = meme.added_date
        ntag.use_count = meme.use_count
        ntag.image = meme.image
        ntag.button_links = meme.button_links
        ntag.save()

    for case in gircases:
        nfract = model.Infraction()
        nfract._type = case._type
        nfract._id = case._id
        nfract.until = case.until
        nfract.mod_id = case.mod_id
        nfract.mod_tag = case.mod_tag
        nfract.reason = case.reason
        nfract.punishment = max(case.punishment // 50, 9) if case.punishment else case.punishment
        nfract.lifted = case.lifted
        nfract.lifted_by_tag = case.lifted_by_tag
        nfract.lifted_by_id = case.lifted_by_id
        nfract.lifted_reason = case.lifted_reason
        nfract.lifted_date = case.lifted_date
        nfract.save()

    for giveaway in girgiveaways:
        ngive = model.Giveaway()
        ngive._id = giveaway._id
        ngive.is_ended = giveaway.is_ended
        ngive.end_time = giveaway.end_time
        ngive.channel = giveaway.channel
        ngive.name = giveaway.name
        ngive.entries = giveaway.entries
        ngive.previous_winners = giveaway.previous_winners
        ngive.sponsor = giveaway.sponsor
        ngive.winners = giveaway.winners
        ngive.save()

    for user in girusers:
        nuser = model.User()
        wptoapply = user // 50
        if wptoapply >= 10:
            wptoapply = 9
        nuser._id = user._id
        nuser.is_clem = user.is_clem
        nuser.is_xp_frozen = user.is_xp_frozen
        nuser.is_muted = user.is_muted
        nuser.is_music_banned = user.is_music_banned
        nuser.was_warn_kicked = user.was_warn_kicked
        nuser.birthday_excluded = user.birthday_excluded
        nuser.raid_verified = user.raid_verified
        nuser.xp = user.xp
        nuser.trivia_points = user.trivia_points
        nuser.level = user.level
        nuser.warn_points = wptoapply
        nuser.offline_report_ping = user.offline_report_ping
        nuser.timezone = user.timezone
        nuser.birthday = user.birthday
        nuser.sticky_roles = user.sticky_roles
        nuser.command_bans = user.command_bans
        nuser.save()

    for filter in girfilter:
        nfilter = model.FilterWord()
        nfilter.notify = filter.notify
        nfilter.bypass = filter.bypass
        nfilter.word = filter.word
        nfilter.false_positive = filter.false_positive
        nfilter.piracy = filter.piracy

    if input("Do you want to migrate additional steps? (eg. migrate filter) This requires access to the Discord bot (n/y)").lower() != 'y':
        exit(0)

    client = MigrateClient()

    client.run()

    print("Finished!")

    # model.Guild.objects(_id=os.getenv("GUILD_ID")).first().tags.

asyncio.run(migrate())