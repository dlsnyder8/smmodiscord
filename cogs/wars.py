import discord
from discord.ext import commands
from discord import Embed
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

    @checks.in_fly_guild()
    @commands.group(aliases = ['war','w'], hidden=True)
    async def wars(self,ctx):
        if ctx.invoked_subcommand is None:
            pass

    @wars.command()
    async def friendly(self,ctx):
        wars = api.get_guild_wars(408,1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Friendly",description="There are no active wars. They may be on hold or may have all ended."))
            return
        


        warstring = ""
        for war in wars[:35]:
            friendly = war['guild_1']
            guild = war['guild_2']
            warstring += f"**{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members)\n"
        print(len(warstring))
        embed = Embed(title="Friendly Wars", description=warstring)

        await ctx.send(embed=embed)


    @wars.command()
    async def too(self,ctx):
        wars = api.get_guild_wars(455,1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Friendly Too",description="There are no active wars. They may be on hold or may have all ended."))
            return
        
        warstring = ""
        for war in wars:
            friendly = war['guild_1']
            guild = war['guild_2']
            warstring += f"**{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members)\n"

        await ctx.send(embed=Embed(title="Friendly Too Wars",description=warstring))

    @wars.command()
    async def nsf(self,ctx):
        wars = api.get_guild_wars(541,1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for NSF",description="There are no active wars. They may be on hold or may have all ended."))
            return
        
        warstring = ""
        for war in wars:
            friendly = war['guild_1']
            guild = war['guild_2']
            warstring += f"**{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members)\n"

        await ctx.send(embed=Embed(title="NSF Wars",description=warstring))

    
    @wars.command()
    async def hug(self,ctx,guild):
        pass

def setup(bot):
    bot.add_cog(Wars(bot))
    print("Wars Cog Loaded")