import discord
from discord import Embed
from discord.ext import commands
from util import checks
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

    
    @commands.group(aliases = ['e'], hidden=True)
    async def event(self,ctx):
        if ctx.invoked_subcommand is None:
            pass


    @event.command()
    @checks.is_owner()
    async def create(self,ctx,name : str, eventtype : str):
        if eventtype not in self.event_types:
            await ctx.send(embed=Embed(title="Invalid event type",description="Events must be on of the following:\n`step`,`level`,`npc`,`pvp`"))

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
        try:
            db.start_event(eventid)
            await ctx.send(f"Event {eventid} has started!")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e
    
    @event.command()
    @checks.is_owner()
    async def end(self,ctx,eventid):
        try:
            db.end_event(eventid)
            await ctx.send(f"Event {eventid} has confluded.")
        except Exception as e:
            await ctx.send(embed=Embed(title="Error", description=e))
            raise e

    @event.command()
    @checks.in_fly()
    async def join(self,ctx,eventid=None):
        active_events = db.active_events()
        if len(active_events == 1):
            eventid = active_events[0][0]
            try:
                db.join_event(eventid,ctx.author.id)
                await ctx.send(f"You have succesfully joined the {active_events[0][2]} event.")
            except Exception as e:
                await ctx.send(embed=Embed(title="Error", description=e))
                raise e
            
            return
        elif(eventid is None):
            await ctx.send(f"There are multiple active events. Please specify the event id with `{ctx.prefix}event join [eventid]`")
            return
        else:
            try:
                eventinfo = db.event_info(eventid)
                db.join_event(eventid,ctx.author.id)
                await ctx.send(f"You have succesfully joined the {eventinfo[1]} event.")
            except Exception as e:
                await ctx.send(embed=Embed(title="Error", description=e))
                raise e

    
def setup(bot):
    bot.add_cog(Event(bot))
    print("Event Cog Loaded")