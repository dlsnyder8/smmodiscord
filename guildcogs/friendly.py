import discord
from discord.embeds import Embed
from discord.ext import commands, tasks
from discord.ext.commands.core import guild_only
from smmolib import checks, log, api
from smmolib import database as db
from discord.ext.commands.cooldowns import BucketType
import logging
from smmolib.log import flylog, log, flylog2, flylog3
import traceback
from datetime import datetime, timezone
from dateutil import parser
from dpymenus import Page, ButtonMenu
import csv
import os


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# fly guilds
fly = (408, 455, 541, 482)

""" Fly role order:
    0-2: Thicc
    3-6: Stepper
    7-9: Gladiator
    10-12: Monster
    13-15: Quester
    16-18: Forager
    19: Main role
    20: NSF Role
    21-23: Tasker
    24-25: Slayer
    26-28: Trader
    29-31: Celebrity
    32: Veteran
"""
fly_roles = [
    # Thicc (Levels)
    727719624434778124, 727722577908334662, 727722769785028672,
    # Stepper
    710290715787264041, 720049949865279559, 727947354929365003, 829700204357877812,
    # Gladiator (NPC)
    724649998985461841, 724650153218277457, 752699779888316417,
    # Monster (PVP)
    710293875289489458, 720052795679703138, 752703370510336080,
    # Quester
    752700240213311580, 752700554672865290, 752700633920045139,
    # Forager
    767163012132896808, 829700288976781312, 829700338893979718,
    # Main Fly Role
    710315282920636506,
    # NSF Role
    722110578516164670,
    # Tasker
    752706107985625139, 752706496315261068, 763043799869030400,
    # Slayer
    752702198303031376, 752702447662923777,
    # Trader
    710277160857763860, 829692366092238858, 720048172399067200,
    # Celebrity
    710307235124871189, 720062633281192008, 752701722719289398,
    # Veteran
    752705054351556658

]

acquaintance = 710307524632641597
traveler = 710318244401119304

dyl = 332314562575597579


