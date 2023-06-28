import mongoengine
import discord
from discord.ext import commands
import os
from typing import Any, Dict, Tuple, Counter
from model import User, Infraction, Infractions
from model.user import User


def get_user(id: int) -> User:
    """Look up the User document of a user, whose ID is given by `id`.
    If the user doesn't have a User document in the database, first create that.

    Parameters
    ----------
    id : int
        The ID of the user we want to look up

    Returns
    -------
    User
        The User document we found from the database.
    """

    user = User.objects(_id=id).first()
    # first we ensure this user has a User document in the database before
    # continuing
    if not user:
        user = User()
        user._id = id
        user.save()
    return user


def leaderboard() -> list:
    return User.objects[0:130].only('_id', 'xp').order_by(
        '-xp', '-_id').select_related()


def leaderboard_rank(xp: int) -> Tuple[int, int]:
    users = User.objects().only('_id', 'xp')
    overall = users().count()
    rank = users(xp__gte=xp).count()
    return (rank, overall)


def inc_points(_id: int, points: int) -> None:
    """Increments the warnpoints by `points` of a user whose ID is given by `_id`.
    If the user doesn't have a User document in the database, first create that.

    Parameters
    ----------
    _id : int
        The user's ID to whom we want to add/remove points
    points : int
        The amount of points to increment the field by, can be negative to remove points
    """

    # first we ensure this user has a User document in the database before
    # continuing
    get_user(_id)
    User.objects(_id=_id).update_one(inc__warn_points=points)


def inc_xp(id: int, xp) -> Tuple[int, int]:
    """Increments user xp.
    """

    get_user(id)
    User.objects(_id=id).update_one(inc__xp=xp)
    u = User.objects(_id=id).first()
    return (u.xp, u.level)


def inc_level(id: int) -> None:
    """Increments user level.
    """

    get_user(id)
    User.objects(_id=id).update_one(inc__level=1)


def get_infractions(id: int) -> Infractions:
    """Return the Document representing the infractions of a user, whose ID is given by `id`
    If the user doesn't have a Infractions document in the database, first create that.

    Parameters
    ----------
    id : int
        The user whose infractions we want to look up.

    Returns
    -------
    Infractions
        [description]
    """

    infractions = Infractions.objects(_id=id).first()
    # first we ensure this user has a Infractions document in the database before
    # continuing
    if infractions is None:
        infractions = Infractions()
        infractions._id = id
        infractions.save()
    return infractions


def add_infraction(_id: int, infraction: Infraction) -> None:
    """Infractions holds all the infractions for a particular user with id `_id` as an
    EmbeddedDocumentListField. This function appends a given infraction object to
    this list. If this user doesn't have any previous infractions, we first add
    a new Infractions document to the database.

    Parameters
    ----------
    _id : int
        ID of the user who we want to add the infraction to.
    infraction : Infraction
        The infraction we want to add to the user.
    """

    # ensure this user has a infractions document before we try to append the new
    # infraction
    get_infractions(_id)
    Infractions.objects(_id=_id).update_one(push__infractions=(infraction).to_mongo())


def set_warn_kicked(_id: int) -> None:
    """Set the `was_warn_kicked` field in the User object of the user, whose ID is given by `_id`,
    to True. (this happens when a user reaches 400+ points for the first time and is kicked).
    If the user doesn't have a User document in the database, first create that.

    Parameters
    ----------
    _id : int
        The user's ID who we want to set `was_warn_kicked` for.
    """

    # first we ensure this user has a User document in the database before
    # continuing
    get_user(_id)
    User.objects(_id=_id).update_one(set__was_warn_kicked=True)


def rundown(id: int) -> list:
    """Return the 3 most recent infractions of a user, whose ID is given by `id`
    If the user doesn't have a Infractions document in the database, first create that.

    Parameters
    ----------
    id : int
        The user whose infractions we want to look up.

    Returns
    -------
    Infractions
        [description]
    """

    infractions = Infractions.objects(_id=id).first()
    # first we ensure this user has a Infractions document in the database before
    # continuing
    if infractions is None:
        infractions = Infractions()
        infractions._id = id
        infractions.save()
        return []

    infractions = infractions.infractions
    infractions = filter(lambda x: x._type != "UNMUTE", infractions)
    infractions = sorted(infractions, key=lambda i: i['date'])
    infractions.reverse()
    return infractions[0:3]


def retrieve_birthdays(date) -> Any:
    return User.objects(birthday=date)


def transfer_profile(oldmember: int, newmember) -> Tuple[User, int]:
    u = get_user(oldmember)
    u._id = newmember
    u.save()

    u2 = get_user(oldmember)
    u2.xp = 0
    u2.level = 0
    u2.save()

    infractions = get_infractions(oldmember)
    infractions._id = newmember
    infractions.save()

    infractions2 = get_infractions(oldmember)
    infractions2.infractions = []
    infractions2.save()

    return u, len(infractions.infractions)


def fetch_raids() -> Dict[str, Any]:
    values = {}
    values["Join spam"] = Infractions.objects(
        infractions__reason__contains="Join spam detected").count()
    values["Join spam over time"] = Infractions.objects(
        infractions__reason__contains="Join spam over time detected").count()
    values["Raid phrase"] = Infractions.objects(
        infractions__reason__contains="Raid phrase detected").count()
    values["Ping spam"] = Infractions.objects(
        infractions__reason__contains="Ping spam").count()
    values["Message spam"] = Infractions.objects(
        infractions__reason__contains="Message spam").count()

    return values


def fetch_infractions_by_mod(_id) -> dict:
    values = {}
    infractions = Infractions.objects(infractions__mod_id=str(_id))
    values["total"] = 0
    infractions = list(infractions.all())
    final_infractions = []
    for target in infractions:
        for infraction in target.infractions:
            if str(infraction.mod_id) == str(_id):
                final_infractions.append(infraction)
                values["total"] += 1

    def get_infraction_reason(reason: str) -> str:
        string = reason.lower()
        return ''.join(e for e in string if e.isalnum() or e == " ").strip()

    infraction_reasons = [
        get_infraction_reason(
            infraction.reason) for infraction in final_infractions if get_infraction_reason(
            infraction.reason) != "temporary mute expired"]
    values["counts"] = sorted(
        Counter(infraction_reasons).items(), key=lambda item: item[1])
    values["counts"].reverse()
    return values


def fetch_infractions_by_keyword(keyword: str) -> dict:
    values = {}
    infractions = Infractions.objects(infractions__reason__contains=keyword)
    infractions = list(infractions.all())
    values["total"] = 0
    final_infractions = []

    for target in infractions:
        for infraction in target.infractions:
            if keyword.lower() in infraction.reason:
                values["total"] += 1
                final_infractions.append(infraction)

    infraction_mods = [infraction.mod_tag for infraction in final_infractions]
    values["counts"] = sorted(
        Counter(infraction_mods).items(), key=lambda item: item[1])
    values["counts"].reverse()
    return values


def set_sticky_roles(_id: int, roles) -> None:
    get_user(_id)
    User.objects(_id=_id).update_one(set__sticky_roles=roles)
