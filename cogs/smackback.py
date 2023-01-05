import discord
from discord.ext import commands
import api
from util import checks, log
import database as db
import logging


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Smackback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['sb'])
    async def smackback(self, ctx):
        if ctx.invoked_subcommand is None:
            pass


async def setup(bot):
    await bot.add_cog(Smackback(bot))
    print("Smackback Cog Loaded")
