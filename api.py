from requests import post, get
import timeit
import os
import ast
import config
import json
import time
#import database as db
import itertools
from datetime import datetime, timezone
from dateutil import parser



tokens = itertools.cycle(config.API_KEYS)

API_KEY = config.API_KEY

#key = {"api_key": API_KEY}

def get_all(smmoid):
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    key =  {"api_key": next(tokens)}
    
    ret = post(url, data=key, timeout=5)

    if ret.ok:
        content = ret.content
        x = content.decode("UTF-8")
        info = json.loads(x)
        #print(info)
        return info

    elif ret.status_code == 429:
        print("Too many requests. Sleeping...")
        
        time.sleep(15)
        return pleb_status(smmoid)
    else:
        print("Failed\n")
        return None



def equipment(smmoid):
    key =  {"api_key": next(tokens)}
    
    url = "https://api.simple-mmo.com/v1/player/equipment/" + str(smmoid)
    
    ret = post(url, data=key,timeout=None)
    if ret.ok:
        try:
            content = ret.content
            x = content.decode("UTF-8")
            info = json.loads(x)
            print(info)
            safemode = info["safeMode"]
            if safemode == 1:
                return True
            return False
        except Exception as e:
            if(info["error"] == "user not found"):
                db.remove_user(smmoid)
                print("Removed user: " + str(smmoid))
            
    elif ret.status_code == 429:
        print("Too many requests. Sleeping...")
        
        time.sleep(30)
        return pleb_status(smmoid)
    else:
        print(f'Return status: {ret.status_code} for ID: {smmoid}')
        print(f'{ret.reason}')
        print("Pleb Status Request Failed\n")
        return None






def safemode_status(smmoid):
    key =  {"api_key": next(tokens)}
    
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    
    ret = post(url, data=key,timeout=None)
    if ret.ok:
        try:
            content = ret.content
            x = content.decode("UTF-8")
            info = json.loads(x)
            safemode = info["safeMode"]
            if safemode == 1:
                return True
            return False
        except Exception as e:
            if(info["error"] == "user not found"):
                db.remove_user(smmoid)
                print("Removed user: " + str(smmoid))
            
    elif ret.status_code == 429:
        print("Too many requests. Sleeping...")
        
        time.sleep(30)
        return pleb_status(smmoid)
    else:
        print(f'Return status: {ret.status_code} for ID: {smmoid}')
        print(f'{ret.reason}')
        print("Pleb Status Request Failed\n")
        return None

def get_skills(smmoid):
    url = "https://api.simple-mmo.com/v1/player/skills/"+str(smmoid)
    key = {"api_key": next(tokens)}
    ret = post(url,data=key,timeout=10)

    if ret.ok:
        content = ret.content
        x = content.decode("UTF-8")
        info = json.loads(x)
        return info
    else:
        print("Failed")
        return None


def get_motto(smmoid):
    key =  {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    
    ret = post(url, data=key, timeout=None)

    if ret.ok:
        content = ret.content
        
        x = content.decode("UTF-8")
        info = json.loads(x)
        motto = info["motto"]
        return motto
    else:
        print("Motto Request Failed\n")
        return None

def get_token():
    pass




def pleb_status(smmoid):
    key =  {"api_key": next(tokens)}
    
    url = "https://api.simple-mmo.com/v1/player/info/" + str(smmoid)
    
    ret = post(url, data=key,timeout=None)
    if ret.ok:
        try:
            content = ret.content
            x = content.decode("UTF-8")
            info = json.loads(x)
            pleb = info["membership"]
            if pleb == 1:
                return True
            return False
        except Exception as e:
            if(info["error"] == "user not found"):
                db.remove_user(smmoid)
                print("Removed user: " + str(smmoid))
            
    elif ret.status_code == 429:
        print("Too many requests. Sleeping...")
        
        time.sleep(30)
        return pleb_status(smmoid)
    else:
        print(f'Return status: {ret.status_code} for ID: {smmoid}')
        print(f'{ret.reason}')
        print("Pleb Status Request Failed\n")
        return None



def guild_info(guildid):
    key =  {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/guilds/info/" + str(guildid)

    ret = post(url, data=key, timeout=5)
    if ret.ok:
        content = ret.content
        print(content)
        return content

    else:
        print("Guild Request failed")
        return None

def guild_members(guildid):
    key =  {"api_key": next(tokens)}
    url = "https://api.simple-mmo.com/v1/guilds/members/" + str(guildid)

    ret = post(url, data=key, timeout=5)
    if ret.ok:
        content = ret.content
        x = content.decode("UTF-8")
        members = json.loads(x)
        return members

    elif ret.status_code == 429:
        print("Too many requests. Sleeping...")
        print(ret.headers)
        
        time.sleep(30)
        return guild_members(guildid)

    else:
        print("Guild Members failed")
        return None

def item_info(itemid):
    key =  {"api_key": next(tokens)}
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
def get_guild_wars(guildid,status):
    key =  {"api_key": next(tokens)}
    url = f"https://api.simple-mmo.com/v1/guilds/wars/{guildid}/{status}" 
    
    ret = post(url, data=key, timeout=None)

    if ret.ok:
        content = ret.content
        
        x = content.decode("UTF-8")
        info = json.loads(x)

        info.sort(reverse=True,key=lambda x:x['guild_1']['kills'])
        #return temp
        return info
    else:
        print("Guild War Request Failed\n")
        return None

def diamond_market():
    key = {"api_key": next(tokens)}
    url = f"https://api.simple-mmo.com/v1/diamond-market"

    ret = post(url, data=key, timeout=None)

    if ret.ok:
        content = ret.content
        
        x = content.decode("UTF-8")
        info = json.loads(x)
       
        return info
    else:
        print("Diamond Market Request Failed\n")
        return None

    
if __name__ == "__main__":
    #profile = get_all(385801)
    #print(profile)
    #print(guild_members(828)[0])
    # creation = profile["creation_date"]
    # print(creation)
    # now = datetime.now(timezone.utc)
    # creation = parser.parse(creation)
    # difference = now - creation
    # print(difference.days)

    print(get_guild_wars(455,1))
    
    #print([x["user_id"] for x in guild_members(828)])

    #print(get_skills(385801))
    
    # for i in range(2000):
    #     if i % 10 == 0:
    #         print(pleb_status(385801),i)

    #equipment(385801)
    #print(diamond_market()[0])