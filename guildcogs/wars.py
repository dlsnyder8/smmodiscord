from discord.ext import commands, tasks
from discord import Embed
import api
from util import checks, log
import database as db
import logging
from datetime import datetime, timezone, timedelta
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Wars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gold_ping.start()

    @checks.in_fly_guild()
    @commands.group(aliases=['war', 'w'], hidden=True)
    async def wars(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @wars.command(aliases=['fly'])
    async def friendly(self, ctx):
        wars = await api.get_guild_wars(408, 1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Friendly", description="There are no active wars. They may be on hold or may have all ended."))
            return

    
        warstring = ""
        for war in wars[:35]:
            if war['guild_1']['id'] == 408:
                friendly = war['guild_1']
                guild = war['guild_2']
            else:
                friendly = war['guild_2']
                guild = war['guild_1']

            warstring += f"({guild['id']}) **{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members?new_page=true&attackable=true)\n"

            if len(warstring) > 1900:
                embed = Embed(title="Friendly Wars", description=warstring)
                await ctx.send(embed=embed)
                warstring = ""

        embed = Embed(title="Friendly Wars", description=warstring)
        await ctx.send(embed=embed)

    @wars.command()
    async def too(self, ctx):
        wars = await api.get_guild_wars(455, 1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Friendly Too", description="There are no active wars. They may be on hold or may have all ended."))
            return

        warstring = ""
        for war in wars:
            if war['guild_1']['id'] == 455:
                friendly = war['guild_1']
                guild = war['guild_2']
            else:
                friendly = war['guild_2']
                guild = war['guild_1']

            warstring += f"({guild['id']}) **{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members?new_page=true&attackable=true)\n"
            if len(warstring) > 1900:
                embed = Embed(title="Friendly Too Wars", description=warstring)
                await ctx.send(embed=embed)
                warstring = ""

        await ctx.send(embed=Embed(title="Friendly Too Wars", description=warstring))

    @wars.command(aliases=['stl'])
    async def still(self, ctx):
        wars = await api.get_guild_wars(482, 1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Still", description="There are no active wars. They may be on hold or may have all ended."))
            return

        warstring = ""
        for war in wars:
            if war['guild_1']['id'] == 482:
                friendly = war['guild_1']
                guild = war['guild_2']
            else:
                friendly = war['guild_2']
                guild = war['guild_1']

            warstring += f"({guild['id']}) **{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members?new_page=true&attackable=true)\n"
            if len(warstring) > 1900:
                embed = Embed(title="Still Wars", description=warstring)
                await ctx.send(embed=embed)
                warstring = ""

        await ctx.send(embed=Embed(title="Still Wars", description=warstring))

    @wars.command()
    async def nsf(self, ctx):
        wars = await api.get_guild_wars(541, 1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for NSF", description="There are no active wars. They may be on hold or may have all ended."))
            return

        warstring = ""
        for war in wars:
            if war['guild_1']['id'] == 541:
                friendly = war['guild_1']
                guild = war['guild_2']
            else:
                friendly = war['guild_2']
                guild = war['guild_1']
            warstring += f"({guild['id']}) **{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members?new_page=true&attackable=true)\n"

            if len(warstring) > 1900:
                embed = Embed(title="NSF Wars", description=warstring)
                await ctx.send(embed=embed)
                warstring = ""

        await ctx.send(embed=Embed(title="NSF Wars", description=warstring))

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.is_verified()
    async def setup(self, ctx, guildid: int):
        if await db.warinfo_isadded(ctx.author.id):
            await ctx.send(f"You already did this. If you need a list of customization options, run `{ctx.prefix}war options`")
            return

        if guildid not in (408, 455, 541, 482):
            await ctx.send("It appears you did not enter a valid Friendly guild id. The options are:\n**408** - Fly\n**455** - Too\n**541** - NSF\n**482** - Still\n")
            return

        smmoid = await db.get_smmoid(ctx.author.id)
        await db.warinfo_setup(ctx.author.id, smmoid, guildid)

        await ctx.send(f"Success! Please run `{ctx.prefix}war options` for a list of customization options, or run `{ctx.prefix}war profile` to see your current profile")

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def options(self, ctx):
        embed = Embed(title="Customization Options")
        string = f"`{ctx.prefix}war guild <int>` - change which guild you're currently in (needs to be a Fly guild)\n"
        string += f"`{ctx.prefix}war minlevel <int>` - sets the min level of your targets (default 200)\n"
        string += f"`{ctx.prefix}war maxlevel <int>` - sets the max level of your targets (default 10,000)\n"
        string += f"`{ctx.prefix}war goldping <bool>` - get pinged if out of safemode and gold is above your threshold\n"
        string += f"`{ctx.prefix}war gold <int>` - threshold amount to get pinged for (default 5,000,000)\n"

        embed.description = string
        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def profile(self, ctx):

        info = await db.warinfo_profile(ctx.author.id)

        embed = Embed(title="Your War Profile")
        string = f"**SMMO ID:** {info.smmoid}\n"
        string += f"**Guild ID:** {info.guildid}\n"
        string += f"**Min Level:** {info.min_level}\n"
        string += f"**Max Level:** {info.max_level}\n"
        string += f"**Gold Ping:** {'Active' if info.gold_ping else 'Inactive'}\n"
        string += f"**Gold Ping Amount:** {info.gold_amount:,}"

        embed.description = string
        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def guild(self, ctx, guildid: int):
        if guildid not in (408, 455, 541, 482):
            await ctx.send("It appears you did not enter a valid Friendly guild id. The options are:\n**408** - Fly\n**455** - Too\n**541** - NSF\n**482** - Still\n")
            return

        await db.warinfo_guild(ctx.author.id, guildid)
        await ctx.send(f"You have changed your active guild to {guildid}")

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def minlevel(self, ctx, level: int):
        await db.warinfo_minlevel(ctx.author.id, level)
        await ctx.send(f"Min level updated to: {level:,}")
        return

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def maxlevel(self, ctx, level: int):
        await db.warinfo_maxlevel(ctx.author.id, level)
        await ctx.send(f"Max level updated to: {level:,}")
        return

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def goldping(self, ctx, ping: bool):
        await db.warinfo_goldping(ctx.author.id, ping)
        await ctx.send(f"Gold ping set to: {'Active' if ping else 'Inactive'}")
        return

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def gold(self, ctx, amount: int):
        await db.warinfo_goldamount(ctx.author.id, amount)
        await ctx.send(f"You will be pinged if your gold is above {amount:,}")
        return

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def attack(self, ctx, guildid: int):
        profile = await db.warinfo_profile(ctx.author.id)

        async with ctx.typing():
            embed = Embed(title="Targets",
                          description=f"{ctx.author.mention}'s Targets")
            attacklist = ""

            members = await api.guild_members(guildid)
            if members is None:
                await ctx.send("Invalid Guild ID or API Malfunction")
                return
            members = [x for x in members if x['level'] >= profile.min_level and x['level'] <=
                       profile.max_level and x['current_hp']/x['max_hp'] > 0.5 and x['safe_mode'] == 0]
            for member in members:
                attacklist += f"[{member['name']}](https://web.simple-mmo.com/user/attack/{member['user_id']}) - Level {member['level']}\n"

                if len(attacklist) > 300:
                    embed.add_field(name="Attack", value=attacklist)
                    attacklist = ""
                if len(embed) > 5500:
                    await ctx.send(embed=embed)
                    embed = Embed(
                        title="Targets", description=f"{ctx.author.mention}'s Targets")

            if len(attacklist) > 0:
                embed.add_field(name="Attack", value=attacklist)
        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def targets(self, ctx):
        profile = await db.warinfo_profile(ctx.author.id)
        targets = await api.get_guild_wars(profile.guildid, 1)
        members = []
        async with ctx.typing():
            for i in range(5):
                try:
                    if targets[i]['guild_2']['id'] in (408, 455, 541, 482):
                        members += await api.guild_members(targets[i]['guild_1']['id'])
                    else:
                        members += await api.guild_members(targets[i]['guild_2']['id'])
                except IndexError:
                    break

            members.sort(reverse=True, key=lambda x: x['level'])
            members = [x for x in members if x['level'] >= profile.min_level and x['level'] <=
                       profile.max_level and x['current_hp']/x['max_hp'] > 0.5 and x['safe_mode'] == 0]

            embed = Embed(title="Targets",
                          description=f"{ctx.author.mention}'s Targets")
            attacklist = ""

            for member in members:
                attacklist += f"[{member['name']}](https://web.simple-mmo.com/user/attack/{member['user_id']}) - Level {member['level']}\n"

                if len(attacklist) > 300:
                    embed.add_field(name="Attack", value=attacklist)
                    attacklist = ""
                if len(embed) > 5500:
                    await ctx.send(embed=embed)
                    embed = Embed(
                        title="Targets", description=f"{ctx.author.mention}'s Targets")

            if len(attacklist) > 0:
                embed.add_field(name="Attack", value=attacklist)

        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def top15(self, ctx):
        profile = await db.warinfo_profile(ctx.author.id)
        targets = await api.get_guild_wars(profile[1], 1)
        members = []

        async with ctx.typing():
            for i in range(15):
                try:
                    if targets[i]['guild_2']['id'] in (408, 455, 541, 482):
                        members += await api.guild_members(targets[i]['guild_1']['id'])
                    else:
                        members += await api.guild_members(targets[i]['guild_2']['id'])
                except IndexError:
                    break

            members.sort(reverse=True, key=lambda x: x['level'])
            members = [x for x in members if x['level'] >= profile.min_level and x['level'] <=
                       profile.max_level and x['current_hp']/x['max_hp'] > 0.5 and x['safe_mode'] == 0]
            embed = Embed(title="Targets",
                          description=f"{ctx.author.mention}'s Targets")
            attacklist = ""

            for member in members:
                attacklist += f"[{member['name']}](https://web.simple-mmo.com/user/attack/{member['user_id']}) - Level {member['level']}\n"

                if len(attacklist) > 300:
                    embed.add_field(name="Attack", value=attacklist)
                    attacklist = ""
                if len(embed) > 5500:
                    await ctx.send(embed=embed)
                    embed = Embed(
                        title="Targets", description=f"{ctx.author.mention}'s Targets")

            if len(attacklist) > 0:
                embed.add_field(name="Attack", value=attacklist)

        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def top(self, ctx, num: int):
        profile = await db.warinfo_profile(ctx.author.id)
        targets = await api.get_guild_wars(profile.guildid, 1)
        members = []

        async with ctx.typing():
            for i in range(num):
                try:
                    if targets[i]['guild_2']['id'] in (408, 455, 541, 482):
                        members += await api.guild_members(targets[i]['guild_1']['id'])
                    else:
                        members += await api.guild_members(targets[i]['guild_2']['id'])
                except IndexError:
                    break

            members.sort(reverse=True, key=lambda x: x['level'])
            members = [x for x in members if x['level'] >= profile.min_level and x['level'] <=
                       profile.max_level and x['current_hp']/x['max_hp'] > 0.5 and x['safe_mode'] == 0]
            embed = Embed(title="Targets",
                          description=f"{ctx.author.mention}'s Targets")
            attacklist = ""

            for member in members:
                attacklist += f"[{member['name']}](https://web.simple-mmo.com/user/attack/{member['user_id']}) - Level {member['level']}\n"

                if len(attacklist) > 300:
                    embed.add_field(name="Attack", value=attacklist)
                    attacklist = ""
                if len(embed) > 5500:
                    await ctx.send(embed=embed)
                    embed = Embed(
                        title="Targets", description=f"{ctx.author.mention}'s Targets")

            if len(attacklist) > 0:
                embed.add_field(name="Attack", value=attacklist)

        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def all(self, ctx):
        profile = await db.warinfo_profile(ctx.author.id)
        targets = await api.get_guild_wars(profile.guildid, 1)
        async with ctx.typing():
            embed = Embed(title="Targets",
                          description=f"{ctx.author.mention}'s Targets")
            attacklist = ""
            members = []
            for i in range(500):
                try:
                    if targets[i]['guild_2']['id'] in (408, 455, 541, 482):
                        members += await api.guild_members(targets[i]['guild_1']['id'])
                    else:
                        members += await api.guild_members(targets[i]['guild_2']['id'])

                except IndexError:
                    break

                members.sort(reverse=True, key=lambda x: x['level'])
                members = [x for x in members if x['level'] >= profile.min_level and x['level'] <=
                           profile.max_level and x['current_hp']/x['max_hp'] > 0.5 and x['safe_mode'] == 0]

            for member in members:
                attacklist += f"[{member['name']}](https://web.simple-mmo.com/user/attack/{member['user_id']}) - Level {member['level']}\n"

                if len(attacklist) > 300:
                    embed.add_field(name="Attack", value=attacklist)
                    attacklist = ""
                if len(embed) > 5500:
                    await ctx.send(embed=embed)
                    embed = Embed(
                        title="Targets", description=f"{ctx.author.mention}'s Targets")

            if len(attacklist) > 0:
                embed.add_field(name="Attack", value=attacklist)

        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def status(self, ctx, target: int):
        async with ctx.typing():
            profile = await db.warinfo_profile(ctx.author.id)

            guilds = await api.get_guild_wars(profile.guildid, 1)

            guild = [x for x in guilds if x['guild_2']['id'] == target]
            if len(guild) == 0:
                guild = [x for x in guilds if x['guild_1']['id'] == target]
                # TODO: This check below does not work
                # Possibly fixed with ==[] check
                if guild == []:
                    await ctx.send("That guild either doesn't exist or is not actively at war with you")
                    return
            else:

                guild = guild[0]
                embed = Embed(
                    title="War Status", description=f"**{guild['guild_1']['name']}**\n{guild['guild_1']['kills']}\n\n**{guild['guild_2']['name']}**\n{guild['guild_2']['kills']}")
                await ctx.send(embed=embed)
            return

    @wars.command(aliases=['nosm'])
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def nosafemode(self, ctx, target: int):
        async with ctx.typing():
            guildmembers = await api.guild_members(target)
            if guildmembers is None:
                await ctx.send("That guild id does not appear to be valid")
                return
            guildinfo = await api.guild_info(target)
            members = [x for x in guildmembers if x['safe_mode'] == 0]
            embed = Embed(
                title="No Safe Mode", description=f"{guildinfo['name']} members out of safe mode")
            attacklist = ""
            for member in members:
                attacklist += f"[{member['name']}](https://web.simple-mmo.com/user/attack/{member['user_id']}) - Level {member['level']}\n"

                if len(attacklist) > 250:
                    embed.add_field(name="\u200b", value=attacklist)
                    attacklist = ""
                if len(embed) > 5600:
                    await ctx.send(embed=embed)
                    embed = Embed(
                        title="No Safe Mode", description=f"{guildinfo['name']} members out of safe mode")

            if len(attacklist) > 0:
                embed.add_field(name="Attack", value=attacklist)
            await ctx.send(embed=embed)
            return

    @tasks.loop(minutes=5, reconnect=True)
    async def gold_ping(self):
        try:
            await log.log(self.bot, "Gold Ping", "Checking for friendly members with gold out....")
            channel = self.bot.get_channel(846657320184053760)
            if channel is None:
                logging.error('Unable to find Friendly gold channel')
                return
            members = await db.gold_ping_users()
            for member in members:

                smmoid = member.smmoid
                discordid = member.discordid
                goldamount = member.gold_amount
                lastping = member.last_pinged

                plus30min = lastping + timedelta(minutes=29)
                # No API calls if it hasn't even been 30 minutes since last ping

                if plus30min > datetime.now(timezone.utc):
                    continue

                info = await api.get_all(smmoid)
                if info is None:
                    logging.error("Api Call get_all has failed")
                    continue

                # Skip user if not in Friendly guild
                try:
                    if info['guild']['id'] not in (408, 455, 541, 482):
                        continue
                except Exception:
                    continue

                if info['safeMode'] == 0 and info['gold'] >= goldamount and info['hp']/info['max_hp'] > 0.5:

                    embed = Embed(
                        title="Actions", description=f":bank: [Quick, bank your gold!](https://web.simple-mmo.com/bank) \n \u200b \n:shield: [Help! Stab to protect their gold!](https://web.simple-mmo.com/user/attack/{smmoid})")
                    await channel.send(f"<@{discordid}> gold ping! {info['gold']:,} gold out!", embed=embed)
                    await db.warinfo_ping_update(discordid)
        except Exception as e:
            logging.error(e)

    @gold_ping.before_loop
    async def before_gold_ping(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Wars(bot))
    logger.info("Wars Cog Loaded")
