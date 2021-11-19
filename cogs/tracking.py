import discord
from discord.ext import commands, tasks
from discord.utils import get
from util import checks
import database as db
import random   
import string
import api
import logging
import aiocron
import asyncio
from datetime import datetime



class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases = ['t'],hidden=True)
    async def tracking(self,ctx):
        if ctx.invoked_subcommand is None:
            pass






def setup(bot):
    bot.add_cog(Tracking(bot))
    print("Pleb Cog Loaded")


asyncio.get_event_loop().run_forever()