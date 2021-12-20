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


class Wars(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # TODO: Change function name and alias
    @commands.group(aliases = ['war','w'], hidden=True)
    async def wars(self,ctx):
        if ctx.invoked_subcommand is None:
            pass


def setup(bot):
    bot.add_cog(Wars(bot))
    print("Wars Cog Loaded")