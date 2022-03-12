from requests import post, get
import timeit
import os
import ast
import config
import json
import time
import database as db
import itertools
from datetime import datetime, timezone
from dateutil import parser
import aiohttp
import asyncio


tokens = itertools.cycle(config.API_KEYS)

API_KEY = config.API_KEY

#key = {"api_key": API_KEY}


async def get_all(smmoid):
    key = {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:
            if ret.status == 200:
                content = ret.content
                x = await content.read()
                info = json.loads(x)

                return info

            elif ret.status == 429:

                await asyncio.sleep(5)
                return await get_all(smmoid)
            else:
                print("Failed\n")
                return None


async def equipment(smmoid):
    key = {"api_key": next(tokens)}

    url = "https://api.simple-mmo.com/v1/player/equipment/" + str(smmoid)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:

            if ret.status == 200:
                try:
                    content = ret.content
                    x = await content.read()
                    info = json.loads(x)

                    safemode = info["safeMode"]
                    if safemode == 1:
                        return True
                    return False
                except Exception:
                    if(info["error"] == "user not found"):
                        db.remove_user(smmoid)
                        print("Removed user: " + str(smmoid))

            elif ret.status_code == 429:

                await asyncio.sleep(30)
                return equipment(smmoid)
            else:
                print(f'Return status: {ret.status_code} for ID: {smmoid}')
                print(f'{ret.reason}')
                print("Pleb Status Request Failed\n")
                return None


async def safemode_status(smmoid):
    key = {"api_key": next(tokens)}

    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:
            if ret.status == 200:
                try:
                    content = ret.content
                    x = await content.read()
                    info = json.loads(x)
                    safemode = info["safeMode"]
                    if safemode == 1:
                        return True
                    return False
                except Exception as e:
                    if(info["error"] == "user not found"):
                        db.remove_user(smmoid)
                        print("Removed user: " + str(smmoid))

            elif ret.status == 429:

                await asyncio.sleep(10)
                return safemode_status(smmoid)
            else:
                print(f'Return status: {ret.status_code} for ID: {smmoid}')
                print(f'{ret.reason}')
                print("Pleb Status Request Failed\n")
                return None


async def get_skills(smmoid):
    url = "https://api.simple-mmo.com/v1/player/skills/"+str(smmoid)
    key = {"api_key": next(tokens)}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:
            if ret.status == 200:
                content = ret.content
                x = await content.read()
                info = json.loads(x)
                return info
            elif ret.status == 429:

                await asyncio.sleep(10)
                return get_skills(smmoid)
            else:
                print("Failed")
                return None


async def get_motto(smmoid):

    key = {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:

            if ret.status == 200:
                content = ret.content

                x = await content.read()
                info = json.loads(x)
                motto = info["motto"]
                return motto
            elif ret.status == 429:

                await asyncio.sleep(10)
                return await get_motto(smmoid)
            else:
                print("Motto Request Failed\n")
                return None


def get_token():
    pass


async def pleb_status(smmoid):

    key = {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:

            if ret.status == 200:
                try:
                    content = ret.content
                    x = await content.read()
                    info = json.loads(x)

                    pleb = info["membership"]
                    if pleb == 1:
                        return True
                    return False
                except Exception as e:

                    if(info["error"] == "user not found"):
                        db.remove_user(smmoid)

                        return

            elif ret.status == 429:

                await asyncio.sleep(10)
                return await pleb_status(smmoid)
            else:
                print(f'Return status: {ret.status} for ID: {smmoid}')
                print(f'{ret.reason}')
                print("Pleb Status Request Failed\n")
                return None

    # ret = post(url, data=key,timeout=None)
    # if ret.ok:
    #     try:
    #         content = ret.content
    #         x = content.decode("UTF-8")
    #         info = json.loads(x)
    #         pleb = info["membership"]
    #         if pleb == 1:
    #             return True
    #         return False
    #     except Exception as e:
    #         if(info["error"] == "user not found"):
    #             db.remove_user(smmoid)
    #             print("Removed user: " + str(smmoid))

    # elif ret.status_code == 429:
    #     print("Too many requests. Sleeping...")

    #     time.sleep(30)
    #     return pleb_status(smmoid)
    # else:
    #     print(f'Return status: {ret.status_code} for ID: {smmoid}')
    #     print(f'{ret.reason}')
    #     print("Pleb Status Request Failed\n")
    #     return None


async def guild_info(guildid):

    key = {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/guilds/info/" + str(guildid)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:

            if ret.status == 200:
                content = ret.content
                x = await content.read()
                info = json.loads(x)

                return info
            elif ret.status == 429:

                await asyncio.sleep(10)
                return await guild_info(guildid)

            else:
                print("Guild Request failed")
                return None


async def guild_members(guildid):
    key = {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/guilds/members/" + str(guildid)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:

            if ret.status == 200:
                content = ret.content
                x = await content.read()
                members = json.loads(x)

                try:
                    members.sort(reverse=True, key=lambda x: x['level'])
                except:
                    pass
                return members

            elif ret.status == 429:

                await asyncio.sleep(10)
                return await guild_members(guildid)

            else:
                print("Guild Members failed")
                return None


def item_info(itemid):
    key = {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/item/info/" + str(itemid)
    ret = post(url, data=key)
    if ret.ok:
        print(ret.content)
    else:
        print("Request Failed")
        return None

# @status:
#   1 : Ongoing
#   2: Ended
#   3: Hold
#   4: All


async def get_guild_wars(guildid, status):
    key = {"api_key": next(tokens)}
    url = f"https://api.simple-mmo.com/v1/guilds/wars/{guildid}/{status}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:
            if ret.status == 200:
                content = ret.content

                x = await content.read()
                info = json.loads(x)

                info.sort(reverse=True, key=lambda x: (
                    x['guild_1']['kills'] + x['guild_2']['kills']))
                return info

            elif ret.status == 429:

                await asyncio.sleep(10)
                return await get_guild_wars(guildid, status)
            else:
                print("Guild War Request Failed\n")
                return None


async def diamond_market():
    key = {"api_key": next(tokens)}
    url = f"https://api.simple-mmo.com/v1/diamond-market"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=key) as ret:

            if ret.status == 200:
                content = ret.content

                x = await content.read()
                info = json.loads(x)

                return info
            elif ret.status == 429:

                await asyncio.sleep(10)
                return await diamond_market()
            else:
                print("Diamond Market Request Failed\n")
                return None


if __name__ == "__main__":
    # profile = get_all(385801)
    # print(profile)
    # #print(guild_members(828)[0])
    # creation = profile["creation_date"]
    # print(creation)
    # now = datetime.now(timezone.utc)
    # creation = parser.parse(creation)
    # difference = now - creation
    # print(difference.days)

    # print(get_guild_wars(408,1))

    #print([x["user_id"] for x in guild_members(828)])

    # print(get_skills(385801))

    # for i in range(2000):
    #     if i % 10 == 0:
    #         print(pleb_status(385801),i)

    # equipment(385801)
    # print(diamond_market()[0])
    # print(guild_members(408)[0])
    # print(guild_info(408))
    # status = await pleb_status(385801)
    # await get_all(385801)
    pass
