import discord
from discord.ext import commands, tasks
from discord import Embed
from util import checks,log
import api
import logging
import database as db
from datetime import datetime, timezone,timedelta
from dateutil import parser
import pytz



logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



class Diamond(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.diamond_check.start()

    
    @commands.group(aliases = ['d'], hidden=True)
    async def diamond(self,ctx):
        if ctx.invoked_subcommand is None:
        
            pass


    @diamond.command()
    @checks.is_owner()
    async def setup(self,ctx, channel: discord.TextChannel, role: discord.Role):
        try:
            db.add_diamond_role(ctx.guild.id,role.id)
            db.add_diamond_channel(ctx.guild.id,channel.id)
            db.update_timestamp(ctx.guild.id,datetime.now(timezone.utc))
            await ctx.send("Succesfully added the channel and role")
        except Exception as e:
            await ctx.send(e)

    @diamond.command()
    @checks.is_owner()
    async def toggle(self,ctx, boolean : bool):
        try:
            db.enable_diamond_ping(ctx.guild.id,boolean)
            await ctx.send(f"Diamond pings have been set to: {boolean}")
        except Exception as e:
            await ctx.send(e)

    @diamond.command()
    @checks.is_owner()  
    async def config(self,ctx):
       
        config = db.server_config(ctx.guild.id)
        print(config)
        ID, ping_bool,role,channel,timestamp = config[0]
        embed = Embed(title="Server Config",description=f"ID: {ID}\nDiamond Ping: {ping_bool}\nPinged Role: {ctx.guild.get_role(role)}\nChannel: {ctx.guild.get_channel(channel)}")
        await ctx.send(embed=embed)
   

    @tasks.loop(minutes=1)
    async def diamond_check(self):
        print("Diamond Loop starting")
        cheap_diamonds = False
        more_than_200 = False
        string = ""
        listings = api.diamond_market()
        embed = Embed(title="Diamonds Under 1.2m")

        for listing in listings:
            if listing["price_per_diamond"] <= 1200000: # 1.2m
                cheap_diamonds = True
                string += f"There are {listing['diamonds_remaining']} diamonds left at {listing['price_per_diamond']:,} each.\n" 
                if listing['diamonds_remaining'] >= 200:
                    more_than_200 = True
        if cheap_diamonds:
            allinfo = db.get_diamond_ping_info()
           
            embed.description = string
            for server in allinfo:
                try:
                    

                    guild = self.bot.get_guild(int(server[0]))
                    
                    channel = self.bot.get_channel(server[2])
                    role =  guild.get_role(server[1])

                    plus30min = server[3] + timedelta(minutes=29)
                    plus30min = pytz.utc.localize(plus30min)
                  
                    
                    if plus30min < datetime.now(timezone.utc):
                        if more_than_200:
                            await channel.send(content=f"{role.mention}\n <https://web.simple-mmo.com/diamond-market>", embed=embed)
                        else:
                            await channel.send(content=f"{role.name}\n <https://web.simple-mmo.com/diamond-market>", embed=embed)
                        db.update_timestamp(server[0],datetime.now(timezone.utc))
                   
                    


                except Exception as e:
                    await log.log(self.bot,"Diamond Market Fucky",f"Something went wrong with {server[0]},{server[2]},{server[1]}")
                    await log.log(self.bot,"Diamond Market Fucky",e)
                    pass
        else:
            print("No cheap diamonds")

    @diamond_check.before_loop
    async def before_diamodn_check(self):
        await self.bot.wait_until_ready()



def setup(bot):
    bot.add_cog(Diamond(bot))
    print("Diamond Cog Loaded")
