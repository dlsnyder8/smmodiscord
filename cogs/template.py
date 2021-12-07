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

# TODO: Change class name
class Template(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # TODO: Change function name and alias
    @commands.group(aliases = ['change me'], hidden=True)
    async def Template(self,ctx):
        if ctx.invoked_subcommand is None:
            pass

# TODO: Add cog to load order in bot.py
# TODO: Change class name and print string
def setup(bot):
    bot.add_cog(Template(bot))
    print("Template Cog Loaded")