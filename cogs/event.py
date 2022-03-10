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
    @checks.MI6()
    async def create(self,ctx,name : str, eventtype : str):
        if eventtype not in self.event_types:
            await ctx.send(embed=Embed(title="Invalid event type",description="Events must be one of the following:\n`step`,`level`,`npc`,`pvp`"))
            return

        try:
            guildrole = await ctx.guild.create_role(name=name)
            event_id = await db.create_event(ctx.guild.id,name,eventtype,guildrole.id)
            await ctx.send(f"Event has been created with id {event_id}. Please remember this ID.")
            
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.MI6()
    async def start(self,ctx,eventid):
        stat_convert = {"pvp" : "user_kills","step" : "steps", "npc" : "npc_kills", "level" : "level"}
        try:
            await db.start_event(eventid)
            eventinfo = await db.event_info(eventid)
           
            members = await db.get_participants(eventid)
            if len(members) == 0:
                await ctx.send("There are no participants for that event. It has been ended automatically")
                await db.end_event(eventid)
                return
            elif members is None:
                await ctx.send("The event ID might be incorrect or something brokey")
                return
            

            
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

        
        for member in members:
                
            smmoid = await db.get_smmoid(member[0])
            profile = await api.get_all(smmoid)
            info = profile[stat_convert[eventinfo[2]]]

            await db.update_start_stat(eventid,member[0],info)




        await ctx.send(f"Event {eventid} has started!")
    
    @event.command()
    @checks.MI6()
    async def end(self,ctx,eventid):
        try:
            eventinfo = await db.event_info(eventid)
            if eventinfo is None:
                await ctx.send("That event id is not valid")
                return
            elif eventinfo[4] is True:
                await ctx.send("That event has already been ended")
                return
            
            await self.stat_update()
            await db.end_event(eventid)
            await ctx.send(f"Event {eventid} has concluded.")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.is_owner()
    async def cleanup(self,ctx,eventid : int):
        try:
            eventinfo = await db.event_info(eventid)
            if eventinfo is None:
                await ctx.send("That appears to be an invalid ID")
                return
            if eventinfo[4] is False:
                await ctx.send(f"You can't cleanup an active event!\n\nIf you want to end an event, run `&event end {eventid}`")
                return
            guildrole = ctx.guild.get_role(eventinfo[8])
            await guildrole.delete(reason="Event ended")
            await ctx.send("Cleanup Concluded")

        except AttributeError as e:
            await ctx.send("This event has already been cleaned up")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e


    @event.command()
    @checks.MI6()
    async def results(self,ctx,eventid: int):
        translation = {"pvp" : "PvP Kills","step" : "Steps", "npc" : "NPC Kills", "level" : "Levels"}
    
        participants = await db.get_participants(eventid)
        if len(participants) == 0 or participants is None:
            await ctx.send("That doesn't appear to be a valid event id")
            return
        eventinfo = await db.event_info(eventid)
        participants.sort(reverse=True,key=lambda x:x[4])

        embed = Embed(title=f"Results for {eventinfo[1]}")
        string = ""
        i = 1
        for particpant in participants:
            string += f"**{i}.** <@{particpant[0]}> - {particpant[4]} {translation[eventinfo[2]]}\n"
            i += 1
        embed.description = string
        await ctx.send(embed=embed)



    @event.command()
    @checks.MI6()
    async def guild_only(self,ctx, eventid : int, boolean : bool):
        try:
            await db.event_guild_only(eventid,boolean)
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

        active_events = await db.active_events()
        if len(active_events) == 1:
            eventid = active_events[0].id
            
            progress = await db.participant_progress(eventid,ctx.author.id)
            eventinfo = await db.event_info(eventid)
            if progress is None:
                await ctx.send("You are not particpating in the current event")
                return
                
            
        elif len(active_events) > 1:
            if eventid is None:
                await ctx.send(f"Please specify an event id as there are multiple active events.")
                return
            else:
                progress = await db.participant_progress(eventid,ctx.author.id)
                eventinfo = await db.event_info(eventid)
                if progress is None:
                    await ctx.send("You are not a participant in that event or that event does not exist.")
                    return
        
        else:
            await ctx.send("There are no active events right now. Please wait for someone to start one.")
            return


        embed = Embed(title=f"Your {translation[eventinfo.type]} for the **{eventinfo.name}** Event",description=f"**Starting amount:** {progress[0]}\n**Last Updated Amount:** {progress[1]}\n**Difference:** {progress[2]}")
        embed = embed.set_footer(text=f"Last Updated: {progress[3]}")
        await ctx.send(embed=embed)



    @event.command()
    @checks.MI6()
    async def participants(self,ctx,eventid=None):
        if eventid is None:
            await ctx.send("You must specify an event ID.")
            return
        else:
            participants = await db.get_participants(eventid)
            await ctx.send(embed=Embed(title="Number of Participants",description=f"There are {len(participants)} people particpating in this event."))
            return

    @event.command()
    @checks.in_fly()
    @checks.is_verified()
    async def join(self,ctx,eventid=None):
        active_events = await db.available_events()
        eventinfo = await db.event_info(eventid)
        tempid=eventid

        # If they've joined it before, error
        if await db.has_joined(eventid,ctx.author.id) and eventid is not None:
            await ctx.send(f"You have already joined event {eventinfo.name}")
            return

        # First, check event they want to join. If event exists...
        if eventinfo is not None:

            #check if event is already ended
            if eventinfo.is_ended:
                await ctx.send(f"This event has come and gone. You cannot join it anymore")
                return
            try:
                
                # if eventinfo[3]:
                #     await ctx.send(f"This event has already started")
                #     return

                # If for friendly only...
                if eventinfo.friendly_only and not ctx.author._roles.has(710315282920636506):
                    await ctx.send(f"This event is only for Friendly members.")
                    return 
                await db.join_event(eventid,ctx.author.id)
                if eventinfo.is_started:
                    stat_convert = {"pvp" : "user_kills","step" : "steps", "npc" : "npc_kills", "level" : "level"}
                    smmoid = await db.get_smmoid(ctx.author.id)
                    profile = await api.get_all(smmoid)
                    info = profile[stat_convert[eventinfo.type]]

                    await db.update_start_stat(eventid,ctx.author.id,info)



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
                if active_events[0].friendly_only and not ctx.author._roles.has(710315282920636506):
                    await ctx.send(f"This event is only for Friendly members.")
                    return 
                elif await db.has_joined(eventid,ctx.author.id):
                    await ctx.send(f"You've already joined the only active event.")
                    return
                await db.join_event(eventid,ctx.author.id)
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
       
    

    @event.command(aliases=['lb'])
    @checks.in_fly()
    async def leaderboard(self,ctx,eventid:int):
        translation = {"pvp" : "PvP Kills","step" : "Steps", "npc" : "NPC Kills", "level" : "Levels"}
    
        participants = await db.get_participants(eventid)
        if participants == []:
            await ctx.send("That doesn't appear to be a valid event id")
            return
        eventinfo = await db.event_info(eventid)
        participants.sort(reverse=True,key=lambda x:x.current_stat-x.starting_stat)

        embed = Embed(title=f"Top 10 Leaderboard for {eventinfo.name}")
        string = ""
        
        for i in range(10):
            try:
                user = participants[i]
            except IndexError:
                break
            discord_user = self.bot.get_user(user.discordid)

            string+= f"**{i+1}.** {discord_user.mention} - {user.current_stat - user.starting_stat} {translation[eventinfo.type]}\n"

        embed.description = string
        await ctx.send(embed=embed)

        

        


    @event.command(aliases=['active'])
    @checks.in_fly()
    async def active_events(self,ctx):
        
        events = await db.active_events()
        string = ""
        for event in events:
            string += f"**{event.name}:** {event.type} event with id: {event.id}\n"

        if string == "":
            await ctx.send(embed=Embed(title="There are no active events"))
        else:
            await ctx.send(embed=Embed(title="Active Events",description=string))

    @event.command(aliases=['joinable'])
    @checks.in_fly()
    async def joinable_events(self,ctx):
        
        events = await db.available_events()
        flyonly = ""
        otherevents = ""

        for event in events:
            if event.friendly_only:
                flyonly += f"**{event.name}:** {event.type} event with id: **{event.id}**\n"
            else:
                otherevents += f"**{event.name}:** {event.type} event with id: **{event.id}**\n"

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
        all_events = await db.active_events()

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