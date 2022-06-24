import discord
from discord.ext import commands, tasks
from discord import Embed
from discord.utils import get
from util import checks, log
import database as db
import random
import string
import api
import logging

logger = logging.getLogger('discord')


dyl = 332314562575597579
server = 444067492013408266


class Pleb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_all_plebs.start()

    @commands.group(aliases=['p'], hidden=True)
    async def pleb(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @pleb.command()
    @checks.is_owner()
    async def ispleb(self, ctx, arg):
        smmoid = int(arg)
        ispleb = await api.pleb_status(smmoid)
        if ispleb:
            await ctx.send(f'{smmoid} is a pleb')
        else:
            await ctx.send(f'{smmoid} is not a pleb')
        return

    @pleb.command()
    @checks.is_owner()
    async def whois(self, ctx, *, member: discord.Member):
        users = await db.disc_ids(member.id)
        for user in users:
            await ctx.send(f'user: {user.smmoid}, verified: {user.verified}')
            return
        await ctx.send("No account connected")

   

    @commands.command(hidden=True)
    @checks.is_owner()
    async def plebcheck(self, ctx=None):

        await log.log(self.bot, "Pleb Check Started", "")
        if(await db.server_added(server)):  # server has been initialized
            pleb_role = (await db.server_config(server)).pleb_role
        else:
            print("Server has not been added to db")
            return

        if ctx is not None:
            await ctx.send("Pleb check starting...")

        plebs = await db.get_all_plebs()
        guild = self.bot.get_guild(int(server))
        role = guild.get_role(int(pleb_role))
        count = 0
        if ctx is not None:
            await ctx.send(f"There are {len(plebs)} people to check.")
        in_server = 0
        for pleb in plebs:

            count += 1
            if ctx is not None:
                if count % 100 == 0:
                    await ctx.send(f"{count} members checked")

            smmoid = pleb.smmoid

            user = guild.get_member(pleb.discid)  # get user object
            if user is None:
                #print(f'{discid} is not found is the server')
                in_server += 1
                continue

            # If user is muted, do not give them the role
            if user._roles.has(751808682169466962):
                continue

            isPleb = await api.pleb_status(smmoid)

            if isPleb is None:
                print("THE API IS STUPID")

            elif isPleb is True:
                await db.update_status(smmoid, True)  # they are a pleb
                if not user._roles.has(832878414839021598):
                    await user.add_roles(role)  # give user pleb role
                #print(f'{user} with uid: {smmoid} has pleb!')

            elif isPleb is False:  # user is not pleb
                await db.update_status(smmoid, False)  # not a pleb
                if user._roles.has(832878414839021598):
                    await user.remove_roles(role)  # remove pleb role
                #print(f'{user} lost pleb!')

        if ctx is not None:
            await ctx.send(f"Pleb check finished! {in_server} linked members not in this server")

    @tasks.loop(hours=3, reconnect=True)
    async def update_all_plebs(self):
        await self.plebcheck()
        return

    @update_all_plebs.before_loop
    async def before_pleb(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Pleb(bot))
    print("Pleb Cog Loaded")
