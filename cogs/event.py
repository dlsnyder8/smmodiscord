import discord
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

    
    @commands.group(aliases = ['e'], hidden=True)
    async def event(self,ctx):
        if ctx.invoked_subcommand is None:
            pass


    @event.command()
    @checks.is_owner()
    async def create(self,ctx,event):
        pass


    
def setup(bot):
    bot.add_cog(Event(bot))
    print("Event Cog Loaded")