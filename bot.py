import os
from discord.ext import commands, tasks
import discord
from discord import Intents, errors,Embed
from discord.ext.commands.core import check
import database as db
import random   
import string
import api
from util import checks,log
import asyncio
from datetime import datetime

import config


import logging

# Logging setup?
logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


dev = False


TOKEN = config.TOKEN
DEV_TOKEN = config.DEV_TOKEN

if TOKEN is None or DEV_TOKEN is None:
    print("Bot Token not found in .env folder")
    quit()

if dev is True:
    TOKEN = DEV_TOKEN

# Set discord intents
intents = Intents.all()
print(intents.value)
bot = commands.Bot(command_prefix='&', intents=intents,status="Contact dyl#8008 with questions") 

###########################
#     Local Variables     #

smmo_server = 444067492013408266
test_server = 538144211866746883
fly_server = 710258284661178418

plebTask = None
guildTask = None
flyTask = None


fly = (408,455,541,482)
dyl = 332314562575597579


server = smmo_server # Change this to which ever server the bot is mainly in
bot.server = server

for f in os.listdir('./cogs'):
    if f.endswith('.py'):
        bot.load_extension(f'cogs.{f[:-3]}')

@bot.event
async def on_ready():
    global plebTask
    global guildTask
    print(f'{bot.user.name} has connected to Discord')
    plebTask = update_all_plebs.start()
    guildTask = update_all_guilds.start()
    print(f"Tasks have been started")
    

@bot.command(hidden=True)
@checks.is_owner()
async def test(ctx,arg):
    return arg


@checks.is_owner()
@bot.command(aliases=["kill"],hidden=True)
async def restart(ctx):
    await ctx.send("Senpai, why you kill me :3")

    await bot.close()


@bot.command(hidden=True)
@checks.is_owner()
async def flycheck(ctx=None):
    print("Fly Check is starting")
    guild = bot.get_guild(fly)
    fly_roles = [bot.get_role(710315282920636506),
                bot.get_role(722110578516164670)]

    if ctx is not None:
        await ctx.send("Fly Check is starting")

    flymembers = db.all_fly()

    for member in flymembers:
        discid = int(member[0])
        smmoid = member[1]
        guildid = member[2]
        


        # get guild from profile (get_all())
        profile = api.get_all(smmoid)
        try:
            current_guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("You are not in a guild")
            return
        
        # if user has left the fly guild
        if current_guildid not in fly:
            user = bot.get_member(discid)

            if user is None:
                continue

            user.remove_roles(fly_roles,reason = "Automatic Removal")
            db.fly_remove(discid)
        
        else:
            if current_guildid != guildid:
                db.fly_update(discid,smmoid,current_guildid)



        


@bot.command(hidden=True)
@checks.is_owner()
async def plebcheck(ctx=None):
    log.log(bot,"Pleb Check Started","")
    if(db.server_added(server)): # server has been initialized
        pleb_role = db.pleb_id(server)
    else:
        print("Server has not been added to db")
        return
    

    if ctx is not None:
        await ctx.send("Pleb check starting...")

    plebs = db.get_all_plebs()
    guild = bot.get_guild(int(server))
    role = guild.get_role(int(pleb_role))
    count = 0
    if ctx is not None:
        await ctx.send(f"There are {len(plebs)} people to check.")
    in_server = 0
    for pleb in plebs:

        count +=1
        if ctx is not None:
            if count % 100 == 0:
                await ctx.send(f"{count} members checked")
        
        discid = int(pleb[0])
        smmoid = int(pleb[1])
        
        
        user = guild.get_member(discid) # get user object
        if user is None:
            #print(f'{discid} is not found is the server')
            in_server += 1
            continue
        
        # If user is muted, do not give them the role
        if user._roles.has(751808682169466962):
            continue

        isPleb = api.pleb_status(smmoid)

        if isPleb is None:
            print("THE API IS STUPID")

        elif isPleb is True:
            db.update_status(smmoid, True) # they are a pleb
            if not user._roles.has(role):
                await user.add_roles(role) # give user pleb role
            #print(f'{user} with uid: {smmoid} has pleb!')

        elif isPleb is False: # user is not pleb
            db.update_status(smmoid, False) # not a pleb
            if user._roles.has(role):
                await user.remove_roles(role) # remove pleb role
            #print(f'{user} lost pleb!')

    if ctx is not None:
        await ctx.send(f"Pleb check finished! {in_server} linked members not in this server")

    print("Pleb check finished")



