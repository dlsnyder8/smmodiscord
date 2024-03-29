import discord
from discord.ext import commands, tasks
from discord import Embed, app_commands
from discord.ext.commands import Context
from util import checks, log, app_checks
import api
import database as db
import logging
import string
import random
from util.cooldowns import BucketType, custom_is_me
from datetime import datetime, timezone



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dyl = 332314562575597579


class Guilds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_member_check.start()
        
    @app_checks.server_configured()
    @app_commands.command(description="Displays an embed with details on how to verify")
    async def verification_info(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=Embed(title="Verification Process",
            description=f"1) Please find your SMMO ID by navigating to your profile on web app and getting the 4-6 digits in the url or if on mobile scrolling to the bottom of your stats page" \
                        "2) Run `/verify SMMOID`"\
                        "3) Add the verification key to your motto, then run `/verify SMMOID` again"))

    @app_checks.server_configured()
    @app_checks.is_verified()
    @app_commands.command(description="Show your profile")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        smmoid = await db.get_smmoid(interaction.user.id)
        # get data from profile_data in db. If not exists, call API
        # If profile data is None, call api
        profile_data, timestamp = await db.get_data(smmoid)
        if profile_data is None:
            profile_data = await api.get_all(smmoid)
        elif (datetime.now(timezone.utc) - timestamp).total_seconds() > 3600:
            profile_data = await api.get_all(smmoid)
            timestamp = datetime.now(timezone.utc)
        

        # Sample Profile_Data
        #  {"hp": 310255, "id": 385801, "def": 5, "dex": 7350, "exp": 96283469640, "str": 115800, "gold": 4425055851, "name": "retired dyl", "guild": {"id": 482, "name": "Still Friendly"}, "level": 62042, "motto": "Retired moderator. If you ask me for moderator help I am guaranteed to be unhelpful", "steps": 39775, "avatar": "/img/sprites/events/halloween-21/chocolate-frog-avatar.png", "banned": 0, "max_hp": 310255, "safeMode": 1, "bonus_def": 8595, "bonus_dex": 0, "bonus_str": 4125, "npc_kills": 21412, "background": 122, "boss_kills": 223, "membership": 1, "reputation": 193, "user_kills": 33100, "chests_opened": 143648, "creation_date": "2020-07-31T19:11:47.000000Z", "last_activity": 1700455799, "market_trades": 18806, "profile_number": "8008", "quests_complete": 114, "tasks_completed": 343, "current_location": {"id": 1, "name": "Simpletopia"}, "dailies_unlocked": 800, "quests_performed": 1895053, "bounties_completed": 2}
        # Build embed from profile data
        
        # Add timestamp to footer
        embed = Embed(title=f"{profile_data['name']}'s Profile", timestamp=timestamp)
        embed.set_footer(text=f"Data Gathered at")
        embed.add_field(name="Level", value=profile_data['level'], inline=True)
        embed.add_field(name="Guild", value=profile_data['guild']['name'], inline=True)
        embed.add_field(name="Steps", value=profile_data['steps'], inline=True)
        embed.add_field(name="Gold", value=profile_data['gold'], inline=True)
        embed.add_field(name="Reputation", value=profile_data['reputation'], inline=True)
        embed.add_field(name="NPC Kills", value=profile_data['npc_kills'], inline=True)
        embed.add_field(name="User Kills", value=profile_data['user_kills'], inline=True)
        embed.add_field(name="Boss Kills", value=profile_data['boss_kills'], inline=True)
        embed.add_field(name="Chests Opened", value=profile_data['chests_opened'], inline=True)
        embed.add_field(name="Quests Completed", value=profile_data['quests_complete'], inline=True)
        embed.add_field(name="Tasks Completed", value=profile_data['tasks_completed'], inline=True)
        embed.add_field(name="Bounties Completed", value=profile_data['bounties_completed'], inline=True)
        embed.add_field(name="Market Trades", value=profile_data['market_trades'], inline=True)
        embed.add_field(name="Quests Performed", value=profile_data['quests_performed'], inline=True)
        embed.add_field(name="Dailies Unlocked", value=profile_data['dailies_unlocked'], inline=True)
        
        creation_date = datetime.strptime(profile_data['creation_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_creation_date = creation_date.strftime("%B %d, %Y")
        embed.add_field(name="Creation Date", value=formatted_creation_date, inline=True)

        last_activity_unix = profile_data['last_activity']
        last_activity_datetime = datetime.fromtimestamp(last_activity_unix)

        embed.add_field(name="Last Activity (UTC)", value=last_activity_datetime, inline=True)
        
        await interaction.followup.send(embed=embed)
        
        

    @app_checks.server_configured()
    @app_commands.command(description="Connects your Discord account with your SMMO account")
    async def verify(self, interaction: discord.Interaction, smmoid: int):
        # check if verified
        if(await db.is_verified(smmoid)):
            await interaction.response.send_message("Someone else has already linked to this SimpleMMO Account. It could be you, or you could have the wrong ID. ")
            return

        if(await db.islinked(interaction.user.id) is True):
            await interaction.response.send_message(embed=Embed(title="Already Linked", description=f"Your account is already linked to an SMMO account. If you need to remove this, use the `/unlink` command"))
            return

        # check if has verification key in db
        key = await db.verif_key(smmoid, interaction.user.id)
        if(key is not None):

            profile = await api.get_all(smmoid)
            try:
                motto = profile['motto']
            except KeyError:
                await interaction.response.send_message(f"A motto cannot be found for this account. This usually means you are trying to link to a deleted account. Ask someone for help to find your SMMO ID")
                return

            if motto is None:
                await interaction.response.send_message(f'Something went wrong. Please contact <@{dyl}> on Discord for help')
                return

            if(key in motto):
                await db.update_verified(smmoid, True)
                await interaction.response.send_message("You are now verified. You can remove the verification key from your motto.")
                data = await db.server_config(interaction.guild.id)
                if data.guild_role is not None:
                    await interaction.followup.send(f"If you're in the guild, please run `/join` to be granted access to guild channels.")
                return
            await interaction.response.send_message(f"""Verification Failed. You are trying to connect your account to **{profile['name']}**. Your verification key is: `{key}` \nPlease add this to your motto and run `/verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>""")
            return
        else:
            # key in DB, but someone else tried to add it. Generate new key
            if(await db.key_init(smmoid) is not None):
                letters = string.ascii_letters
                key = "SMMO-" + ''.join(random.choice(letters)
                                        for i in range(8))
                await db.update_pleb(smmoid, interaction.user.id, key)
                await interaction.response.send_message(f"""Your new verification key is: `{key}` \nPlease add this to your motto and run `/verify {smmoid}` again! \n<https://web.simple-mmo.com/changemotto>""")
                return

            # no key in db, generate and add
            # generate verification key, add to db, tell user to add to profile and run command again
            else:
                letters = string.ascii_letters
                key = "SMMO-" + ''.join(random.choice(letters)
                                        for i in range(8))
                await db.add_new_pleb(smmoid, interaction.user.id, key)
                await interaction.response.send_message(f'Your verification key is: `{key}` \nPlease add this to your motto and run `/verify {smmoid}` again! \n<https://web.simple-mmo.com/changemotto>')
                return


    @app_checks.is_verified()
    @app_commands.command(description="Give yourself the guild role if you're in this server's guild")
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,60),key=BucketType.Member)
    @app_checks.server_configured()
    async def join(self, interaction: discord.Interaction):
        await interaction.response.defer()
        config = await db.server_config(interaction.guild.id)
        if config.guild_role is None:
            await interaction.followup.send("The guild role for this server has not been set up. Please contact an administrator on this server", ephemeral=True)
            return
        if interaction.user._roles.has(config.guild_role):

            await interaction.followup.send(f"You've already been granted the {config.guild_name} role :)", ephemeral=True)
            return

        smmoid = await db.get_smmoid(interaction.user.id)

        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await interaction.followup.send("You are not in a guild", ephemeral=True)
            return

        # if user is in a fly guild....
        if guildid in config.guilds or interaction.user.id == dyl:
            roles_given = ""

            # add guild role
            try:
                await interaction.user.add_roles(interaction.guild.get_role(config.guild_role))
            except discord.Forbidden:
                await interaction.followup.send("I am unable to add roles to this user because either I do not have proper permissions, or my role is not high enough.")
                return
            roles_given += f"<@&{config.guild_role}>"

            if config.non_guild_role is not None:
                try:
                    await interaction.user.remove_roles(interaction.guild.get_role(config.non_guild_role))
                except discord.Forbidden:
                    pass
            if config.log_channel is not None:
                await log.server_log(self.bot, interaction.guild.id, title="User has joined the guild", desc=f"**Roles given to** {interaction.user.mention}\n{roles_given}", id=interaction.user.id)
            channel = self.bot.get_channel(config.welcome_channel)
            if interaction.user.id != dyl:
                try:
                    await channel.send(f"Welcome {interaction.user.mention} to the {config.guild_name} guild!")
                except discord.HTTPException:
                    pass
                except AttributeError:
                    await interaction.followup.send(f'Welcome to the guild!')
                    message = await interaction.followup.send(f"This message can be moved to another channel by using `/config update_welcome #channel`")
                    await message.delete(delay=5)

        else:
            await interaction.followup.send("You are not in the guild. If you think this is a mistake, try contacting your guild leader")
            return

    @app_commands.command(description="Checks to see who has the guild role, but is not in the guild or has not linked")
    @app_checks.is_admin()
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,600),key=BucketType.Guild)
    async def softcheck(self, interaction: discord.Interaction, guildrole: discord.Role = None):
        await interaction.response.defer(thinking=True)
        server = await db.ServerInfo(interaction.guild.id)
        guilds = server.guilds
        allmembers = []
        for x in guilds:
            allmembers.extend([x['user_id'] for x in (await api.guild_members(x, server.api_token))])

        guild = self.bot.get_guild(server.serverid)
        if guild is None:
            return

        if guildrole is None:
            guild_role = guild.get_role(server.guild_role)
        else:
            guild_role = guildrole

        if guild_role is None:
            embed = discord.Embed(title="Guild Member Check Failed",
                                    description="It appears that my config is wrong and I cannot find the guild role")
            await interaction.followup.send(embed=embed)
            return

        removed = []
        for member in guild_role.members:
            if await db.islinked(member.id):
                smmoid = await db.get_smmoid(member.id)
                if smmoid not in allmembers:
                    removed.append(f"{member.mention}")
            else:
                removed.append(f'{member.mention}')

        if len(removed) > 0:
            embed = Embed(
                title="Users not in guild"
            )
            splitUsers = [removed[i:i+33]
                            for i in range(0, len(removed), 33)]

            for split in splitUsers:
                embed.add_field(name="Users", value=' '.join(split))
            await interaction.followup.send(embed=embed)

        else:
            await interaction.followup.send("Everyone is linked and in the guild")

    @tasks.loop(hours=4, reconnect=True)
    async def guild_member_check(self):
        ignored_servers = [710258284661178418]
        await log.log(self.bot, "Guild Member Check Started", " ")

        allservers = await db.all_servers()
        filtered = [
            x for x in allservers if x.guild_role is not None and x.guilds is not None]
        

        for server in filtered:
            if server.serverid in ignored_servers:
                continue

            guilds = server.guilds

            allmembers = []

            for x in guilds:
                allmembers.extend([x['user_id'] for x in (await api.guild_members(x, server.api_token))])

            if allmembers == []:
                continue
            
            guild = self.bot.get_guild(server.serverid)
            if guild is None:
                continue

            await log.log(self.bot, "Guild Check", f'Checking server {guild.name} ')

            guild_role = guild.get_role(server.guild_role)

            non_guild_role = guild.get_role(server.non_guild_role)

            if guild_role is None:
                log.server_log(self.bot, server.serverid, title="Guild Member Check Failed",
                               desc="It appears that my config is wrong and I cannot find the guild role")
                continue

            removed = []
            for member in guild_role.members:
                if await db.islinked(member.id):
                    smmoid = await db.get_smmoid(member.id)
                    if smmoid not in allmembers:
                        try:
                            await member.remove_roles(guild_role, reason="User has left the guild")
                            removed.append(f"{member.mention}")
                        except discord.Forbidden:
                            removed.append(f"{member.mention} (I do not have permission to remove the guild role")
                        if non_guild_role is not None:
                            try:
                                await member.add_roles(non_guild_role)
                            except discord.Forbidden:
                                pass
                else:
                    try:
                        await member.remove_roles(guild_role, reason="User has not linked")
                        removed.append(f'{member.mention}')
                    except discord.Forbidden:
                        removed.append(f"{member.mention} (I do not have permission to remove the guild role")
                    if non_guild_role is not None:
                        try:
                            await member.add_roles(non_guild_role)
                        except discord.Forbidden:
                            pass
            if len(removed) > 0:
                embed = Embed(
                    title="Users with the guild role removed"
                )
                splitUsers = [removed[i:i+33]
                              for i in range(0, len(removed), 33)]

                for split in splitUsers:
                    embed.add_field(name="Users", value=' '.join(split))

                await log.server_log_embed(self.bot, server.serverid, embed)
                embed.title = f"Users with guild role removed for id: {server.serverid}"
                await log.embedlog(self.bot, embed)

    @guild_member_check.before_loop
    async def before_guild_member_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Guilds(bot))
    logger.info("Guilds Cog Loaded")
