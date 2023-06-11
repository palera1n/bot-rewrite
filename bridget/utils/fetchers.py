import json
import urllib
import aiohttp

from aiocache import cached
from typing import Union, Optional

client_session = None


@cached(ttl=3600)
async def get_ios_cfw() -> Optional[dict]:
    """Gets all apps on ios.cfw.guide

    Returns
    -------
    dict
        "ios, jailbreaks, devices"
    """

    async with client_session.get("https://api.appledb.dev/main.json") as resp:
        if resp.status == 200:
            data = await resp.json()
            return data


@cached(ttl=3600)
async def get_ipsw_firmware_info(version: str) -> Union[dict, list]:
    """Gets all apps on ios.cfw.guide

    Returns
    -------
    dict
        "ios, jailbreaks, devices"
    """

    async with client_session.get(f"https://api.ipsw.me/v4/ipsw/{version}") as resp:
        if resp.status == 200:
            data = await resp.json()
            return data

        return []


@cached(ttl=600)
async def get_dstatus_components() -> Optional[dict]:
    async with client_session.get("https://discordstatus.com/api/v2/components.json") as resp:
        if resp.status == 200:
            components = await resp.json()
            return components


@cached(ttl=600)
async def get_dstatus_incidents() -> Optional[dict]:
    async with client_session.get("https://discordstatus.com/api/v2/incidents.json") as resp:
        if resp.status == 200:
            incidents = await resp.json()
            return incidents


async def fetch_remote_json(url: str) -> Optional[dict]:
    """Get a JSON file from a URL

    Parameters
    ----------
    url : str
        "URL of the JSON file"

    Returns
    -------
    json
        "Remote JSON file"

    """

    async with client_session.get(url) as resp:
        if resp.status == 200:
            text = await resp.text()
            try:
                if text.startswith('{"bug_type":'):
                    return json.loads(text.split("\n", 1)[1])
                else:
                    return json.loads(text)
            except:
                return None
        else:
            return None


async def fetch_remote_file(url: str) -> Optional[str]:
    """Get a file from a URL

    Parameters
    ----------
    url : str
        "URL of the file"

    Returns
    -------
    json
        "Remote file"

    """

    async with client_session.get(url) as resp:
        if resp.status == 200:
            return await resp.text()
        else:
            return None


async def canister_search_package(query: str) -> Optional[list]:
    """Search for a tweak in Canister's catalogue

    Parameters
    ----------
    query : str
        "Query to search for"

    Returns
    -------
    list
        "List of packages that Canister found matching the query"

    """

    async with client_session.get(f'https://api.canister.me/v2/jailbreak/package/search?q={urllib.parse.quote(query)}') as resp:
        if resp.status == 200:
            response = json.loads(await resp.text())
            return response.get('data')
        else:
            return None


async def canister_search_repo(query: str) -> Optional[list]:
    """Search for a repo in Canister's catalogue

    Parameters
    ----------
    query : str
        "Query to search for"

    Returns
    -------
    list
        "List of repos that Canister found matching the query"

    """

    async with client_session.get(f'https://api.canister.me/v2/jailbreak/repository/search?q={urllib.parse.quote(query)}') as resp:
        if resp.status == 200:
            response = json.loads(await resp.text())
            return response.get('data')
        else:
            return None


@cached(ttl=3600)
async def canister_fetch_repos() -> Optional[list]:
    async with client_session.get('https://api.canister.me/v2/jailbreak/repository/ranking?rank=*') as resp:
        if resp.status == 200:
            response = await resp.json(content_type=None)
            return response.get("data")

        return None


@cached(ttl=3600)
async def fetch_scam_urls() -> Optional[dict]:
    async with client_session.get("https://raw.githubusercontent.com/SlimShadyIAm/Anti-Scam-Json-List/main/antiscam.json") as resp:
        if resp.status == 200:
            obj = json.loads(await resp.text())
            return obj


async def init_client_session() -> None:
    global client_session
    client_session = aiohttp.ClientSession()
