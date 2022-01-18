import discord
from discord.ext import commands
from util import checks, log
import api
import logging
import database as db

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Smackback(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    
    @commands.group(aliases = ['sb'])
    async def Template(self,ctx):
        if ctx.invoked_subcommand is None:
            pass


    



def setup(bot):
    bot.add_cog(Smackback(bot))
    print("Smackback Cog Loaded")