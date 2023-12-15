import discord
from discord import Embed, app_commands
from discord.ext import commands, tasks
import logging, csv, os, uuid
import api
import database as db
from util import checks, log, app_checks
from util.cooldowns import BucketType, custom_is_me


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Event(commands.GroupCog, name="event"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.event_types = ["step", "pvp", "npc", "level"]
        self.stat_update.start()
        super().__init__()

    # @app_commands.command(aliases=['e'], hidden=True)
    # @checks.server_configured()
    # async def event(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         pass

    @app_commands.command()
    @app_checks.is_admin()
    @app_commands.choices(event_type=[
        app_commands.Choice(name='Stepping Event',value='step'),
        app_commands.Choice(name='PvP Event',value='pvp'),
        app_commands.Choice(name='NPC Slaughter Event',value='npc'),
        app_commands.Choice(name='Leveling Event',value='level')
    ])
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,120),key=BucketType.Guild)
    async def create(self, interaction: discord.Interaction, name: str, event_type: app_commands.Choice[str]):
        # if eventtype not in self.event_types:
        #     await ctx.send(embed=Embed(title="Invalid event type", description="Events must be one of the following:\n`step`,`level`,`npc`,`pvp`"))
        #     return

        try:
            guildrole = await interaction.guild.create_role(name=name)
            event_id = await db.create_event(interaction.guild.id, name, event_type.value, guildrole.id)
            await interaction.response.send_message(f"Event has been created with id {event_id}. Please remember this ID. {guildrole.mention} has been created for this event")

        except Exception as e:
            await interaction.response.send_message(embed=Embed(title="Error", description=e))
            raise e

    @app_commands.command()
    @app_checks.is_admin()
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,120),key=BucketType.Guild)
    async def start(self, interaction: discord.Interaction, eventid:int):
        await interaction.response.send_message("Gathering starting stats. This may take a minute, please wait for confirmation.")
        stat_convert = {"pvp": "user_kills", "step": "steps",
                        "npc": "npc_kills", "level": "level"}
        valid = await db.valid_event(eventid, interaction.guild.id)
        if valid is False:
            await interaction.followup.send("Invalid event ID")
            return 
        elif valid.is_started:
            await interaction.followup.send("This event has already started. You do not need to start it again")
            return
        try:
            await db.start_event(eventid, interaction.guild.id)
            eventinfo = await db.event_info(eventid, interaction.guild.id)

            members = await db.get_participants(eventid)
            if members is None:
                await interaction.followup.send("That is not a valid ID")
                return
            if len(members) == 0:
                await interaction.followup.send("There are no participants for that event. It has been ended automatically")
                await db.end_event(eventid, interaction.guild.id)
                return
            elif members is None:
                await interaction.followup.send("The event ID might be incorrect or something brokey")
                return

        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=e))
            raise e

        for member in members:

            smmoid = await db.get_smmoid(member.discordid)
            profile = await api.get_all(smmoid)
            info = profile[stat_convert[eventinfo.type]]

            await db.update_start_stat(eventid, member.discordid, info)

        await interaction.followup.send(f"Event {eventid} has started!")

    @app_commands.command()
    @app_checks.is_admin()
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,120),key=BucketType.Guild)
    async def end(self, interaction: discord.Interaction, eventid: int):
        await interaction.response.send_message("Gathering final stats. Please be patient.")
        try:
            eventinfo = await db.event_info(eventid, interaction.guild.id)
            if eventinfo is None:
                await interaction.followup.send("That event id is not valid")
                return
            elif eventinfo.is_ended:
                await interaction.followup.send("That event has already been ended")
                return

            await self.stat_update(interaction.guild.id)
            await db.end_event(eventid, interaction.guild.id)
            await interaction.followup.send(f"Event {eventid} has concluded. Make sure to clean up the event with `/event cleanup {eventid}`")
            
        except Exception as e:
            await interaction.followup.send(embed=Embed(title="Error", description=e))
            raise e

    @app_commands.command()
    @app_checks.is_admin()
    async def cleanup(self, interaction: discord.Interaction, eventid: int):
        try:
            eventinfo = await db.event_info(eventid, interaction.guild.id)
            
            if eventinfo is None:
                await interaction.response.send_message(f"To see a list of events to cleanup, run `/event finished`")
                return
            if eventinfo.is_ended is False:
                await interaction.response.send_message(f"You can't cleanup an active event!\n\nIf you want to end an event, run `/event end`")
                return
            guildrole = interaction.guild.get_role(eventinfo.event_role)
            await db.cleanup_event(eventid, interaction.guild.id)
            await guildrole.delete(reason="Event ended")
            await interaction.response.send_message("Cleanup Concluded")

        except AttributeError:
            await interaction.response.send_message("This event has already been cleaned up")
        except Exception as e:
            await interaction.response.send_message(embed=Embed(title="Error", description=e))
            raise e

    @app_commands.command()
    @app_checks.is_admin()
    async def results(self, interaction:discord.Interaction, eventid: int):
        valid = await db.valid_event(eventid, interaction.guild_id)
        if valid is False:
            await interaction.response.send_message("Invalid event ID")
            return

        translation = {"pvp": "PvP Kills", "step": "Steps",
                       "npc": "NPC Kills", "level": "Levels"}

        participants = await db.get_participants(eventid)
        if len(participants) == 0 or participants is None:
            await interaction.response.send_message("That doesn't appear to be a valid event id")
            return
        eventinfo = valid # await db.event_info(eventid, ctx.guild.id)
        print(eventinfo)

        participants.sort(
            reverse=True, key=lambda x: x.current_stat-x.starting_stat)

        embed = Embed(title=f"Results for {eventinfo.name}")
        string = ""
        i = 1
        last = 1
        # async with ctx.typing():
        embeds = []
        await interaction.response.defer(thinking=True)
        for particpant in participants:
            string += f"**{i}.** <@{particpant.discordid}> - {particpant.current_stat-particpant.starting_stat} {translation[eventinfo.type]}\n"
            if i % 20 == 0:
                last = i
                embed.add_field(name=f'Users {i-20} - {i}', value=string)
                string = ''

            if len(embed) > 5500:
                embeds.append(embed)
                embed = Embed(title=f"Results for {eventinfo.name}")

            i += 1
        embeds.append(embed)
        if len(string) > 0:
            embed.add_field(name=f'Users {last} - {i-1}', value=string)
            await interaction.followup.send(embeds=embeds)

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.server_configured()
    async def guild_only(self, interaction:discord.Interaction, eventid: int, boolean: bool):
        try:
            await db.event_guild_only(eventid, interaction.guild.id, boolean)
            if boolean:
                await interaction.response.send_message(f"Event {eventid} has been set to `guild only`")
            else:
                await interaction.response.send_message(f"Event {eventid} has been set to `public`")
        except Exception as e:
            await interaction.response.send_message(embed=Embed(title="Error", description=e))
            raise e

    @app_commands.command()
    @app_checks.is_verified()
    async def stat(self, interaction:discord.Interaction, eventid:int=None):

        translation = {"pvp": "PvP Kills", "step": "Steps",
                       "npc": "NPC Kills", "level": "Levels"}

        active_events = await db.active_events(interaction.guild.id)
        if len(active_events) == 1:
            eventid = active_events[0].id

            progress = await db.participant_progress(eventid, interaction.user.id)
            eventinfo = await db.event_info(eventid, interaction.guild.id)
            if progress is None or eventinfo is None:
                await interaction.response.send_message("You are not particpating in the current event")
                return

        elif len(active_events) > 1:
            if eventid is None:
                await interaction.response.send_message(f"Please specify an event id as there are multiple active events.")
                return
            else:
                progress = await db.participant_progress(eventid, interaction.user.id)
                eventinfo = await db.event_info(eventid, interaction.guild.id)
                if progress is None:
                    await interaction.response.send_message("You are not a participant in that event or that event does not exist.")
                    return
                elif eventinfo is None:
                    await interaction.response.send_message("That event does not exist or is not being hosted in this server.")

        else:
            await interaction.response.send_message("There are no active events right now. Please wait for someone to start one.")
            return

        embed = Embed(title=f"Your {translation[eventinfo.type]} for the **{eventinfo.name}** Event",
                      description=f"**Starting amount:** {progress[0]}\n**Last Updated Amount:** {progress[1]}\n**Difference:** {progress[2]}")
        embed = embed.set_footer(text=f"Last Updated: {progress[3]} UTC")
        await interaction.response.send_message(embed=embed)
        
        
    @app_checks.is_admin()
    @app_commands.command(name="export")
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,120),key=BucketType.Guild)
    async def export(self, interaction:discord.Interaction, eventid:int):
        await interaction.response.defer(thinking=True)
        
        valid = await db.valid_event(eventid, interaction.guild_id)
        if valid is False:
            await interaction.followup.send("Invalid event ID")
            return
        
        participants = await db.get_participants(eventid)
        if len(participants) == 0 or participants is None:
            await interaction.followup.send("That doesn't appear to be a valid event id")
            return

        participants.sort(
            reverse=True, key=lambda x: x.current_stat-x.starting_stat)
        
        # create random file name
        random_filename = str(uuid.uuid4())
        with open(f'{random_filename}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['smmoid', 'discordid', 'starting_stat', 'current_stat', 'last_updated'])
            for member in participants:
                data = [member.id, member.discordid, member.starting_stat, member.current_stat, member.last_updated ]
                writer.writerow(data)
        await interaction.followup.send("Here are the guild stats", file=discord.File(f'{random_filename}.csv'))
        os.remove(f'{random_filename}.csv')

    @app_commands.command()
    @app_checks.is_admin()
    async def participants(self, interaction:discord.Interaction, eventid: int=None):

        if eventid is None:
            await interaction.response.send_message("You must specify an event ID.")
            return

        valid = await db.valid_event(eventid, interaction.guild.id)
        if valid is False:
            await interaction.response.send_message("Invalid event ID")
            return

        participants = await db.get_participants(eventid)
        if participants is None:
            await interaction.response.send_message(embed=Embed(
                title="Not a valid eventid",
                description=f"To see a list of events for this server, you can run the `/joinable` command"
            ))
            return
        await interaction.response.send_message(embed=Embed(title="Number of Participants", description=f"There are {len(participants)} people particpating in this event."))
        return

    @app_commands.command()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def join(self, interaction:discord.Interaction, eventid: int=None):
        active_events = await db.available_events(interaction.guild.id)
        eventinfo = await db.event_info(eventid, interaction.guild.id)
        tempid = eventid

        # If they've joined it before, error
        if eventid is not None and await db.has_joined(eventid, interaction.user.id):
            await interaction.response.send_message(f"You have already joined event {eventinfo.name}")
            return

        # First, check event they want to join. If event exists...
        if eventinfo is not None:

            # check if event is already ended
            if eventinfo.is_ended:
                await interaction.response.send_message(f"This event has come and gone. You cannot join it anymore")
                return
            try:
                data = await db.server_config(interaction.guild.id)
                if data.guild_role is not None and eventinfo.guild_only and not interaction.user._roles.has(data.guild_role):
                    await interaction.response.send_message(f"This event is only for Guild members.")
                    return
                await db.join_event(eventid, interaction.user.id)
                if eventinfo.is_started:
                    stat_convert = {
                        "pvp": "user_kills", "step": "steps", "npc": "npc_kills", "level": "level"}
                    smmoid = await db.get_smmoid(interaction.user.id)
                    profile = await api.get_all(smmoid)
                    info = profile[stat_convert[eventinfo.type]]

                    await db.update_start_stat(eventid, interaction.user.id, info)

                await interaction.user.add_roles(interaction.guild.get_role(eventinfo.event_role))
                await interaction.response.send_message(f"You have succesfully joined the {eventinfo.name} event.")
                return
            except Exception as e:
                await interaction.response.send_message(embed=Embed(title="Error", description=e))
                raise e

        elif len(active_events) == 1:
            eventid = active_events[0].id

            if tempid is not None and tempid != eventid:
                await interaction.response.send_message("The ID you entered is not valid. Please run `&e join` to join the only active event")
                return
            try:
                # if guild only, check if in guild
                if active_events[0].guild_only and not interaction.user._roles.has(710315282920636506):
                    await interaction.response.send_message(f"This event is only for Guild members.")
                    return
                elif await db.has_joined(eventid, interaction.user.id):
                    await interaction.response.send_message(f"You've already joined the only active event.")
                    return
                await db.join_event(eventid, interaction.user.id)
                await interaction.user.add_roles(interaction.guild.get_role(active_events[0].event_role))

                await interaction.response.send_message(f"You have succesfully joined the {active_events[0].name} event.")
            except Exception as e:
                await interaction.response.send_message(embed=Embed(title="Error", description=e))
                raise e

            return
        elif(eventid is None):
            if len(active_events) > 1:
                await interaction.response.send_message(f"There are multiple active events. Please specify the event id with `/event join [eventid]`")
            else:
                await interaction.response.send_message("There are no joinable events right now.")
            return

    @app_commands.command()
    @app_checks.is_owner()
    async def ids(self, interaction:discord.Interaction, eventid: int, num: int):

        participants = await db.get_participants(eventid)
        if participants == []:
            await interaction.response.send_message("That doesn't appear to be a valid event id")
            return

        participants.sort(
            reverse=True, key=lambda x: x.current_stat-x.starting_stat)

        embed = Embed(title=f"List of IDs of top {num} users")
        string = ""

        for i in range(num):
            try:
                user = participants[i]
            except IndexError:
                break

            string += f"{user.discordid}\n"

        embed.description = string
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_checks.is_verified()
    async def leaderboard(self, interaction:discord.Interaction, eventid: int):
        valid = await db.valid_event(eventid, interaction.guild.id)
        if valid is False:
            await interaction.response.send_message("Invalid event ID")
            return

        translation = {"pvp": "PvP Kills", "step": "Steps",
                       "npc": "NPC Kills", "level": "Levels"}

        participants = await db.get_participants(eventid)
        if participants == []:
            await interaction.response.send_message("That doesn't appear to be a valid event id")
            return
        eventinfo = await db.event_info(eventid, interaction.guild.id)
        if eventinfo.is_started is False:
            await interaction.response.send_message("The event has not started yet")
            return
        participants.sort(
            reverse=True, key=lambda x: x.current_stat-x.starting_stat)

        embed = Embed(title=f"Top 10 Leaderboard for {eventinfo.name}")
        string = ""

        for i in range(10):
            try:
                user = participants[i]
            except IndexError:
                break
            discord_user = self.bot.get_user(user.discordid)

            string += f"**{i+1}.** {discord_user.mention if discord_user is not None else f'<@{user.discordid}>'} - {user.current_stat - user.starting_stat} {translation[eventinfo.type]}\n"

        embed.description = string
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='finished')
    @app_checks.is_admin()
    async def finished_events(self, interaction:discord.Interaction):

        events = await db.finished_events(interaction.guild.id)
        if events is None:
            await interaction.response.send_message("There are no events to clean up")
            return
        string = ""
        for event in events:
            string += f"**{event.name}:** {event.type} event with id: {event.id}\n"

        await interaction.response.send_message(embed=Embed(title="Events to clean up", description=string))

    @app_commands.command()
    @app_checks.is_verified()
    async def active_events(self, interaction:discord.Interaction):

        events = await db.active_events(interaction.guild.id)
        string = ""
        for event in events:
            string += f"**{event.name}:** {event.type} event with id: {event.id}\n"

        if string == "":
            await interaction.response.send_message(embed=Embed(title="There are no active events"))
        else:
            await interaction.response.send_message(embed=Embed(title="Active Events", description=string))

    @app_commands.command()
    @app_checks.is_verified()
    async def joinable_events(self, interaction:discord.Interaction):

        events = await db.available_events(interaction.guild.id)
        guildonly = ""
        otherevents = ""

        for event in events:
            if event.guild_only:
                guildonly += f"**{event.name}:** {event.type} event with id: **{event.id}**\n"
            else:
                otherevents += f"**{event.name}:** {event.type} event with id: **{event.id}**\n"

        embed = Embed(title="Joinable Events",
                      description="Below are events that you can join")
        if len(guildonly) > 0 or len(otherevents) > 0:
            if len(guildonly) > 0:
                embed = embed.add_field(
                    name="Guild Only Events", value=guildonly, inline=True)
            if len(otherevents) > 0:
                embed = embed.add_field(
                    name="Open Events", value=otherevents, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=Embed(title="No Joinable Events"))

    @tasks.loop(hours=1, reconnect=True)
    async def stat_update(self, server=None):
        await log.log(self.bot, "Task Started", "Events Stats are being updated")
        stat_convert = {"pvp": "user_kills", "step": "steps",
                        "npc": "npc_kills", "level": "level"}
        all_events = await db.active_events(server)

        for event in all_events:

            participants = await db.get_participants(event.id)

            for participant in participants:

                smmoid = await db.get_smmoid(participant.discordid)
                profile = await api.get_all(smmoid)
                try:
                    await db.update_stat(event.id,
                                     participant.discordid,
                                     profile[stat_convert[event.type]])
                except KeyError:
                    logger.error(f"KeyError for {participant.discordid} in {event.id} with {profile}")

    @stat_update.before_loop
    async def before_stat_update(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Event(bot))
    logger.info("Event Cog Loaded")
