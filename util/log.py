# TODO: Load this cog in bot.py
import discord
from discord import channel
from discord.embeds import Embed
from discord.ext import commands
from discord.utils import get
from util import checks
import database as db
import api
import asyncio
import time
import logging
from datetime import datetime


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


   
async def test(self,ctx, desc: str):
    await self.genlog(ctx,title="testing",desc=desc)



async def log(bot, title : str, desc : str):
    channel = bot.get_channel(790666439673643028)
    embed = discord.Embed(
        title=title, 
        description=desc,
        timestamp=datetime.now(datetime.utcnow), 
        color=0x00ff00
        )
    

    await channel.send(embed=embed)


async def flylog(bot, title: str, desc: str, userid):
    channel = bot.get_channel(770177350758563850) # Actual log channel
    #channel = bot.get_channel(868565628695494716) #shit-code-only channel
    embed = discord.Embed(
        title = title,
        description = desc,
        timestamp=datetime.now(),
        color=0x008e64
    )
    embed.set_footer(text=f"ID: {userid}")
    await channel.send(embed=embed)


