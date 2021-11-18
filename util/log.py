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





   
async def test(self,ctx, desc: str):
    await self.genlog(ctx,title="testing",desc=desc)



async def genlog(self, title : str, desc : str):
    channel = self.bot.get_channel(790666439673643028)
    embed = discord.Embed(
        title=title, 
        description=desc, 
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


