import discord
from discord.ext import commands, tasks
from discord import Embed
import api
import database as db
from util import checks, log
import logging
from datetime import datetime, timezone, timedelta
from dateutil import parser
import pytz


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Diamond(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.diamond_check.start()

    @commands.group(aliases=['d'], hidden=True)
    async def diamond(self, ctx):
        if ctx.invoked_subcommand is None:

            pass

    @diamond.command()
    @checks.is_owner()
    async def setup(self, ctx, channel: discord.TextChannel, role: discord.Role):
        try:
            await db.add_diamond_role(ctx.guild.id, role.id)
            await db.add_diamond_channel(ctx.guild.id, channel.id)
            await db.update_timestamp(ctx.guild.id, datetime.utcnow())
            await ctx.send("Succesfully added the channel and role")
        except Exception as e:
            await ctx.send(e)
            raise e

    @diamond.command()
    @checks.is_owner()
    async def toggle(self, ctx, boolean: bool):
        try:
            await db.enable_diamond_ping(ctx.guild.id, boolean)
            await ctx.send(f"Diamond pings have been set to: {boolean}")
        except Exception as e:
            await ctx.send(e)
            raise e

    @diamond.command()
    @checks.is_owner()
    async def config(self, ctx):

        config = await db.server_config(ctx.guild.id)
        print(config)
        ID, ping_bool, role, channel, timestamp = config[0]
        embed = Embed(title="Server Config",
                      description=f"ID: {ID}\nDiamond Ping: {ping_bool}\nPinged Role: {ctx.guild.get_role(role)}\nChannel: {ctx.guild.get_channel(channel)}")
        await ctx.send(embed=embed)

    @tasks.loop(minutes=1, reconnect=True)
    async def diamond_check(self):
        # print('starting diamond check')
        cheap_diamonds = False
        more_than_200 = False
        string = ""
        listings = await api.diamond_market()
        allservers = await db.all_servers()
        # listings = [{"price_per_diamond": 1, "diamonds_remaining": 5}]

        # Servers who have premium and have a properly configured diamond pings
        filtered = [
            x for x in allservers if x.premium and x.diamond_ping and x.diamond_role is not None and x.diamond_channel is not None]

        for server in filtered:
            diamond = [x for x in listings if x['price_per_diamond']
                       < server.diamond_amount]

            if diamond is not []:
                embed = Embed(title="Cheap Diamonds!!!")
                string = ""
                for list in diamond:
                    string += f"There are {list['diamonds_remaining']} diamonds left at {list['price_per_diamond']:,} each.\n"

                embed.description = string
                guild = self.bot.get_guild(server.serverid)
                if guild is None:
                    continue
                chan = self.bot.get_channel(server.diamond_channel)
                role = guild.get_role(server.diamond_role)

                if chan is None or role is None:
                    embed = Embed(title="Diamond Config is missing role or channel",
                                  description=f"Role: {role}\nChannel: {chan}")
                    await log.server_log_embed(self.bot, server.serverid, embed)
                    continue
                if server.last_pinged is None:
                    await db.update_timestamp(server.serverid, datetime.now(timezone.utc))
                    continue
                plus30min = server.last_pinged + timedelta(minutes=29)
                plus30min = pytz.utc.localize(plus30min)

                if plus30min < datetime.now(timezone.utc):
                    await chan.send(f'{role.mention}', embed=embed)
                    await db.update_timestamp(server.serverid, datetime.now(timezone.utc))

    @diamond_check.before_loop
    async def before_diamodn_check(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Diamond(bot))
    print("Diamond Cog Loaded")