@bot.command(hidden=True)
@checks.is_owner()
async def guildcheck(ctx=None):
    log.log(bot,"Guild Check Started","")

    if(ctx is not None):
        await ctx.send("Guild check starting...")

    guild = bot.get_guild(int(server))
    leaderrole = guild.get_role(int(db.leader_id(server)))
    ambassadorrole = guild.get_role(int(db.ambassador_role(server)))
    

    ambassadors = db.all_ambassadors()
    leaders = db.all_leaders()

    # discid, smmoid, guildid
    for leader in leaders:
        await asyncio.sleep(1)
        discid = int(leader[0])
        lsmmoid = int(leader[1])
        guildid = int(leader[2])

        # get any guild ambassadors in that guild
        guildambs = [x for x in ambassadors if x[2] == guildid]


        # check leader in guild
        members = api.guild_members(guildid)

        # get leader from member list
        try:
            gLeader = [x for x in members if x["position"] == "Leader"]
        except Exception as e:
            # if the guild has been disbanded, remove leader + any guild ambassadors
            if(members["error"] == "guild not found"):
                user = guild.get_member(discid)
                if user is not None:
                    print(f"{user.name} is not a leader because guild {guildid} has been deleted.")
                    # if not leader, remove role and update db
                    await user.remove_roles(leaderrole)
                db.guild_leader_update(str(discid),False,0,0)


                if len(guildambs) > 0:
                    for amb in guildambs:
                        user = guild.get_member(int(amb[0]))
                        if user is not None:
                            print(f"{user.name} is not an ambassador because guild {guildid} has been deleted.")
                            await user.remove_roles(ambassadorrole)
                        db.guild_ambassador_update(amb[0], False, 0)
                continue


        # if current leader is not one w/ role, remove leader + ambassadors
        if int(gLeader[0]["user_id"]) != lsmmoid:
            user = guild.get_member(discid)
            if user is not None:
                print(f"{user.name} is not a leader")
                # if not leader, remove role and update db
                await user.remove_roles(leaderrole)
            db.guild_leader_update(str(discid),False,0,0)


            if len(guildambs) > 0:
                for amb in guildambs:
                    user = guild.get_member(int(amb[0]))
                    if user is not None:
                        print(f"{user.name} is not an ambassador")
                        await user.remove_roles(ambassadorrole)
                    db.guild_ambassador_update(amb[0], False, 0)
            continue
        
        # if gleader is person w/ role, check ambassadors to see if they're in guild
        else:
            if len(guildambs) > 0:
                for amb in guildambs:
                    # if ambassador is not in members list
                    if len([x for x in members if int(x["user_id"]) == int(amb[1])]) == 0:
                        user = guild.get_member(int(amb[0]))
                        if user is not None:
                            print(f"{user.name} is not an ambassador")

                            await user.remove_roles(ambassadorrole)
                        db.guild_ambassador_update(amb[0], False, 0)


    if(ctx is not None):
        await ctx.send("Guild Check has finished.")
    print("Guild Check has finished")


@tasks.loop(hours=6)
async def update_fly():
    #await flycheck()
    return


@tasks.loop(hours=3)
async def update_all_plebs():
    await plebcheck()
    return

@tasks.loop(hours=4)
async def update_all_guilds():
    await guildcheck()
    return





bot.run(TOKEN)
