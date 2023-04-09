import mongoengine
import discord
from discord.ext import commands
import os
from model import User


def leaderboard():
    return User.objects[0:130].only('_id', 'xp').order_by('-xp', '-_id').select_related()

def get_user(user_id):
    return User.objects(_id=user_id).first()

def leaderboard_rank(self, xp):
        users = User.objects().only('_id', 'xp')
        overall = users().count()
        rank = users(xp__gte=xp).count()
        return (rank, overall)

def inc_xp(self, id, xp):
        """Increments user xp.
        """

        self.get_user(id)
        User.objects(_id=id).update_one(inc__xp=xp)
        u = User.objects(_id=id).first()
        return (u.xp, u.level)

def inc_level(self, id) -> None:
        """Increments user level.
        """

        self.get_user(id)
        User.objects(_id=id).update_one(inc__level=1)
