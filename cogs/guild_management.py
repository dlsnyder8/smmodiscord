import discord
from discord.ext import commands, tasks
import api
from util import checks, log
import database as db
import logging
import asyncio
import config

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

server = 444067492013408266


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_all_guilds.start()

    @checks.is_verified()
    @checks.in_main()
    @commands.group(aliases=['g'], hidden=True)
    async def guild(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @guild.command(aliases=['frl'], hidden=True)
    @checks.is_owner()
    async def forceremoveleader(self, ctx, dmem: discord.Member):
        pass

    # @guild.command(aliases=['fc'], hidden=True)
    # @checks.is_owner()
    # async def forceconnect(self, ctx, dmem: discord.Member):
    #     # get smmo id
    #     if(await db.islinked(dmem.id)):
    #         smmoid = await db.get_smmoid(dmem.id)
    #     else:
    #         await ctx.send("They are not linked")
    #         return

    #     # add to database
    #     if not await db.is_added(dmem.id):
    #         await db.add_guild_person(dmem.id, smmoid)

    #     # get guild from profile (get_all())
    #     profile = await api.get_all(smmoid)
    #     try:
    #         guildid = profile["guild"]["id"]
    #     except KeyError as e:
    #         await ctx.send("They are not in a guild")
    #         return
    #     # check if leader of guild
    #     members = await api.guild_members(guildid)
    #     for member in members:

    #         if member["user_id"] == smmoid:
    #             if member["position"] == "Leader":
    #                 # if leader, add role and add info to DB
    #                 leaderid = await db.leader_id(ctx.guild.id)
    #                 await dmem.add_roles(ctx.guild.get_role(int(leaderid)))
    #                 await ctx.send("They have been verified as a leader")
    #                 await db.guild_leader_update(dmem.id, True, guildid, smmoid)
    #                 return
    #             else:
    #                 await ctx.send(f"They are only a member of your guild. If they want the Ambassador role, their guild leader will need to connect and run `{ctx.prefix}g aa <ID/@mention>`")
    #                 return

    @checks.is_guild_banned()
    @guild.command(aliases=['c'], usage="", description="Gives you the leader role if you're the leader of a guild. You must verify with the bot first.")
    @checks.is_verified()
    async def connect(self, ctx):
        # get smmo id
        smmoid = await db.get_smmoid(ctx.author.id)

        # add to database
        if not await db.is_added(ctx.author.id):
            await db.add_guild_person(ctx.author.id, smmoid)

        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("You are not in a guild")
            return
        # check if leader of guild
        members = await api.guild_members(guildid)
        for member in members:

            if member["user_id"] == smmoid:
                if member["position"] == "Leader":
                    # if leader, add role and add info to DB
                    leaderid = (await db.server_config(ctx.guild.id)).leader_role
                    await ctx.author.add_roles(ctx.guild.get_role(leaderid))
                    await ctx.send("You have been verified as a leader.")
                    await db.guild_leader_update(ctx.author.id, True, guildid, smmoid)
                    channel = self.bot.get_channel(758175768496177183)
                    await channel.send(f"Welcome {ctx.author.mention}! Please be sure to read <#758154183164690483> before posting your first advertisement.")
                    return
                else:
                    await ctx.send(f"You are only a member of your guild. If you want the Ambassador role, your guild leader will need to connect and run `{ctx.prefix}g aa <ID/@mention>`")
                    return

    @checks.is_guild_banned()
    @checks.is_leader()
    @guild.command(aliases=['aa'], usage="<ID/@Mention>", description="Adds a user as an ambassador for your guild. They must verify with the bot first.")
    async def addambassador(self, ctx, *, member: discord.Member):

        # get member smmoid and check if verified
        smmoid = await db.get_smmoid(member.id)

        if smmoid is None:
            embed = discord.Embed(
                title="Not Verified",
                description=f"{member.mention} is not verified. They need to run `{ctx.prefix}verify <smmoid>` to start the process",
                color=0x00ff00)

            await ctx.send(
                embed=embed
            )
            return

        if await db.is_banned(member.id):
            await ctx.send(embed=discord.Embed(title="Banned", description=f"{member.mention} has been banned from the guild portion of this bot and cannot be added as an ambassador."))
            return
        if not await db.is_added(member.id):
            await db.add_guild_person(member.id, smmoid)

        guildid, _ = await db.ret_guild_smmoid(ctx.author.id)

        # check if num of ambassadors is more than two
        ambassadors = await db.ambassadors(guildid)

        if len(ambassadors) == 2:
            await ctx.send(embed=discord.Embed(
                title="Enough Ambassadors",
                description=f"You can only have 2 ambassadors. You can remove your ambassadors using `{ctx.prefix}g ra <ID/@mention>`. If you don't remember your ambassadors, you can use `{ctx.prefix}g ca` to list them all."
            ))
            return

        # check if member is in caller's guild

        members = await api.guild_members(guildid)
        for mem in members:
            if mem["user_id"] == smmoid:
                # add ambassador role if all True
                # add player to db
                ambassadorid = (await db.server_config(ctx.guild.id)).ambassador_role
                await member.add_roles(ctx.guild.get_role(ambassadorid))
                await db.guild_ambassador_update(member.id, True, guildid)

                channel = self.bot.get_channel(758175768496177183)
                await channel.send(f"Welcome {member.mention}! Please be sure to read <#758154183164690483> and consult with your guild leader before posting an advertisement.")

                await ctx.send(f"{member.display_name} is now a Guild Ambassador for your guild")
                return

        await ctx.send(f"{member.display_name} must be in your guild to add them as an ambassador")
        return

    @checks.is_verified()
    @checks.is_leader()
    @guild.command(aliases=['ra'], usage="<ID/@Mention>", description="Removes an ambassador for your guild.")
    async def removeambassador(self, ctx, *, member: discord.Member):
        # check if member is an ambassador
        val, guildid = await db.is_ambassador(member.id)

        if val:
            # check if member ambassador for guild leader
            lguildid, _ = await db.ret_guild_smmoid(ctx.author.id)
            if lguildid == guildid:
                ambassadorid = (await db.server_config(ctx.guild.id)).ambassador_role
                await member.remove_roles(ctx.guild.get_role(ambassadorid))
                await db.guild_ambassador_update(member.id, False, guildid)
                await ctx.send(f"{member.mention} has been removed as an ambassador for your guild")
                return

            else:
                await ctx.send(f"{member.display_name} is not an ambassador for your guild")
                return

        else:
            await ctx.send(f"{member.display_name} is not an ambassador")
            return

    @checks.is_verified()
    @checks.is_leader()
    @guild.command(aliases=['ca', 'ambassadors'], usage="", description="Lists all current ambassadors for your guild.")
    async def currentambassadors(self, ctx):
        lguild, _ = await db.ret_guild_smmoid(ctx.author.id)
        ambassadors = await db.ambassadors(lguild)

        embed = discord.Embed(
            title="Ambassadors",
            color=0x0000FF
        )
        x = 1
        for ambassador in ambassadors:
            embed.add_field(
                name=f"Ambassador {x}:", value=f"<@{ambassador.discid}>")
            x += 1

        await ctx.send(embed=embed)

    @checks.is_owner()
    @guild.command(hidden=True)
    async def leaderrole(self, ctx, *args):
        if not await db.server_added(ctx.guild.id):
            await ctx.send(f"Please run `{ctx.prefix}a init` before you run this command!")
            return

        # args should only have len of 1
        if(len(args) != 1):
            await ctx.send(f"Incorrect Number of Arguments! \n Correct usage: {ctx.prefix}ap [role id]")
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
                await db.add_leader_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return

        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return

    @checks.is_owner()
    @guild.command(hidden=True)
    async def ambrole(self, ctx, *args):
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
                await db.add_ambassador_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return

        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return

    @commands.command(hidden=True)
    @checks.is_owner()
    async def guildcheck(self, ctx=None):

        await log.log(self.bot, "Guild Check Started", "")

        if(ctx is not None):
            await ctx.send("Guild check starting...")

        guild = self.bot.get_guild(int(server))
        config = await db.server_config(server)
        leaderrole = guild.get_role(config.leader_role)
        ambassadorrole = guild.get_role(config.ambassador_role)

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
                    await db.guild_leader_update(discid, False, 0, 0)

                    if len(guildambs) > 0:
                        for amb in guildambs:
                            user = guild.get_member(amb.discid)
                            if user is not None:
                                print(
                                    f"{user.name} is not an ambassador because guild {guildid} has been deleted.")
                                await user.remove_roles(ambassadorrole)
                            await db.guild_ambassador_update(amb.discid, False, 0)
                    continue

            # if current leader is not one w/ role, remove leader + ambassadors

            if len(gLeader) > 0 and int(gLeader[0]["user_id"]) != lsmmoid:
                user = guild.get_member(discid)
                if user is not None:
                    print(f"{user.name} is not a leader")
                    # if not leader, remove role and update db
                    await user.remove_roles(leaderrole)
                await db.guild_leader_update(discid, False, 0, 0)

                if len(guildambs) > 0:
                    for amb in guildambs:
                        user = guild.get_member(int(amb.discid))
                        if user is not None:
                            print(f"{user.name} is not an ambassador")
                            await user.remove_roles(ambassadorrole)
                        await db.guild_ambassador_update(amb.discid, False, 0)
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

    @tasks.loop(hours=4, reconnect=True)
    async def update_all_guilds(self):
        await self.guildcheck()
        return

    @update_all_guilds.before_loop
    async def before_guilds(self):
        await self.bot.wait_until_ready()


def setup(bot):
    if config.main_acct:
        bot.add_cog(Guild(bot))
        print("Guild Cog Loaded")