class Friendly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flycheck.start()

    @checks.in_fly()
    @commands.group(aliases=['fly', 'f'], hidden=True)
    async def friendly(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @friendly.command()
    @checks.is_owner()
    async def nofly(self, ctx):
        await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[19]))

    @commands.command()
    @checks.in_fly_guild()
    async def colors(self, ctx):
        embed = Embed(title="So you want a colored role?", description=f"There are 4 ways to not be a stinky color:\n- Join the guild and have access to 80+ roles\n- Boost the server\n- Post artwork in <#734892163502178434> to get the <@&733433793871872051> role\n- Win an event")
        await ctx.send(embed=embed)

    @checks.in_fly()
    @friendly.command(aliases=['fc', 'friendcheck'])
    @checks.no_bot_channel()
    @checks.in_fly_guild()
    async def friend_check(self, ctx):

        member = ctx.author

        weighted_fly_roles = {
            # Thicc (Levels)
            727719624434778124: 1, 727722577908334662: 2, 727722769785028672: 3,
            # Stepper
            710290715787264041: 1, 720049949865279559: 2, 727947354929365003: 3, 829700204357877812: 4,
            # Gladiator (NPC)
            724649998985461841: 1, 724650153218277457: 2, 752699779888316417: 3,
            # Monster (PVP)
            710293875289489458: 1, 720052795679703138: 2, 752703370510336080: 3,
            # Quester
            752700240213311580: 1, 752700554672865290: 2, 752700633920045139: 3,
            # Forager
            767163012132896808: 1, 829700288976781312: 2, 829700338893979718: 3,
            # Tasker
            752706107985625139: 1, 752706496315261068: 2, 763043799869030400: 3,
            # Slayer
            752702198303031376: 1, 752702447662923777: 2,
            # Decorated
            731018776648089670: 1, 731019364068753449: 2,
            # Trader
            710277160857763860: 1, 829692366092238858: 2, 720048172399067200: 3,
            # Celebrity
            710307235124871189: 1, 720062633281192008: 2, 752701722719289398: 3,
            # Veteran
            752705054351556658: 1,
            # Suggester
            720047404996624487: 1,
            # Storyteller
            774361923218309130: 1,
            # Looter
            720049700782342215: 1,
            # Collector
            710290631855177739: 1, 720050166396354671: 2, 752699424735494175: 3,
            # Tycoon
            723955238385746030: 1, 723955584038076486: 2,
            # Thief
            734573085637869651: 1, 734573239249928222: 2,
            # Sniper
            713281314882846730: 1, 720053096855896084: 2,
            # Artist
            733433793871872051: 1, 748786772833730580: 2,
            # Diamond
            717579223174348900: 1, 720061797838618660: 2,
            # Hero
            710317545340797068: 1, 720049289187033188: 2,
            # Meme'd
            710325364756447306: 1, 720053250669281301: 2,
            # Hunter
            720052696757043294: 1, 774354836614545419: 2,
            # Enforcer
            719173436856991804: 1, 720052932971593800: 2,
            # Contributor
            868508713525334066: 1, 720683761959960627: 2, 720684106551132263: 3,
            # Booster
            716498456453316672: 1,
            # BF/CF/BFF
            756119028543651951: 1, 894229709192314920: 2, 723506672944807946: 3,
            # Charity Club
            713069407261425724: 1
        }

        event_roles = {
            731438976572850239: 1, 729562423912038462: 1, 784451589922226176: 1, 749945230907670560: 1
        }

        invite_roles = {710325364756447306: 1, 720053250669281301: 2, 748786772833730580: 2, 720048172399067200: 3,
                        774354836614545419: 2, 720052932971593800: 2, 720683761959960627: 2, 720684106551132263: 3}

        async with ctx.typing():

            roles = member.roles

            roleids = [r.id for r in roles]
            print(roleids)
            output = set(roleids).intersection(weighted_fly_roles)
            events = set(roleids).intersection(event_roles)
            inviteonly = set(roleids).intersection(invite_roles)
            total = 0
            invite = False
            chatter = False
            for x in output:
                total += weighted_fly_roles[x]
            if len(events) >= 1:
                total += 1
            if len(inviteonly) >= 1:
                invite = True
            # Check for chatter role
            if member._roles.has(908072543708135455):
                chatter = True

            embed = Embed(title="Friendship Eligibility")

            if total < 15:
                embed.description = f"Try getting some more roles! You only have {total} roles."

            elif total < 30:
                if not chatter:
                    embed.description = f"You have {total} roles, but you still need to hit level 15 on MEE6 to be eligible for Close Friend. You can check your current rank by doing `!rank` in <#710718330516013147>"
                else:
                    embed.description = f"You are eligible for Close Friend with {total} roles :)\nPlease run this command again in <#719944258156494998> to apply for the role"

            elif total < 45:
                if not chatter:
                    embed.description = f"You have {total} roles, but you still need to hit level 15 on MEE6 to be eligible for Best Friend. You can check your current rank by doing `!rank` in <#710718330516013147>"
                else:
                    embed.description = f"You are eligible for Best Friend!! Nice job getting {total} roles.\nPlease run this command again in <#719944258156494998> to apply for the role"
            else:
                if invite and chatter:
                    embed.description = f"A master role gatherer has joined the ranks of BFF. Congrats on {total} roles!\nPlease run this command again in <#719944258156494998> to apply for the role"
                elif not invite and not chatter:
                    embed. description = f"You have enough roles to be eligible for BFF with {total} roles, however you need to get an invite only role still and you need to reach level 15 on MEE6 to be eligible for BFF. You can check your current rank by doing `!rank` in <#710718330516013147>"
                elif not chatter:
                    embed.description = f"You have {total} roles, but you still need to hit level 15 on MEE6 to be eligible for BFF. You can check your current rank by doing `!rank` in <#710718330516013147>"
                elif not invite:
                    embed. description = f"You have enough roles to be eligible for BFF with {total} roles, however you need to get an invite only role still."

            await ctx.send(embed=embed)

            return

    @checks.is_owner()
    @friendly.command(aliases=["stats"])
    async def guildstats(self, ctx):
        guild = self.bot.get_guild(710258284661178418)
        role = guild.get_role(710315282920636506)
        members = role.members
        async with ctx.typing():
            with open('friendly.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['smmoid', 'name', 'npc_kills', 'user_kills', 'quests_complete', 'level',
                                'tasks', 'boss_kills', 'market_trades', 'reputation', 'bounties', 'dailies', 'chests'])
                for member in members:
                    smmoid = await db.get_smmoid(member.id)
                    x = await api.get_all(smmoid)

                    data = [smmoid, x['name'], x['npc_kills'], x['user_kills'], x['quests_complete'], x['level'], x['tasks_completed'],
                            x['boss_kills'], x['market_trades'], x['reputation'], x['bounties_completed'], x['dailies_unlocked'], x['chests_opened']]
                    writer.writerow(data)
            file_csv = open('friendly.csv')
            await ctx.send("Here are the guild stats", file=file_csv)
            os.remove('friendly.csv')

    @checks.is_owner()
    @friendly.command()
    async def remove(self, ctx, member: discord.Member):
        try:
            await db.fly_remove(member.id)
            await ctx.send("Success!")
        except Exception as e:
            await ctx.send(e)

    @checks.is_verified()
    @commands.command()
    @guild_only()
    @commands.cooldown(1, 60, BucketType.user)
    async def join(self, ctx):
        if ctx.author._roles.has(fly_roles[19]):

            await ctx.send("You've already been granted the Friendly role :)")
            return

        smmoid = await db.get_smmoid(ctx.author.id)

        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("You are not in a guild")
            return

        # if user is in a fly guild....
        if guildid in fly or ctx.author.id == dyl:

            roles_given = ""
            try:
                ingamename = profile["name"]
            except Exception as e:
                await ctx.send(e)

            # add fly role
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[19]))
            await ctx.author.add_roles(ctx.guild.get_role(traveler))
            await ctx.author.remove_roles(ctx.guild.get_role(acquaintance))
            await ctx.send(f"Welcome to Friendly :)\nYou can run `{ctx.prefix}fly eligibility` (`{ctx.prefix}f e` for short) to check your eligibility for specific roles (more info in <#710305444194680893>)")
            roles_given += f"<@&{fly_roles[19]}>"
            # if user is in NSF
            if guildid == 541:
                nsf_role = ctx.guild.get_role(783930500732551219)
                await ctx.author.add_roles(nsf_role)
                roles_given += f" ,<@&783930500732551219>"

            await flylog(self.bot, f"{ingamename} has joined Fly", f"**Roles given to** {ctx.author.mention}\n{roles_given}", ctx.author.id)
            await self.bot.get_channel(934284308112375808).send(embed=Embed(title="Beginning of year stats", description=f'{profile}'))
            channel = self.bot.get_channel(728355657283141735)
            if ctx.author.id != dyl:
                await channel.send(f"Welcome {ctx.author.mention} to the Friendliest guild in SimpleMMO!")

            await ctx.send(f"{self.bot.get_user(581061608357363712).mention}\n ;adminlink {ctx.author.id} {smmoid}")

        else:
            await ctx.send("You are not in Fly. Try contacting a Big Friend if you believe this is a mistake")
            return

    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.is_verified()
    @friendly.command(aliases=['e'])
    async def eligibility(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)
        skills = await api.get_skills(smmoid)

        embed = Embed(title=f"Role eligibility for {ctx.author.display_name}")
        string = ""

        # Thicc (Levels)
        level = profile["level"]
        if level >= 1000 and level < 5000:
            string += f"**Thicc:** <@&{fly_roles[0]}>\n"
        elif level >= 5000 and level < 10000:
            string += f"**Thicc:** <@&{fly_roles[1]}>\n"
        elif level >= 10000:
            string += f"**Thicc:** <@&{fly_roles[2]}>\n"
        else:
            string += f"**Thicc:** Not Eligible\n"

        # Stepper
        steps = profile["steps"]
        if steps >= 7500 and steps < 50000:
            string += f"**Stepper:** <@&{fly_roles[3]}>\n"

        elif steps >= 50000 and steps < 100000:
            string += f"**Stepper:** <@&{fly_roles[4]}>\n"
        elif steps >= 100000 and steps < 1000000:
            string += f"**Stepper:** <@&{fly_roles[5]}>\n"
        elif steps >= 1000000:
            string += f"**Stepper:** <@&{fly_roles[6]}>\n"
        else:
            string += f"**Stepper:** Not Eligible\n"

        # Gladiator (NPC)
        npc_kills = profile["npc_kills"]
        if npc_kills >= 1000 and npc_kills < 10000:
            string += f"**Gladiator:** <@&{fly_roles[7]}>\n"
        elif npc_kills >= 10000 and npc_kills < 20000:
            string += f"**Gladiator:** <@&{fly_roles[8]}>\n"
        elif npc_kills >= 20000:
            string += f"**Gladiator:** <@&{fly_roles[9]}>\n"
        else:
            string += f"**Gladiator:** Not Eligible\n"

        # Monster (PVP)
        pvp_kills = profile["user_kills"]
        if pvp_kills >= 100 and pvp_kills < 2500:
            string += f"**Monster:** <@&{fly_roles[10]}>\n"
        elif pvp_kills >= 2500 and pvp_kills < 10000:
            string += f"**Monster:** <@&{fly_roles[11]}>\n"
        elif pvp_kills >= 10000:
            string += f"**Monster:** <@&{fly_roles[12]}>\n"
        else:
            string += f"**Monster:** Not Eligible\n"

        # Quester
        quests = profile["quests_performed"]
        if quests >= 2500 and quests < 10000:
            string += f"**Quester:** <@&{fly_roles[13]}>\n"
        elif quests >= 10000 and quests < 30000:
            string += f"**Quester:** <@&{fly_roles[14]}>\n"
        elif quests >= 30000:
            string += f"**Quester:** <@&{fly_roles[15]}>\n"
        else:
            string += f"**Quester:** Not Eligible\n"

        # Forager
        total_skill_level = 0
        for skill in skills:

            if skill["skill"] == "crafting":
                continue

            else:
                total_skill_level = total_skill_level + skill["level"]

        if total_skill_level >= 150 and total_skill_level < 300:
            string += f"**Forager:** <@&{fly_roles[16]}>\n"
        elif total_skill_level >= 300 and total_skill_level < 500:
            string += f"**Forager:** <@&{fly_roles[17]}>\n"
        elif total_skill_level >= 500:
            string += f"**Forager:** <@&{fly_roles[18]}>\n"
        else:
            string += f"**Forager:** Not Eligible\n"

        # Tasker
        nr_tasks = profile["tasks_completed"]
        if nr_tasks >= 1000:
            string += f"**Tasker:** <@&{fly_roles[23]}>\n"
        elif nr_tasks >= 500:
            string += f"**Tasker:** <@&{fly_roles[22]}>\n"
        elif nr_tasks >= 250:
            string += f"**Tasker:** <@&{fly_roles[21]}>\n"
        else:
            string += f"**Tasker:** Not Eligible\n"

        wb_kills = profile["boss_kills"]
        if wb_kills >= 100:
            string += f"**Slayer:** <@&{fly_roles[25]}>\n"
        elif wb_kills >= 50:
            string += f"**Slayer:** <@&{fly_roles[24]}>\n"
        else:
            string += f"**Slayer:** Not Eligible\n"

         # Trader
        trades = profile["market_trades"]
        if trades >= 10000:
            string += f"**Trader:** <@&{fly_roles[27]}>\n"
        elif trades >= 1000:
            string += f"**Trader:** <@&{fly_roles[26]}>\n"
        else:
            string += f"**Trader:** Not Eligible\n"

        # Celebrity
        rep = profile["reputation"]
        if rep >= 500:
            string += f"**Celebrity:** <@&{fly_roles[31]}>\n"
        elif rep >= 200:
            string += f"**Celebrity:** <@&{fly_roles[30]}>\n"
        elif rep >= 30:
            string += f"**Celebrity:** <@&{fly_roles[29]}>\n"
        else:
            string += f"**Celebrity:** Not Eligible\n"

         # Veteran
        creation = profile["creation_date"]
        now = datetime.now(timezone.utc)
        creation = parser.parse(creation)
        difference = now - creation

        if difference.days >= 365:
            string += f"**Veteran:** <@&{fly_roles[32]}>\n"
        else:
            string += f"**Veteran:** Not Eligible\n"

        embed.description = string
        await ctx.send(embed=embed)

    @checks.no_bot_channel()
    @friendly.command(aliases=['roles'], enabled=False)
    @checks.in_fly()
    async def send_role_embed(self, ctx):

        string = ""
        string += f"`{ctx.prefix}fly thicc` - Level\n"
        string += f"`{ctx.prefix}fly stepper` - Steps Taken\n"
        string += f"`{ctx.prefix}fly gladiator` - NPC Kills\n"
        string += f"`{ctx.prefix}fly monster` - PvP Kills\n"
        string += f"`{ctx.prefix}fly quester` - Quests Completed\n"
        string += f"`{ctx.prefix}fly forager` - Skill Levels\n"
        string += f"`{ctx.prefix}fly tasker` - Tasks Completed\n"
        string += f"`{ctx.prefix}fly slayer` - World Boss Kills\n"
        string += f"`{ctx.prefix}fly trader` - Market Trades\n"
        string += f"`{ctx.prefix}fly celebrity` - Reputation\n"
        string += f"`{ctx.prefix}fly veteran` - Over 1 Year Old"

        embed = discord.Embed(
            title="Friendly Roles",
            description=string
        )

        await ctx.send(embed=embed)
        return

    @friendly.command(aliases=['thicc'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def thicc_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[2]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Thicc++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")
        # Thicc (Levels)
        level = profile["level"]
        if level >= 1000 and level < 5000:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[0]))
            embed.description = "You have been given the Thicc role"
            await ctx.send(embed=embed)
            return
        elif level >= 5000 and level < 10000:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[0]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[1]))
            embed.description = "You have been given the Thicc+ role"
            await ctx.send(embed=embed)
            return
        elif level >= 10000:
            for role in fly_roles[0:2]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[2]))
            embed.description = "You have been given the Thicc++ role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="Insufficient Level",
            description="You are below level 1000"
        ))
        return

    @friendly.command(aliases=['stepper'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def stepper_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[6]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Stepper+++."
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")
        # Stepper
        steps = profile["steps"]
        if steps >= 7500 and steps < 50000:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[3]))
            embed.description = "You have been given the Stepper role"
            await ctx.send(embed=embed)
            return
        elif steps >= 50000 and steps < 100000:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[3]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[4]))
            embed.description = "You have been given the Stepper+ role"
            await ctx.send(embed=embed)
            return
        elif steps >= 100000 and steps < 1000000:
            for role in fly_roles[3:5]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[5]))
            embed.description = "You have been given the Stepper++ role"
            await ctx.send(embed=embed)
            return
        elif steps >= 1000000:
            for role in fly_roles[3:6]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[6]))
            embed.description = "You have been given the Stepper+++ role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="Step more",
            description="You need more than 7500 steps for this role"
        ))

        return

    @friendly.command(aliases=['gladiator'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def gladiator_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[9]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Gladiator++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")
        # Gladiator (NPC)
        npc_kills = profile["npc_kills"]
        if npc_kills >= 1000 and npc_kills < 10000:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[7]))
            embed.description = "You have been given the Gladiator role"
            await ctx.send(embed=embed)
            return
        elif npc_kills >= 10000 and npc_kills < 20000:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[7]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[8]))
            embed.description = "You have been given the Gladiator+ role"
            await ctx.send(embed=embed)
            return
        elif npc_kills >= 20000:
            for role in fly_roles[7:9]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[9]))
            embed.description = "You have been given the Gladiator++ role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="It looks like you should visit the Battle Arena",
            description="You need more than 1000 NPC Kills for this role"
        ))

        return

    @friendly.command(aliases=['monster'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def monster_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[12]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Monster++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Monster (PVP)
        pvp_kills = profile["user_kills"]
        if pvp_kills >= 100 and pvp_kills < 2500:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[10]))
            embed.description = "You have been given the Monster role"
            await ctx.send(embed=embed)
            return
        elif pvp_kills >= 2500 and pvp_kills < 10000:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[10]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[11]))
            embed.description = "You have been given the Monster+ role"
            await ctx.send(embed=embed)
            return
        elif pvp_kills >= 10000:
            for role in fly_roles[10:12]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[12]))
            embed.description = "You have been given the Monster++ role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="I sense more bloodshed in your future",
            description="You need more than 100 Player Kills for this role"
        ))

        return

    @friendly.command(aliases=['quester'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def quester_roles(self, ctx):

        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[15]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Quester++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Quester
        quests = profile["quests_performed"]
        if quests >= 2500 and quests < 10000:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[13]))
            embed.description = "You have been given the Quester role"
            await ctx.send(embed=embed)
            return
        elif quests >= 10000 and quests < 30000:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[13]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[14]))
            embed.description = "You have been given the Quester+ role"
            await ctx.send(embed=embed)
            return
        elif quests >= 30000:
            for role in fly_roles[13:15]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[15]))
            embed.description = "You have been given the Quester++ role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="Are you an adventurer or a couch potato?",
            description="You need more than 2500 Quests Completed for this role"
        ))
        return

    @friendly.command(aliases=['forager'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def forager_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)

        if ctx.guild.get_role(fly_roles[18]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Forager++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Add special roles
        skills = await api.get_skills(smmoid)

        # Forager
        total_skill_level = 0
        for skill in skills:

            if skill["skill"] == "crafting":
                continue

            else:
                total_skill_level = total_skill_level + skill["level"]

        if total_skill_level >= 150 and total_skill_level < 300:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[16]))
            embed.description = "You have been given the Forager role"
            await ctx.send(embed=embed)
            return
        elif total_skill_level >= 300 and total_skill_level < 500:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[16]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[17]))
            embed.description = "You have been given the Forager+ role"
            await ctx.send(embed=embed)
            return
        elif total_skill_level >= 500:
            for role in fly_roles[16:18]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[18]))
            embed.description = "You have been given the Forager++ role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="You're supposed to collect materials, not look at them...",
            description="You need more than 150 Resource Skill Levels for this role"
        ))
        return

    @friendly.command(aliases=['tasker'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def tasker_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[23]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Tasker++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Tasker
        nr_tasks = profile["tasks_completed"]
        if nr_tasks >= 1000:
            for role in fly_roles[21:23]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[23]))
            embed.description = "You have been given the Tasker++ role"
            await ctx.send(embed=embed)
            return
        elif nr_tasks >= 500:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[21]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[22]))
            embed.description = "You have been given the Tasker+ role"
            await ctx.send(embed=embed)
            return
        elif nr_tasks >= 250:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[21]))
            embed.description = "You have been given the Tasker role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="More tasks are required of you",
            description=f"You need more than 250 Completed tasks for this role. You have {nr_tasks}."
        ))

        return

    @friendly.command(aliases=['slayer'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def slayer_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[25]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Slayer+"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Slayer (World Boss Kills)
        wb_kills = profile["boss_kills"]
        if wb_kills >= 100:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[24]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[25]))
            embed.description = "You have been given the Slayer+ role"
            await ctx.send(embed=embed)
            return
        elif wb_kills >= 50:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[24]))
            embed.description = "You have been given the Slayer role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="Have you even heard of a World Boss before?",
            description=f"You have killed {wb_kills} World Bosses and need 50 for Slayer."
        ))

        return

    @friendly.command(aliases=['trader'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def trader_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[27]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Trader+"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Trader
        trades = profile["market_trades"]
        if trades >= 10000:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[26]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[27]))
            embed.description = "You have been given the Trader+ role"
            await ctx.send(embed=embed)
            return
        elif trades >= 1000:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[26]))
            embed.description = "You have been given the Trader role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="Buy more stuff :)",
            description=f"You need at least 1000 trades and you have {trades}."
        ))
        return

    @friendly.command(aliases=['celebrity'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def celebrity_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.guild.get_role(fly_roles[31]) in ctx.author.roles:
            embed = discord.Embed(title="No Role Given")
            embed.description = "You already have Celebrity++"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Role Given")

        # Celebrity
        rep = profile["reputation"]
        if rep >= 500:
            for role in fly_roles[29:31]:
                await ctx.author.remove_roles(ctx.guild.get_role(role))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[31]))
            embed.description = "You have been given the Celebrity++ role"
            await ctx.send(embed=embed)
            return
        elif rep >= 200:
            await ctx.author.remove_roles(ctx.guild.get_role(fly_roles[29]))
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[30]))
            embed.description = "You have been given the Celebrity+ role"
            await ctx.send(embed=embed)
            return
        elif rep >= 30:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[29]))
            embed.description = "You have been given the Celebrity role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="Have you tried bribing noobs?",
            description=f"You need at least 30 reputation and you have {rep}."
        ))

        return

    @friendly.command(aliases=['veteran'], enabled=False)
    @checks.in_fly()
    @checks.is_verified()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def veteran_roles(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        profile = await api.get_all(smmoid)

        if ctx.author._roles.has(fly_roles[32]):
            await ctx.send(embed=discord.Embed(title="You already have this role silly"))
            return

        embed = discord.Embed(title="Role Given")

        # Veteran
        creation = profile["creation_date"]
        now = datetime.now(timezone.utc)
        creation = parser.parse(creation)
        difference = now - creation

        if difference.days >= 365:
            await ctx.author.add_roles(ctx.guild.get_role(fly_roles[32]))
            embed.description = "You have been given the Veteran role"
            await ctx.send(embed=embed)
            return

        await ctx.send(embed=discord.Embed(
            title="So little...",
            description=f"You've only been playing for {difference.days} days. Try again in {365-difference.days} days."
        ))

        return

    @friendly.command(aliases=['bfc'])
    @checks.is_fly_admin()
    @checks.in_fly()
    @commands.cooldown(1, 600, BucketType.guild)
    async def big_fly_check(self, ctx):

        all_fly_roles = [
            # Main Fly Role
            ctx.guild.get_role(710315282920636506),
            # NSF Role
            ctx.guild.get_role(722110578516164670), ctx.guild.get_role(
                783930500732551219),
            # Thicc (Levels)
            ctx.guild.get_role(727719624434778124), ctx.guild.get_role(
                727722577908334662), ctx.guild.get_role(727722769785028672),
            # Stepper
            ctx.guild.get_role(710290715787264041), ctx.guild.get_role(720049949865279559), ctx.guild.get_role(
                727947354929365003), ctx.guild.get_role(829700204357877812),
            # Gladiator (NPC)
            ctx.guild.get_role(724649998985461841), ctx.guild.get_role(
                724650153218277457), ctx.guild.get_role(752699779888316417),
            # Monster (PVP)
            ctx.guild.get_role(710293875289489458), ctx.guild.get_role(
                720052795679703138), ctx.guild.get_role(752703370510336080),
            # Quester
            ctx.guild.get_role(752700240213311580), ctx.guild.get_role(
                752700554672865290), ctx.guild.get_role(752700633920045139),
            # Forager
            ctx.guild.get_role(767163012132896808), ctx.guild.get_role(
                829700288976781312), ctx.guild.get_role(829700338893979718),
            # Tasker
            ctx.guild.get_role(752706107985625139), ctx.guild.get_role(
                752706496315261068), ctx.guild.get_role(763043799869030400),
            # Slayer
            ctx.guild.get_role(752702198303031376), ctx.guild.get_role(
                752702447662923777),
            # Decorated
            ctx.guild.get_role(731018776648089670), ctx.guild.get_role(
                731019364068753449),
            # Trader
            ctx.guild.get_role(710277160857763860), ctx.guild.get_role(
                829692366092238858), ctx.guild.get_role(720048172399067200),
            # Celebrity
            ctx.guild.get_role(710307235124871189), ctx.guild.get_role(
                720062633281192008), ctx.guild.get_role(752701722719289398),
            # Veteran
            ctx.guild.get_role(752705054351556658),
            # Suggester
            ctx.guild.get_role(720047404996624487),
            # Storyteller
            ctx.guild.get_role(774361923218309130),
            # Looter
            ctx.guild.get_role(720049700782342215),
            # Collector
            ctx.guild.get_role(710290631855177739), ctx.guild.get_role(
                720050166396354671), ctx.guild.get_role(752699424735494175),
            # Tycoon
            ctx.guild.get_role(723955238385746030), ctx.guild.get_role(
                723955584038076486),
            # Thief
            ctx.guild.get_role(734573085637869651), ctx.guild.get_role(
                734573239249928222),
            # Sniper
            ctx.guild.get_role(713281314882846730), ctx.guild.get_role(
                720053096855896084),
            # Diamond
            ctx.guild.get_role(717579223174348900), ctx.guild.get_role(
                720061797838618660),
            # Hero
            ctx.guild.get_role(710317545340797068), ctx.guild.get_role(
                720049289187033188),
            # Meme'd
            ctx.guild.get_role(710325364756447306), ctx.guild.get_role(
                720053250669281301),
            # Hunter
            ctx.guild.get_role(720052696757043294), ctx.guild.get_role(
                774354836614545419),
            # Enforcer
            ctx.guild.get_role(719173436856991804), ctx.guild.get_role(
                720052932971593800),
            # Contributor
            ctx.guild.get_role(868508713525334066), ctx.guild.get_role(
                720683761959960627), ctx.guild.get_role(720684106551132263),
            # Secret CF/BF
            ctx.guild.get_role(756119028543651951), ctx.guild.get_role(
                894229709192314920),
            # CF/BF/BFF (non-secret)
            ctx.guild.get_role(719181452855738400), ctx.guild.get_role(
                720041551069446225), ctx.guild.get_role(723506672944807946),
            # charity
            ctx.guild.get_role(713069407261425724),
            # ping roles
            ctx.guild.get_role(840696114537431080), ctx.guild.get_role(
                897118429629251584), ctx.guild.get_role(840694858259890196)
        ]

        try:
            guild = ctx.guild
            fly_role = guild.get_role(710315282920636506)
            members = fly_role.members
            not_in_fly = 0
            not_linked = 0
            total = 0

            fly1 = fly[0]
            fly2 = fly[1]
            fly3 = fly[2]
            fly4 = fly[3]

            fly1 = await api.guild_members(fly1)
            fly2 = await api.guild_members(fly2)
            fly3 = await api.guild_members(fly3)
            fly4 = await api.guild_members(fly4)

            fly1 = [x["user_id"] for x in fly1]
            fly2 = [x["user_id"] for x in fly2]
            fly3 = [x["user_id"] for x in fly3]
            fly4 = [x["user_id"] for x in fly4]

            allmembers = fly1 + fly2 + fly3 + fly4
            # for guild in fly:
            #     tempmembers = api.guild_members(guild)
            #     allmembers += [x["user_id"] for x in tempmembers]

            # await ctx.send(allmembers)

            listUsers = []
            await ctx.send(f"Starting. Checking {len(members)} people.")
            async with ctx.typing():
                for member in members:

                    total += 1
                    if(total % 100 == 0):
                        await ctx.send(f"{total} out of {len(members)} checked")

                    if await db.islinked(member.id):
                        smmoid = await db.get_smmoid(member.id)

                        if smmoid in allmembers:
                            # Add to database
                            try:
                                await db.fly_add(member.id, smmoid, 0)
                            except:
                                await db.fly_update(member.id, smmoid, 0)

                        # Has Friendly role, but not in Friendly.
                        else:
                            listUsers.append(f"{member.mention}")
                            print(f"{member.display_name}")

                            not_in_fly += 1
                            print(not_in_fly)
                            await member.remove_roles(*all_fly_roles, reason="User left fly")
                            await member.add_roles(ctx.guild.get_role(acquaintance))

                    else:
                        # unlinked. remove roles
                        not_linked += 1
                        print(f"{member.display_name}")

                        listUsers.append(f"{member.mention}")
                        await member.remove_roles(*all_fly_roles, reason="User left fly")
                        await member.add_roles(ctx.guild.get_role(acquaintance))

                await ctx.send(f"{len(members)} Friendly members checked.\n{not_in_fly} member(s) not in fly\n{not_linked} member(s) not linked to bot :(")

                splitUsers = [listUsers[i:i+33]
                              for i in range(0, len(listUsers), 33)]
                if len(splitUsers) != 0:
                    embed = Embed(
                        title="Users with Fly role removed"
                    )
                    for split in splitUsers:
                        embed.add_field(name="Users", value=' '.join(split))

                    await ctx.send(embed=embed)

                return
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @friendly.command(aliases=['log'])
    @checks.in_fly()
    @checks.is_owner()
    async def test2(self, ctx):
        try:
            await flylog(self.bot, "Testing Testing", "This is a test")
        except Exception as e:
            await ctx.send(e)
            await ctx.send(traceback.print_exc())

    @friendly.command(aliases=["rd"])
    @checks.is_owner()
    async def remove_dyl(self, ctx):
        await ctx.author.remove_roles(ctx.guild.get_role(710315282920636506))

    @friendly.command(aliases=["bd"])
    @checks.is_owner()
    async def bring_dyl(self, ctx):
        await ctx.author.add_roles(ctx.guild.get_role(710315282920636506))

    @friendly.command(aliases=['check_roles', 'cr', 'checkroles'], enabled=False)
    @checks.no_bot_channel()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.has_joined()
    @commands.cooldown(1, 60, BucketType.user)
    async def add_roles(self, ctx):
        member = ctx.author

        # First check if already has any of the roles bot gives:
        roleids = [r.id for r in member.roles]
        output = set(roleids).intersection(fly_roles)
        if len(output) > 1:
            string = ""
            string += "You already have at least one of the roles the bot can give out. Please use one of the following role commands to apply for new roles.\n"
            string += "\n"
            string += f"`{ctx.prefix}fly thicc` - Level\n"
            string += f"`{ctx.prefix}fly stepper` - Steps Taken\n"
            string += f"`{ctx.prefix}fly gladiator` - NPC Kills\n"
            string += f"`{ctx.prefix}fly monster` - PvP Kills\n"
            string += f"`{ctx.prefix}fly quester` - Quests Completed\n"
            string += f"`{ctx.prefix}fly forager` - Skill Levels\n"
            string += f"`{ctx.prefix}fly tasker` - Tasks Completed\n"
            string += f"`{ctx.prefix}fly slayer` - World Boss Kills\n"
            string += f"`{ctx.prefix}fly trader` - Market Trades\n"
            string += f"`{ctx.prefix}fly celebrity` - Reputation\n"
            string += f"`{ctx.prefix}fly veteran` - Over 1 Year Old"

            embed = discord.Embed(
                title="Nope",
                description=string
            )

            await ctx.send(embed=embed)
            return

        smmoid = await db.get_smmoid(member.id)
        profile = await api.get_all(smmoid)
        rolesadded = ""
        # Add special roles
        skills = await api.get_skills(smmoid)
        async with ctx.typing():
            # Thicc (Levels)
            level = profile["level"]
            if level >= 1000 and level < 5000:
                role = ctx.guild.get_role(fly_roles[0])
                rolesadded += f"<@&{role.id}> "
                await member.add_roles(role)

            elif level >= 5000 and level < 10000:
                role = ctx.guild.get_role(fly_roles[1])
                rolesadded += f"<@&{role.id}> "
                await member.add_roles(role)
            elif level >= 10000:
                role = ctx.guild.get_role(fly_roles[2])
                rolesadded += f"<@&{role.id}> "
                await member.add_roles(role)

            # Stepper
            steps = profile["steps"]
            if steps >= 7500 and steps < 50000:
                rolesadded += f"<@&{fly_roles[3]}> "
                await member.add_roles(ctx.guild.get_role(fly_roles[3]))
            elif steps >= 50000 and steps < 100000:
                rolesadded += f"<@&{fly_roles[4]}> "
                await member.add_roles(ctx.guild.get_role(fly_roles[4]))
            elif steps >= 100000 and steps < 1000000:
                await member.add_roles(ctx.guild.get_role(fly_roles[5]))
                rolesadded += f"<@&{fly_roles[5]}> "
            elif steps >= 1000000:
                await member.add_roles(ctx.guild.get_role(fly_roles[6]))
            # Gladiator (NPC)
            npc_kills = profile["npc_kills"]
            if npc_kills >= 1000 and npc_kills < 10000:
                await member.add_roles(ctx.guild.get_role(fly_roles[7]))
                rolesadded += f"<@&{fly_roles[7]}> "
            elif npc_kills >= 10000 and npc_kills < 20000:
                await member.add_roles(ctx.guild.get_role(fly_roles[8]))
                rolesadded += f"<@&{fly_roles[8]}> "
            elif npc_kills >= 20000:
                await member.add_roles(ctx.guild.get_role(fly_roles[9]))
                rolesadded += f"<@&{fly_roles[9]}> "

            # Monster (PVP)
            pvp_kills = profile["user_kills"]
            if pvp_kills >= 100 and pvp_kills < 2500:
                await member.add_roles(ctx.guild.get_role(fly_roles[10]))
                rolesadded += f"<@&{fly_roles[10]}> "
            elif pvp_kills >= 2500 and pvp_kills < 10000:
                await member.add_roles(ctx.guild.get_role(fly_roles[11]))
                rolesadded += f"<@&{fly_roles[11]}> "
            elif pvp_kills >= 10000:
                await member.add_roles(ctx.guild.get_role(fly_roles[12]))
                rolesadded += f"<@&{fly_roles[12]}> "
            # Quester
            quests = profile["quests_performed"]
            if quests >= 2500 and quests < 10000:
                await member.add_roles(ctx.guild.get_role(fly_roles[13]))
                rolesadded += f"<@&{fly_roles[13]}> "
            elif quests >= 10000 and quests < 30000:
                await member.add_roles(ctx.guild.get_role(fly_roles[14]))
                rolesadded += f"<@&{fly_roles[14]}> "
            elif quests >= 30000:
                await member.add_roles(ctx.guild.get_role(fly_roles[15]))
                rolesadded += f"<@&{fly_roles[15]}> "

            # Tasker
            nr_tasks = profile["tasks_completed"]
            if nr_tasks >= 1000:
                await member.add_roles(ctx.guild.get_role(fly_roles[23]))
                rolesadded += f"<@&{fly_roles[23]}> "
            elif nr_tasks >= 500:
                await member.add_roles(ctx.guild.get_role(fly_roles[22]))
                rolesadded += f"<@&{fly_roles[22]}> "
            if nr_tasks >= 250:
                await member.add_roles(ctx.guild.get_role(fly_roles[21]))
                rolesadded += f"<@&{fly_roles[21]}> "

            # Slayer
            wb_kills = profile["boss_kills"]
            if wb_kills >= 100:
                await member.add_roles(ctx.guild.get_role(fly_roles[25]))
                rolesadded += f"<@&{fly_roles[25]}> "
            elif wb_kills >= 50:
                await member.add_roles(ctx.guild.get_role(fly_roles[24]))
                rolesadded += f"<@&{fly_roles[24]}> "

            # Trader
            trades = profile["market_trades"]
            if trades >= 10000:
                await member.add_roles(ctx.guild.get_role(fly_roles[27]))
                rolesadded += f"<@&{fly_roles[27]}> "
            elif trades >= 1000:
                await member.add_roles(ctx.guild.get_role(fly_roles[26]))
                rolesadded += f"<@&{fly_roles[26]}> "

            # Celebrity
            rep = profile["reputation"]
            if rep >= 500:
                await member.add_roles(ctx.guild.get_role(fly_roles[31]))
                rolesadded += f"<@&{fly_roles[31]}> "
            elif rep >= 200:
                await member.add_roles(ctx.guild.get_role(fly_roles[30]))
                rolesadded += f"<@&{fly_roles[30]}> "
            elif rep >= 30:
                await member.add_roles(ctx.guild.get_role(fly_roles[29]))
                rolesadded += f"<@&{fly_roles[29]}> "

            # Veteran
            creation = profile["creation_date"]
            now = datetime.now(timezone.utc)
            creation = parser.parse(creation)
            difference = now - creation
            if difference.days >= 365:
                await member.add_roles(ctx.guild.get_role(fly_roles[32]))
                rolesadded += f"<@&{fly_roles[32]}> "

            # Forager
            total_skill_level = 0
            for skill in skills:

                if skill["skill"] == "crafting":
                    continue

                else:
                    total_skill_level = total_skill_level + skill["level"]

            if total_skill_level >= 150 and total_skill_level < 300:
                await member.add_roles(ctx.guild.get_role(fly_roles[16]))
                rolesadded += f"<@&{fly_roles[16]}> "
            elif total_skill_level >= 300 and total_skill_level < 500:
                await member.add_roles(ctx.guild.get_role(fly_roles[17]))
                rolesadded += f"<@&{fly_roles[17]}> "
            elif total_skill_level >= 500:
                await member.add_roles(ctx.guild.get_role(fly_roles[18]))
                rolesadded += f"<@&{fly_roles[18]}> "

            ingamename = profile["name"]

            await ctx.send(embed=Embed(
                title="Success",
                description=f"You have been given all applicable roles. Contact <@332314562575597579> if they seem to be incorrect."
            ))
            await flylog(self.bot, "Role check run",
                         f"**Roles given to {ingamename}:**\n{rolesadded}", member.id)

        return

    @friendly.command(aliases=["rfr"])
    @checks.in_fly()
    @checks.is_verified()
    @checks.is_fly_admin()
    @commands.cooldown(1, 30, BucketType.user)
    async def remove_all_roles(self, ctx, member: discord.Member):
        async with ctx.typing():
            if member is not None:
                for roleid in fly_roles[:18]:
                    role = (ctx.guild.get_role(roleid))
                    await member.remove_roles(role, reason="Admin role removal")
                for roleid in fly_roles[21:]:
                    role = (ctx.guild.get_role(roleid))
                    await member.remove_roles(role, reason="Admin role removal")

            await ctx.send(f"Roles have been removed from {member.display_name}")

    @friendly.command(aliases=["traveler"])
    @checks.in_fly()
    @checks.is_verified()
    @checks.is_owner()
    async def remove_traveler(self, ctx, member: discord.Member):

        if member is not None:
            await member.remove_roles(ctx.guild.get_role(traveler))

    @friendly.command(aliases=['fj'])
    @checks.is_owner()
    async def force_join(self, ctx, member: discord.Member):
        if member._roles.has(fly_roles[19]):

            if not await db.in_fly(member.id):
                smmoid = await db.get_smmoid(member.id)
                profile = await api.get_all(smmoid)
                try:
                    guildid = profile["guild"]["id"]
                except KeyError as e:
                    return
                await db.fly_add(member.id, smmoid, guildid)
                await ctx.send("Added to database :P")
                await ctx.send(f"Welcome to Friendly :)\nYou can run `{ctx.prefix}fly check_roles` to check for all available Friendly roles\nOr you can run `{ctx.prefix}fly roles` for specific roles")
                return

            await ctx.send("They've already been granted the Friendly role :)")
            return

        smmoid = await db.get_smmoid(member.id)

        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("They are not in a guild")
            return

        # if user is in a fly guild....
        if guildid in fly or member.id == dyl:
            if not await db.in_fly(member.id):
                await db.fly_add(member.id, smmoid, guildid)

            # if user is in NSF
            if guildid == 541:
                await member.add_roles(ctx.guild.get_role(fly_roles[20]))

            # add fly role
            await member.add_roles(ctx.guild.get_role(fly_roles[19]))
            await member.add_roles(ctx.guild.get_role(traveler))
            await member.remove_roles(ctx.guild.get_role(acquaintance))
            await ctx.send(f"Welcome to Friendly :)\nYou can run `{ctx.prefix}fly check_roles` to check for all available Friendly roles\nOr you can run `{ctx.prefix}fly roles` for specific roles")

        else:
            await ctx.send("You are not in Fly. Try contacting a Big Friend if you believe this is a mistake")
            return

    @tasks.loop(hours=3)
    async def flycheck(self):
        await log(self.bot, "Fly Check Started", "Friendly guild members are being checked")
        await flylog2(self.bot, "Fly Check Started", "Friendly guild members are being checked")
        guild = self.bot.get_guild(710258284661178418)
        all_fly_roles = [
            # Main Fly Role
            guild.get_role(710315282920636506),
            # NSF Role
            guild.get_role(722110578516164670), guild.get_role(
                783930500732551219),
            # Thicc (Levels)
            guild.get_role(727719624434778124), guild.get_role(
                727722577908334662), guild.get_role(727722769785028672),
            # Stepper
            guild.get_role(710290715787264041), guild.get_role(720049949865279559), guild.get_role(
                727947354929365003), guild.get_role(829700204357877812),
            # Gladiator (NPC)
            guild.get_role(724649998985461841), guild.get_role(
                724650153218277457), guild.get_role(752699779888316417),
            # Monster (PVP)
            guild.get_role(710293875289489458), guild.get_role(
                720052795679703138), guild.get_role(752703370510336080),
            # Quester
            guild.get_role(752700240213311580), guild.get_role(
                752700554672865290), guild.get_role(752700633920045139),
            # Forager
            guild.get_role(767163012132896808), guild.get_role(
                829700288976781312), guild.get_role(829700338893979718),
            # Tasker
            guild.get_role(752706107985625139), guild.get_role(
                752706496315261068), guild.get_role(763043799869030400),
            # Slayer
            guild.get_role(752702198303031376), guild.get_role(
                752702447662923777),
            # Decorated
            guild.get_role(731018776648089670), guild.get_role(
                731019364068753449),
            # Trader
            guild.get_role(710277160857763860), guild.get_role(
                829692366092238858), guild.get_role(720048172399067200),
            # Celebrity
            guild.get_role(710307235124871189), guild.get_role(
                720062633281192008), guild.get_role(752701722719289398),
            # Veteran
            guild.get_role(752705054351556658),
            # Suggester
            guild.get_role(720047404996624487),
            # Storyteller
            guild.get_role(774361923218309130),
            # Looter
            guild.get_role(720049700782342215),
            # Collector
            guild.get_role(710290631855177739), guild.get_role(
                720050166396354671), guild.get_role(752699424735494175),
            # Tycoon
            guild.get_role(723955238385746030), guild.get_role(
                723955584038076486),
            # Thief
            guild.get_role(734573085637869651), guild.get_role(
                734573239249928222),
            # Sniper
            guild.get_role(713281314882846730), guild.get_role(
                720053096855896084),
            # Diamond
            guild.get_role(717579223174348900), guild.get_role(
                720061797838618660),
            # Hero
            guild.get_role(710317545340797068), guild.get_role(
                720049289187033188),
            # Meme'd
            guild.get_role(710325364756447306), guild.get_role(
                720053250669281301),
            # Hunter
            guild.get_role(720052696757043294), guild.get_role(
                774354836614545419),
            # Enforcer
            guild.get_role(719173436856991804), guild.get_role(
                720052932971593800),
            # Contributor
            guild.get_role(868508713525334066), guild.get_role(
                720683761959960627), guild.get_role(720684106551132263),
            # Secret CF/BF
            guild.get_role(756119028543651951), guild.get_role(
                894229709192314920),
            # CF/BF/BFF (non-secret)
            guild.get_role(719181452855738400), guild.get_role(
                720041551069446225), guild.get_role(723506672944807946),
            # charity
            guild.get_role(713069407261425724),
            # ping roles
            guild.get_role(840696114537431080), guild.get_role(
                897118429629251584), guild.get_role(840694858259890196)
        ]

        fly_role = guild.get_role(710315282920636506)
        members = fly_role.members
        not_in_fly = 0
        not_linked = 0
        total = 0

        fly1 = fly[0]
        fly2 = fly[1]
        fly3 = fly[2]
        fly4 = fly[3]

        fly1 = await api.guild_members(fly1)
        fly2 = await api.guild_members(fly2)
        fly3 = await api.guild_members(fly3)
        fly4 = await api.guild_members(fly4)

        fly1 = [x["user_id"] for x in fly1]
        fly2 = [x["user_id"] for x in fly2]
        fly3 = [x["user_id"] for x in fly3]
        fly4 = [x["user_id"] for x in fly4]

        allmembers = fly1 + fly2 + fly3 + fly4
        listUsers = []

        for member in members:
            total += 1
            if await db.islinked(member.id):
                smmoid = await db.get_smmoid(member.id)

                if smmoid in allmembers:
                    # Add to database
                    try:
                        await db.fly_add(member.id, smmoid, 0)
                    except:
                        await db.fly_update(member.id, smmoid, 0)

                # Has Friendly role, but not in Friendly.
                else:
                    listUsers.append(f"{member.mention}")
                    not_in_fly += 1
                    memberroles = ""
                    for role in member.roles:
                        memberroles += f"{role.mention}\n"
                    await flylog3(self.bot, Embed(title=f"{member.display_name}'s Roles", description=memberroles))
                    await member.remove_roles(*all_fly_roles, reason="User left fly")
                    await member.add_roles(guild.get_role(acquaintance))

            else:
                # unlinked. remove roles
                not_linked += 1
                memberroles = ""
                for role in member.roles:
                    memberroles += f"{role.mention}\n"
                await flylog3(self.bot, Embed(title=f"{member.display_name}'s Roles", description=memberroles))

                listUsers.append(f"{member.mention}")
                await member.remove_roles(*all_fly_roles, reason="User left fly")
                await member.add_roles(guild.get_role(acquaintance))

        await flylog2(self.bot, "Friendly Check", f"{len(members)} Friendly members checked.\n{not_in_fly} member(s) not in fly\n{not_linked} member(s) not linked to bot :(")
        splitUsers = [listUsers[i:i+33]
                      for i in range(0, len(listUsers), 33)]
        if len(splitUsers) != 0:
            embed = Embed(
                title="Users with Fly role removed"
            )
            for split in splitUsers:
                embed.add_field(name="Users", value=' '.join(split))

            flylog3(self.bot, embed)

    @flycheck.before_loop
    async def before_flycheck(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Friendly(bot))

    print("Friendly Cog Loaded")
