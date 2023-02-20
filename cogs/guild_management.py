import discord
from discord.ext import commands, tasks
from discord import Embed, app_commands
import api
from util import checks, log, app_checks
import database as db
import logging
import asyncio
import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

server = 444067492013408266


class Guild(commands.GroupCog, name="gm"):
    def __init__(self, bot):
        self.bot = bot
        self.update_all_guilds.start()
        super().__init__()

    @app_checks.is_guild_banned()
    @app_commands.command(description="Gives you the leader role if you're the leader of a guild. You must verify with the bot first.")
    @app_checks.is_verified()
    async def connect(self, interaction: discord.Interaction):
        if interaction.user._roles.has(846649715538133014):
            await interaction.response.send_message("You already have the guild leader role")
            return
        # get smmo id
        smmoid = await db.get_smmoid(interaction.user.id)

        # add to database
        if not await db.is_added(interaction.user.id):
            await db.add_guild_person(interaction.user.id, smmoid)

        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await interaction.response.send_message("You are not in a guild")
            return
        # check if leader of guild
        members = await api.guild_members(guildid)
        for member in members:

            if member["user_id"] == smmoid:
                if member["position"] == "Leader":
                    # if leader, add role and add info to DB
                    leaderid = (await db.server_config(interaction.guild.id)).leader_role
                    await interaction.user.add_roles(interaction.guild.get_role(leaderid))
                    await interaction.response.send_message("You have been verified as a leader.")
                    await db.guild_leader_update(interaction.user.id, True, guildid, smmoid)
                    channel = self.bot.get_channel(758175768496177183)
                    await channel.send(f"Welcome {interaction.user.mention}! Please be sure to read <#758154183164690483> before posting your first advertisement.")
                    return
                else:
                    await interaction.response.send_message(f"You are only a member of your guild. If you want the Ambassador role, your guild leader will need to connect and run `/g aa <ID/@mention>`")
                    return

    @app_checks.is_guild_banned()
    @app_checks.is_verified()
    @app_checks.is_leader()
    @app_commands.command(description="Adds a user as an ambassador for your guild. They must verify with the bot first.")
    async def addambassador(self, interaction: discord.Interaction, member: discord.Member):
       

        # get member smmoid and check if verified
        smmoid = await db.get_smmoid(member.id)

        if await db.is_banned(member.id):
            await interaction.response.send_message(embed=discord.Embed(title="Banned", description=f"{member.mention} has been banned from the guild portion of this bot and cannot be added as an ambassador."))
            return
        if not await db.is_added(member.id):
            await db.add_guild_person(member.id, smmoid)

        guildid, _ = await db.ret_guild_smmoid(interaction.user.id)

        # check if num of ambassadors is more than two
        ambassadors = await db.ambassadors(guildid)

        if len(ambassadors) == 2:
            await interaction.response.send_message(embed=discord.Embed(
                title="Enough Ambassadors",
                description=f"You can only have 2 ambassadors. You can remove your ambassadors using `/g ra <ID/@mention>`. If you don't remember your ambassadors, you can use `/g ca` to list them all."
            ))
            return

        # check if member is in caller's guild

        members = await api.guild_members(guildid)
        for mem in members:
            if mem["user_id"] == smmoid:
                # add ambassador role if all True
                # add player to db
                ambassadorid = (await db.server_config(interaction.guild.id)).ambassador_role
                await member.add_roles(interaction.guild.get_role(ambassadorid))
                await db.guild_ambassador_update(member.id, True, guildid)

                channel = self.bot.get_channel(758175768496177183)
                await channel.send(f"Welcome {member.mention}! Please be sure to read <#758154183164690483> and consult with your guild leader before posting an advertisement.")

                await interaction.response.send_message(f"{member.display_name} is now a Guild Ambassador for your guild")
                return

        await interaction.response.send_message(f"{member.display_name} must be in your guild to add them as an ambassador")
        return

    @app_checks.is_verified()
    @app_checks.is_leader()
    @app_commands.command(description="Removes an ambassador for your guild.")
    async def removeambassador(self, interaction: discord.Interaction, member: discord.Member):
        # check if member is an ambassador
        val, guildid = await db.is_ambassador(member.id)

        if val:
            # check if member ambassador for guild leader
            lguildid, _ = await db.ret_guild_smmoid(interaction.user.id)
            if lguildid == guildid:
                ambassadorid = (await db.server_config(interaction.guild.id)).ambassador_role
                await member.remove_roles(interaction.guild.get_role(ambassadorid))
                await db.guild_ambassador_update(member.id, False, guildid)
                await interaction.response.send_message(f"{member.mention} has been removed as an ambassador for your guild")
                return

            else:
                await interaction.response.send_message(f"{member.display_name} is not an ambassador for your guild")
                return

        else:
            await interaction.response.send_message(f"{member.display_name} is not an ambassador")
            return

    @app_checks.is_verified()
    @app_checks.is_leader()
    @app_commands.command(description="Lists all current ambassadors for your guild.")
    async def currentambassadors(self, interaction: discord.Interaction):
        lguild, _ = await db.ret_guild_smmoid(interaction.user.id)
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

        await interaction.response.send_message(embed=embed)

    @app_checks.is_owner()
    @app_commands.command()
    async def leaderrole(self, interaction: discord.Interaction, role: discord.Role):
        if not await db.server_added(interaction.guild.id):
            await interaction.response.send_message(f"Please run `/a init` before you run this command!")
            return

        await db.add_leader_role(interaction.guild.id, role.id)
        await interaction.response.send_message("Role successfully added!")
        return

        

    @app_checks.is_owner()
    @app_commands.command()
    async def ambrole(self, interaction: discord.Interaction, role: discord.Role):
        if not await db.server_added(interaction.guild.id):
            await interaction.response.send_message("Please run `^a init` before you run this command!")
            return

        await db.add_ambassador_role(interaction.guild.id, role.id)
        await interaction.response.send_message("Role successfully added!")
        return


    @commands.command()
    @checks.is_owner()
    async def guildcheck(self, interaction: discord.Interaction=None):

        await log.log(self.bot, "Guild Check Started", "")

        if(interaction is not None):
            await interaction.response.send_message("Guild check starting...")

        guild = self.bot.get_guild(int(server))
        if guild is None:
            return
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
            if members is None:
                logging.error("API call guild_members failed")
                continue

            # get leader from member list
            try:
                gLeader = [x for x in members if x["position"] == "Leader"]
            except Exception as e:
                # if the guild has been disbanded, remove leader + any guild ambassadors
                if(members["error"] == "guild not found"):
                    user = guild.get_member(discid)
                    if user is not None:
                        logging.info(
                            f"{user.name} is not a leader because guild {guildid} has been deleted.")
                        # if not leader, remove role and update db
                        await user.remove_roles(leaderrole)
                    await db.guild_leader_update(discid, False, 0, 0)

                    if len(guildambs) > 0:
                        for amb in guildambs:
                            user = guild.get_member(amb.discid)
                            if user is not None:
                                logging.info(
                                    f"{user.name} is not an ambassador because guild {guildid} has been deleted.")
                                await user.remove_roles(ambassadorrole)
                            await db.guild_ambassador_update(amb.discid, False, 0)
                    continue

            # if current leader is not one w/ role, remove leader + ambassadors

            if len(gLeader) > 0 and int(gLeader[0]["user_id"]) != lsmmoid:
                user = guild.get_member(discid)
                if user is not None:
                    logging.info(f"{user.name} is not a leader")
                    # if not leader, remove role and update db
                    await user.remove_roles(leaderrole)
                await db.guild_leader_update(discid, False, 0, 0)

                if len(guildambs) > 0:
                    for amb in guildambs:
                        user = guild.get_member(int(amb.discid))
                        if user is not None:
                            logging.info(f"{user.name} is not an ambassador")
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
                                logging.info(f"{user.name} is not an ambassador")

                                await user.remove_roles(ambassadorrole)
                            await db.guild_ambassador_update(amb[0], False, 0)

        if(interaction is not None):
            await interaction.response.send_message("Guild Check has finished.")

    @tasks.loop(hours=4, reconnect=True)
    async def update_all_guilds(self):
        await self.guildcheck(None)
        return

    @update_all_guilds.before_loop
    async def before_guilds(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    if config.main_acct:
        await bot.add_cog(Guild(bot))
        # await add_cog(cog, /, *, override=False, guild=..., guilds=...)
        logger.info("Guild management Cog Loaded")
