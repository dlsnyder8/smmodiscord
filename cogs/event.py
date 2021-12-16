import discord
from discord import Embed
from discord.ext import commands, tasks
from util import checks, log
import api
import logging
import database as db

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Event(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.event_types = ["step","pvp","npc","level"]
        self.stat_update.start()

    
    @commands.group(aliases = ['e'], hidden=True)
    async def event(self,ctx):
        if ctx.invoked_subcommand is None:
            pass


    @event.command()
    @checks.is_owner()
    async def create(self,ctx,name : str, eventtype : str):
        if eventtype not in self.event_types:
            await ctx.send(embed=Embed(title="Invalid event type",description="Events must be one of the following:\n`step`,`level`,`npc`,`pvp`"))
            return

        try:
            event_id = db.create_event(ctx.guild.id,name,eventtype)
            print(event_id)
            await ctx.send(f"Event has been created with id {event_id}. Please remember this ID.")

        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.is_owner()
    async def start(self,ctx,eventid):
        stat_convert = {"pvp" : "user_kills","step" : "steps", "npc" : "npc_kills", "level" : "level"}
        try:
            db.start_event(eventid)
            eventinfo = db.event_info(eventid)
           
            members = db.get_participants(eventid)
            if len(members) == 0:
                await ctx.send("There are no participants for that event")
                return
            if members is None:
                await ctx.send("The event ID might be incorrect or something brokey")
                return
            

            
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

        
        for member in members:
                
            smmoid = db.get_smmoid(member[0])
            profile = api.get_all(smmoid)
            info = profile[stat_convert[eventinfo[2]]]

            db.update_start_stat(eventid,member[0],info)




        await ctx.send(f"Event {eventid} has started!")
    
    @event.command()
    @checks.is_owner()
    async def end(self,ctx,eventid):
        try:
            db.end_event(eventid)
            await ctx.send(f"Event {eventid} has concluded.")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e


    @event.command()
    @checks.is_owner()
    async def guild_only(self,ctx, eventid : int, boolean : bool):
        try:
            db.event_guild_only(eventid,boolean)
            if boolean:
                await ctx.send(f"Event {eventid} has been set to `guild only`")
            else:
                await ctx.send(f"Event {eventid} has been set to `public`")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.in_fly()
    @checks.is_verified()
    async def stat(self,ctx,eventid=None):

        translation = {"pvp" : "PvP Kills","step" : "Steps", "npc" : "NPC Kills", "level" : "Levels"}

        active_events = db.active_events()
        print(len(active_events))
        print(active_events)
        if len(active_events) == 1:
            eventid = active_events[0][0]
            
            progress = db.participant_progress(eventid,ctx.author.id)
            eventinfo = db.event_info(eventid)
            if progress is None:
                await ctx.send("You are not particpating in the current event")
                return
                
            
        elif len(active_events) > 1:
            if eventid is None:
                await ctx.send(f"Please specify an event id as there are multiple active events.")
                return
            else:
                progress = db.participant_progress(eventid,ctx.author.id)
                eventinfo = db.event_info(eventid)
                if progress is None:
                    await ctx.send("You are not a participant in that event or that event does not exist.")
                    return
        
        else:
            await ctx.send("There are no active events right now. Please wait for someone to start one.")
            return


        embed = Embed(title=f"Your {translation[eventinfo[2]]} for the **{eventinfo[1]}** Event",description=f"**Starting amount:** {progress[0]}\n**Last Updated Amount:** {progress[1]}\n**Difference:** {progress[2]}")
        embed = embed.set_footer(text=f"Last Updated: {progress[3]}")
        await ctx.send(embed=embed)



    @event.command()
    @checks.is_owner()
    async def participants(self,ctx,eventid=None):
        if eventid is None:
            await ctx.send("You must specify an event ID.")
            return
        else:
            participants = db.get_participants(eventid)
            await ctx.send(embed=Embed(title="Number of Participants",description=f"There are {len(participants)} people particpating in this event."))
            return

    @event.command()
    @checks.in_fly()
    @checks.is_verified()
    async def join(self,ctx,eventid=None):
        active_events = db.available_events()
        if len(active_events) == 1:
            eventid = active_events[0][0]
            try:
                # if guild only, check if in guild
                if active_events[0][-1] and not ctx.author._roles.has(710315282920636506):
                    await ctx.send(f"This event is only for Friendly members.")
                    return 
                db.join_event(eventid,ctx.author.id)
                await ctx.send(f"You have succesfully joined the {active_events[0][2]} event.")
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
        else:
            try:
                
                eventinfo = db.event_info(eventid)
                if eventinfo[3]:
                    await ctx.send(f"This event has already started")
                    return
                if eventinfo[-1] and not ctx.author._roles.has(710315282920636506):
                    await ctx.send(f"This event is only for Friendly members.")
                    return 
                db.join_event(eventid,ctx.author.id)
                await ctx.send(f"You have succesfully joined the {eventinfo[1]} event.")
            except Exception as e:
                await ctx.send(embed=Embed(title="Error", description=e))
                raise e
    

    @event.command(aliases=['lb'])
    @checks.is_owner()
    async def leaderboard(self,ctx,eventid:int):
        translation = {"pvp" : "PvP Kills","step" : "Steps", "npc" : "NPC Kills", "level" : "Levels"}
    
        participants = db.get_participants(eventid)
        if len(participants) == 0 or participants is None:
            await ctx.send("That doesn't appear to be a valid event id")
            return
        eventinfo = db.event_info(eventid)
        participants.sort(reverse=True,key=lambda x:x[4])

        embed = Embed(title=f"Top 10 Leaderboard for {eventinfo[1]}")
        string = ""
        print(participants)
        for i in range(10):
            try:
                user = participants[i]
            except IndexError:
                break
            discord_user = self.bot.get_user(user[0])

            string+= f"**{i+1}.** {discord_user.mention} - {user[4]} {translation[eventinfo[2]]}\n"

        embed.description = string
        await ctx.send(embed=embed)

        

        


    @event.command(aliases=['active'])
    @checks.is_owner()
    async def active_events(self,ctx):
        
        events = db.active_events()
        string = ""
        for event in events:
            string += f"**{event[2]}:** {event[3]} event with id: {event[0]}\n"
        await ctx.send(embed=Embed(title="Active Events",description=string))

    @event.command(aliases=['joinable'])
    @checks.is_owner()
    async def joinable_events(self,ctx):
        
        events = db.available_events()
        flyonly = ""
        otherevents = ""

        for event in events:
            if event[4]:
                flyonly += f"**{event[2]}:** {event[3]} event with id: **{event[0]}**\n"
            else:
                otherevents += f"**{event[2]}:** {event[3]} event with id: **{event[0]}**\n"

        embed = Embed(title="Joinable Events",description="Below are events that you can join")
        if len(flyonly) > 0 or len(otherevents) > 0:
            if len(flyonly) > 0:
                embed = embed.add_field(name="Fly Only Events",value=flyonly,inline=True)
            if len(otherevents) > 0:
                embed = embed.add_field(name="Open Events",value=otherevents,inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=Embed(title="No Joinable Events"))
    
    @tasks.loop(hours=1)
    async def stat_update(self):
        await log.log(self.bot,"Task Started","Events Stats are being updated")
        stat_convert = {"pvp" : "user_kills","step" : "steps", "npc" : "npc_kills", "level" : "level"}
        all_events = db.active_events()

        for event in all_events:
            eventid = event[0]
            participants = db.get_participants(eventid)
            eventtype = event[3]
            for participant in participants:
                discid = participant[0]
                smmoid = db.get_smmoid(discid)
                profile = api.get_all(smmoid)
                db.update_stat(eventid,discid,profile[stat_convert[eventtype]])


    @stat_update.before_loop
    async def before_stat_update(self):
        await self.bot.wait_until_ready()

    
def setup(bot):
    bot.add_cog(Event(bot))
    print("Event Cog Loaded")