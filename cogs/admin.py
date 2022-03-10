import discord
from discord.embeds import Embed
from discord.ext import commands, tasks
from util import checks, log
import database as db
from discord.ext.commands.cooldowns import BucketType
import api
import asyncio
import time
import logging
import aiofiles
import random

dyl = 332314562575597579
server = 444067492013408266

fly = (408, 455, 541, 482)


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_all_plebs.start()
        self.update_all_guilds.start()
        # self.yadda.start()

    @checks.is_owner()
    @commands.group(aliases=['a'], hidden=True, case_insensitive=True)
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @commands.cooldown(1, 300, BucketType.guild)
    @commands.command()
    async def topic(self, ctx):
        async with aiofiles.open("assets/starters.txt", mode='r') as f:
            content = await f.read()

        content = content.splitlines()
        line = random.choice(content)

        await ctx.send(line)

    @commands.command()
    @checks.is_owner()
    async def split(self, ctx, channel: discord.TextChannel, messageid):
        try:
            message = await channel.fetch_message(messageid)
            users = message.raw_mentions

            string = ""

            for user in users:
                string += f"{user} "

            await ctx.send(string)
        except discord.NotFound:
            await ctx.send("Message not found")

        except discord.Forbidden:
            await ctx.send("Not enough permissions")

        except discord.HTTPException:
            await ctx.send("HTTP Error")

    @checks.is_owner()
    @admin.command()
    async def forceremove(self, ctx, smmoid: int):
        try:
            val = await db.remove_user(smmoid)
            if val:
                await ctx.send("Success!")
            else:
                await ctx.send("They weren't removed. Either they never started verification or something else.")
        except Exception as e:
            await ctx.send("Uh oh")
            raise e

    @checks.is_owner()
    @admin.command(hidden=True)
    async def unlink(self, ctx, member: discord.Member):
        if(await db.islinked(str(member.id))):
            smmoid = await db.get_smmoid(str(member.id))
            if(await db.remove_user(str(smmoid))):
                await ctx.send(f"User {smmoid} successfully removed")
            else:
                await ctx.send(f"User {smmoid} was not removed")
                return

            if await db.is_added(str(member.id)):  # if linked to a guild
                leaderrole = ctx.guild.get_role(int(await db.leader_id(server)))
                ambassadorrole = ctx.guild.get_role(int(await db.ambassador_role(server)))

                guildid, smmoid = await db.ret_guild_smmoid(str(member.id))
                if(await db.is_leader(str(member.id))):

                    ambassadors = await db.all_ambassadors()
                    guildambs = [x for x in ambassadors if x[2] == guildid]

                    print(
                        f"{member.name} has been removed as a leader when unlinked")
                    # if not leader, remove role and update db
                    await member.remove_roles(leaderrole)
                    await db.remove_guild_user(smmoid)

                    if len(guildambs) > 0:
                        for amb in guildambs:
                            user = ctx.guild.get_member(int(amb[0]))
                            print(
                                f"{user.name} is not an ambassador because the leader has been unlinked")
                            await user.remove_roles(ambassadorrole)
                            await db.guild_ambassador_update(amb[0], False, 0)
                else:
                    # user is an ambassador

                    print(
                        f"{member.name} is not an ambassador because they unlinked")
                    await member.remove_roles(ambassadorrole)
                    await db.remove_guild_user(smmoid)

        else:
            await ctx.send("This user is not linked.")

    @checks.is_owner()
    @commands.group(aliases=['fv'], hidden=True)
    async def forceverify(self, ctx, member: discord.Member, arg: int):
        try:
            await db.add_new_pleb(arg, str(member.id), None, verified=True)
            await ctx.send(f"{member.name} has been linked to {arg}")
        except:
            await ctx.send(f"You messed something up or {member.name} already started the verification process. bully dyl or something to fix")

    @admin.command()
    @checks.is_owner()
    async def remove(self, ctx, arg: int):
        try:
            await db.remove_user(arg)
        except Exception as e:
            await ctx.send(e)
            return

    @admin.command()
    @checks.is_owner()
    async def ping(ctx):
        start = time.perf_counter()
        message = await ctx.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(content='Pong! {:.2f}ms'.format(duration))

    @admin.command(name='init', description="Sets up bot in server", hidden=True)
    @checks.is_owner()
    async def init(self, ctx):
        guild = ctx.guild
        print(guild.id)

        if await db.server_added(guild.id):
            await ctx.send("Server has already been initialized")
            return
        try:
            await db.add_server(guild.id, guild.name)
            await ctx.send("Server successfully initialized")
            return
        except:
            await ctx.send(f"Something went wrong. Contact <@{dyl}> on Discord for help")
            return

    @admin.command(hidden=True)
    @checks.is_owner()
    async def set_role(self, ctx, *args):

        if not await db.server_added(ctx.guild.id):
            await ctx.send("Please run `^a init` before you run this command!")
            return

        # args should only have len of 1
        if(len(args) != 1):
            await ctx.send("Incorrect Number of Arguments! \n Correct usage: ^ap [role id]")
            return
        roles = ctx.guild.roles
        roleid = args[0]

        # cleanse roleid

        if '@' in roleid:
            roleid = roleid.replace('<', '')
            roleid = roleid.replace('@', '')
            roleid = roleid.replace('>', '')
            roleid = roleid.replace('&', '')

        roleid = int(roleid)
        for role in roles:

            if role.id == roleid:
                await db.add_server_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return

        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return

    @admin.command(aliases=['rb'])
    @checks.is_owner()
    async def rollback(self, ctx):
        await db.rollback()
        await ctx.send("Database Rollback in progress")
        return

    @commands.command(hidden=True)
    @checks.is_owner()
    async def reload(self, ctx, *, cog: str):
        string = f"cogs.{cog}"
        try:
            self.bot.reload_extension(string)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} -{e}')

        else:
            await ctx.send('**SUCCESS!**')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def give(self, ctx, arg: int, members: commands.Greedy[discord.Member]):
        string = ""
        for member in members:
            smmoid = await db.get_smmoid(str(member.id))
            if(await api.pleb_status(smmoid)):  # If they a pleb
                string += f"{member.name}: <https://web.simple-mmo.com/senditem/{smmoid}/{arg}>\n"
            else:
                string += f"{member.name} is not a pleb anymore\n"

        await ctx.send(string)

    @admin.command()
    @checks.is_owner()
    async def test(self, ctx):
        await ctx.send(embed=Embed(description=ctx.author.roles))

    @commands.command(hidden=True)
    @checks.is_owner()
    async def plebcheck(self, ctx=None):
        print("Pleb check starting")
        await log.log(self.bot, "Pleb Check Started", "")
        if(await db.server_added(server)):  # server has been initialized
            pleb_role = await db.pleb_id(server)
        else:
            print("Server has not been added to db")
            return

        if ctx is not None:
            await ctx.send("Pleb check starting...")

        plebs = await db.get_all_plebs()
        guild = self.bot.get_guild(int(server))
        role = guild.get_role(int(pleb_role))
        count = 0
        if ctx is not None:
            await ctx.send(f"There are {len(plebs)} people to check.")
        in_server = 0
        for pleb in plebs:

            count += 1
            if ctx is not None:
                if count % 100 == 0:
                    await ctx.send(f"{count} members checked")

            discid = int(pleb[0])
            smmoid = int(pleb[1])

            user = guild.get_member(discid)  # get user object
            if user is None:
                #print(f'{discid} is not found is the server')
                in_server += 1
                continue

            # If user is muted, do not give them the role
            if user._roles.has(751808682169466962):
                continue

            isPleb = await api.pleb_status(smmoid)

            if isPleb is None:
                print("THE API IS STUPID")

            elif isPleb is True:
                await db.update_status(smmoid, True)  # they are a pleb
                if not user._roles.has(832878414839021598):
                    await user.add_roles(role)  # give user pleb role
                #print(f'{user} with uid: {smmoid} has pleb!')

            elif isPleb is False:  # user is not pleb
                await db.update_status(smmoid, False)  # not a pleb
                if user._roles.has(832878414839021598):
                    await user.remove_roles(role)  # remove pleb role
                #print(f'{user} lost pleb!')

        if ctx is not None:
            await ctx.send(f"Pleb check finished! {in_server} linked members not in this server")

        print("Pleb check finished")

    @commands.command(hidden=True)
    @checks.is_owner()
    async def guildcheck(self, ctx=None):
        print("Guild check starting")
        await log.log(self.bot, "Guild Check Started", "")

        if(ctx is not None):
            await ctx.send("Guild check starting...")

        guild = self.bot.get_guild(int(server))
        leaderrole = guild.get_role(int(await db.leader_id(server)))
        ambassadorrole = guild.get_role(int(await db.ambassador_role(server)))

        ambassadors = await db.all_ambassadors()
        leaders = await db.all_leaders()

        # discid, smmoid, guildid
        for leader in leaders:
            await asyncio.sleep(0.5)
            discid = int(leader[0])
            lsmmoid = int(leader[1])
            guildid = int(leader[2])

            # get any guild ambassadors in that guild
            guildambs = [x for x in ambassadors if x[2] == guildid]

            # check leader in guild
            members = await api.guild_members(guildid)

            # get leader from member list
            try:
                gLeader = [x for x in members if x["position"] == "Leader"]
            except Exception as e:
                print("members:", members)
                # if the guild has been disbanded, remove leader + any guild ambassadors
                if(members["error"] == "guild not found"):
                    user = guild.get_member(discid)
                    if user is not None:
                        print(
                            f"{user.name} is not a leader because guild {guildid} has been deleted.")
                        # if not leader, remove role and update db
                        await user.remove_roles(leaderrole)
                    await db.guild_leader_update(str(discid), False, 0, 0)

                    if len(guildambs) > 0:
                        for amb in guildambs:
                            user = guild.get_member(int(amb[0]))
                            if user is not None:
                                print(
                                    f"{user.name} is not an ambassador because guild {guildid} has been deleted.")
                                await user.remove_roles(ambassadorrole)
                            await db.guild_ambassador_update(amb[0], False, 0)
                    continue

            # if current leader is not one w/ role, remove leader + ambassadors
            if int(gLeader[0]["user_id"]) != lsmmoid:
                user = guild.get_member(discid)
                if user is not None:
                    print(f"{user.name} is not a leader")
                    # if not leader, remove role and update db
                    await user.remove_roles(leaderrole)
                await db.guild_leader_update(str(discid), False, 0, 0)

                if len(guildambs) > 0:
                    for amb in guildambs:
                        user = guild.get_member(int(amb[0]))
                        if user is not None:
                            print(f"{user.name} is not an ambassador")
                            await user.remove_roles(ambassadorrole)
                        await db.guild_ambassador_update(amb[0], False, 0)
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
                            await db.guild_ambassador_update(amb[0], False, 0)

        if(ctx is not None):
            await ctx.send("Guild Check has finished.")
        print("Guild Check has finished")

    @tasks.loop(hours=3)
    async def update_all_plebs(self):
        await self.plebcheck()
        return

    @tasks.loop(hours=4)
    async def update_all_guilds(self):
        await self.guildcheck()
        return

    @update_all_plebs.before_loop
    async def before_pleb(self):
        await self.bot.wait_until_ready()

    @update_all_guilds.before_loop
    async def before_guilds(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=37)
    async def yadda(self):
        print("Yaddayadda")
        channel = self.bot.get_channel(860889861145493524)
        await channel.send("Yadda exposed the tickets")
        return

    @yadda.before_loop
    async def before_yadda(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Admin(bot))
    print("Admin Cog Loaded")
