import discord
from discord import Embed
from discord.ext import commands, tasks
import logging
import api
import database as db
from util import checks, log


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_types = ["step", "pvp", "npc", "level"]
        self.stat_update.start()

    @commands.group(aliases=['e'], hidden=True)
    @checks.server_configured()
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @event.command()
    @checks.is_admin()
    async def create(self, ctx, name: str, eventtype: str):
        if eventtype not in self.event_types:
            await ctx.send(embed=Embed(title="Invalid event type", description="Events must be one of the following:\n`step`,`level`,`npc`,`pvp`"))
            return

        try:
            guildrole = await ctx.guild.create_role(name=name)
            event_id = await db.create_event(ctx.guild.id, name, eventtype, guildrole.id)
            await ctx.send(f"Event has been created with id {event_id}. Please remember this ID.")

        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.is_admin()
    async def start(self, ctx, eventid):
        stat_convert = {"pvp": "user_kills", "step": "steps",
                        "npc": "npc_kills", "level": "level"}
        valid = await db.valid_event(eventid, ctx.guild.id)
        if valid is False:
            await ctx.send("Invalid event ID")
            return
        try:
            await db.start_event(eventid, ctx.guild.id)
            eventinfo = await db.event_info(eventid, ctx.guild.id)

            members = await db.get_participants(eventid)
            if members is None:
                await ctx.send("That is not a valid ID")
                return
            if len(members) == 0:
                await ctx.send("There are no participants for that event. It has been ended automatically")
                await db.end_event(eventid, ctx.guild.id)
                return
            elif members is None:
                await ctx.send("The event ID might be incorrect or something brokey")
                return

        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

        for member in members:

            smmoid = await db.get_smmoid(member.discordid)
            profile = await api.get_all(smmoid)
            info = profile[stat_convert[eventinfo.type]]

            await db.update_start_stat(eventid, member.discordid, info)

        await ctx.send(f"Event {eventid} has started!")

    @event.command()
    @checks.is_admin()
    async def end(self, ctx, eventid):
        try:
            eventinfo = await db.event_info(eventid, ctx.guild.id)
            if eventinfo is None:
                await ctx.send("That event id is not valid")
                return
            elif eventinfo.is_ended:
                await ctx.send("That event has already been ended")
                return

            await self.stat_update(ctx.guild.id)
            await db.end_event(eventid, ctx.guild.id)
            await ctx.send(f"Event {eventid} has concluded.")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.is_admin()
    async def cleanup(self, ctx, eventid: int):
        try:
            eventinfo = await db.event_info(eventid, ctx.guild.id)
            if eventinfo is None:
                await ctx.send(f"To see a list of events to cleanup, run {ctx.prefix}e finished ")
                return
            if eventinfo.is_ended is False:
                await ctx.send(f"You can't cleanup an active event!\n\nIf you want to end an event, run `&event end {eventid}`")
                return
            guildrole = ctx.guild.get_role(eventinfo.event_role)
            await db.cleanup_event(eventid, ctx.guild.id)
            await guildrole.delete(reason="Event ended")
            await ctx.send("Cleanup Concluded")

        except AttributeError:
            await ctx.send("This event has already been cleaned up")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.is_admin()
    async def results(self, ctx, eventid: int):
        valid = await db.valid_event(eventid, ctx.guild.id)
        if valid is False:
            await ctx.send("Invalid event ID")
            return

        translation = {"pvp": "PvP Kills", "step": "Steps",
                       "npc": "NPC Kills", "level": "Levels"}

        participants = await db.get_participants(eventid)
        if len(participants) == 0 or participants is None:
            await ctx.send("That doesn't appear to be a valid event id")
            return
        eventinfo = await db.event_info(eventid, ctx.guild.id)
        participants.sort(
            reverse=True, key=lambda x: x.current_stat-x.starting_stat)

        embed = Embed(title=f"Results for {eventinfo.name}")
        string = ""
        i = 1
        async with ctx.typing():
            for particpant in participants:
                string += f"**{i}.** <@{particpant.discordid}> - {particpant.current_stat-particpant.starting_stat} {translation[eventinfo.type]}\n"
                if i % 20 == 0:
                    last = i
                    embed.add_field(name=f'Users {i-20} - {i}', value=string)
                    string = ''

                if len(embed) > 5500:
                    await ctx.send(embed=embed)
                    embed = Embed(title=f"Results for {eventinfo.name}")

                i += 1

            if len(string) > 0:
                embed.add_field(name=f'Users {last} - {i-1}', value=string)
                await ctx.send(embed=embed)

    @event.command()
    @checks.is_admin()
    @checks.server_configured()
    async def guild_only(self, ctx, eventid: int, boolean: bool):
        try:
            await db.event_guild_only(eventid, ctx.guild.id, boolean)
            if boolean:
                await ctx.send(f"Event {eventid} has been set to `guild only`")
            else:
                await ctx.send(f"Event {eventid} has been set to `public`")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.is_verified()
    async def stat(self, ctx, eventid=None):

        translation = {"pvp": "PvP Kills", "step": "Steps",
                       "npc": "NPC Kills", "level": "Levels"}

        active_events = await db.active_events(ctx.guild.id)
        if len(active_events) == 1:
            eventid = active_events[0].id

            progress = await db.participant_progress(eventid, ctx.author.id)
            eventinfo = await db.event_info(eventid, ctx.guild.id)
            if progress is None or eventinfo is None:
                await ctx.send("You are not particpating in the current event")
                return

        elif len(active_events) > 1:
            if eventid is None:
                await ctx.send(f"Please specify an event id as there are multiple active events.")
                return
            else:
                progress = await db.participant_progress(eventid, ctx.author.id)
                eventinfo = await db.event_info(eventid, ctx.guild.id)
                if progress is None:
                    await ctx.send("You are not a participant in that event or that event does not exist.")
                    return
                elif eventinfo is None:
                    await ctx.send("That event does not exist or is not being hosted in this server.")

        else:
            await ctx.send("There are no active events right now. Please wait for someone to start one.")
            return

        embed = Embed(title=f"Your {translation[eventinfo.type]} for the **{eventinfo.name}** Event",
                      description=f"**Starting amount:** {progress[0]}\n**Last Updated Amount:** {progress[1]}\n**Difference:** {progress[2]}")
        embed = embed.set_footer(text=f"Last Updated: {progress[3]} UTC")
        await ctx.send(embed=embed)

    @event.command()
    @checks.is_admin()
    async def participants(self, ctx, eventid=None):

        if eventid is None:
            await ctx.send("You must specify an event ID.")
            return

        valid = await db.valid_event(eventid, ctx.guild.id)
        if valid is False:
            await ctx.send("Invalid event ID")
            return

        participants = await db.get_participants(eventid)
        if participants is None:
            await ctx.send(embed=Embed(
                title="Not a valid eventid",
                description=f"To see a list of events for this server, you can run {ctx.prefix}e joinable_events"
            ))
            return
        await ctx.send(embed=Embed(title="Number of Participants", description=f"There are {len(participants)} people particpating in this event."))
        return

    @event.command(aliases=['signup'])
    @checks.is_verified()
    @checks.server_configured()
    async def join(self, ctx, eventid=None):
        active_events = await db.available_events(ctx.guild.id)
        eventinfo = await db.event_info(eventid, ctx.guild.id)
        tempid = eventid

        # If they've joined it before, error
        if eventid is not None and await db.has_joined(eventid, ctx.author.id):
            await ctx.send(f"You have already joined event {eventinfo.name}")
            return

        # First, check event they want to join. If event exists...
        if eventinfo is not None:

            # check if event is already ended
            if eventinfo.is_ended:
                await ctx.send(f"This event has come and gone. You cannot join it anymore")
                return
            try:
                data = await db.server_config(ctx.guild.id)
                if data.guild_role is not None and eventinfo.guild_only and not ctx.author._roles.has(data.guild_role):
                    await ctx.send(f"This event is only for Guild members.")
                    return
                await db.join_event(eventid, ctx.author.id)
                if eventinfo.is_started:
                    stat_convert = {
                        "pvp": "user_kills", "step": "steps", "npc": "npc_kills", "level": "level"}
                    smmoid = await db.get_smmoid(ctx.author.id)
                    profile = await api.get_all(smmoid)
                    info = profile[stat_convert[eventinfo.type]]

                    await db.update_start_stat(eventid, ctx.author.id, info)

                await ctx.author.add_roles(ctx.guild.get_role(eventinfo.event_role))
                await ctx.send(f"You have succesfully joined the {eventinfo.name} event.")
                return
            except Exception as e:
                await ctx.send(embed=Embed(title="Error", description=e))
                raise e

        elif len(active_events) == 1:
            eventid = active_events[0].id

            if tempid is not None and tempid != eventid:
                await ctx.send("The ID you entered is not valid. Please run `&e join` to join the only active event")
                return
            try:
                # if guild only, check if in guild
                if active_events[0].guild_only and not ctx.author._roles.has(710315282920636506):
                    await ctx.send(f"This event is only for Guild members.")
                    return
                elif await db.has_joined(eventid, ctx.author.id):
                    await ctx.send(f"You've already joined the only active event.")
                    return
                await db.join_event(eventid, ctx.author.id)
                await ctx.author.add_roles(ctx.guild.get_role(active_events[0].event_role))

                await ctx.send(f"You have succesfully joined the {active_events[0].name} event.")
            except Exception as e:
                await ctx.send(embed=Embed(title="Error", description=e))
                raise e

            return
        elif(eventid is None):
            if len(active_events) > 1:
                await ctx.send(f"There are multiple active events. Please specify the event id with `{ctx.prefix}event join [eventid]`")
            else:
                await ctx.send("There are no joinable events right now.")
            return

    @event.command()
    @checks.is_verified()
    @checks.is_owner()
    async def ids(self, ctx, eventid: int, num: int):

        participants = await db.get_participants(eventid)
        if participants == []:
            await ctx.send("That doesn't appear to be a valid event id")
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
        await ctx.send(embed=embed)

    @event.command(aliases=['lb'])
    @checks.is_verified()
    async def leaderboard(self, ctx, eventid: int):
        valid = await db.valid_event(eventid, ctx.guild.id)
        if valid is False:
            await ctx.send("Invalid event ID")
            return

        translation = {"pvp": "PvP Kills", "step": "Steps",
                       "npc": "NPC Kills", "level": "Levels"}

        participants = await db.get_participants(eventid)
        if participants == []:
            await ctx.send("That doesn't appear to be a valid event id")
            return
        eventinfo = await db.event_info(eventid, ctx.guild.id)
        if eventinfo.is_started is False:
            await ctx.reply("The event has not started yet")
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
        await ctx.send(embed=embed)

    @event.command(aliases=['finished'])
    @checks.is_admin()
    async def finished_events(self, ctx):

        events = await db.finished_events(ctx.guild.id)
        if events is None:
            await ctx.reply("There are no events to clean up")
            return
        string = ""
        for event in events:
            string += f"**{event.name}:** {event.type} event with id: {event.id}\n"

        await ctx.send(embed=Embed(title="Events to clean up", description=string))

    @event.command(aliases=['active'])
    @checks.is_verified()
    async def active_events(self, ctx):

        events = await db.active_events(ctx.guild.id)
        string = ""
        for event in events:
            string += f"**{event.name}:** {event.type} event with id: {event.id}\n"

        if string == "":
            await ctx.send(embed=Embed(title="There are no active events"))
        else:
            await ctx.send(embed=Embed(title="Active Events", description=string))

    @event.command(aliases=['joinable'])
    @checks.is_verified()
    async def joinable_events(self, ctx):

        events = await db.available_events(ctx.guild.id)
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
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=Embed(title="No Joinable Events"))

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
                await db.update_stat(event.id,
                                     participant.discordid,
                                     profile[stat_convert[event.type]])

    @stat_update.before_loop
    async def before_stat_update(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Event(bot))
    print("Event Cog Loaded")
