import discord
from discord.ext import commands, tasks
from discord import app_commands
from util import checks, log, app_checks
from util.cooldowns import custom_is_me, BucketType
import database as db
import api
import logging
import config


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        
    @app_commands.command()
    @app_checks.is_verified()
    @app_commands.checks.dynamic_cooldown(custom_is_me(1,600),key=BucketType.Member)
    async def iampleb(self, interaction: discord.Interaction):
        user = interaction.user
        if user._roles.has(832878414839021598):
            await interaction.response.send_message("Hey dude you've already got the role.", ephemeral=True)
            return
        
        smmoid = await db.get_smmoid(user.id)
        isPleb = await api.pleb_status(smmoid)
        if isPleb is None:
            logging.error("THE API IS STUPID")
            await interaction.response.send_message("SMMO API Error")
            return

        elif isPleb is True:
            await db.update_status(smmoid, True)  # they are a pleb
            if not user._roles.has(832878414839021598):
                pleb_role = interaction.guild.get_role((await db.server_config(server)).pleb_role)
                if pleb_role is None:
                    await interaction.response.send_message("Supporter Role not found. Contact Dyl", ephemeral=True)
                    return
                await user.add_roles(pleb_role)  # give user pleb role
                await interaction.response.send_message("Role Given!", ephemeral=True)
           
            

    @commands.command(hidden=True)
    @checks.is_owner()
    async def plebcheck(self, ctx=None):

        await log.log(self.bot, "Pleb Check Started", "")
        if(await db.server_added(server)):  # server has been initialized
            pleb_role = (await db.server_config(server)).pleb_role
        else:
            logging.error("Server has not been added to db")
            return
        if ctx is not None:
            await ctx.send("Pleb check starting...")

        guild = self.bot.get_guild(int(server))
        if guild is None:
            return
        role = guild.get_role(int(pleb_role))
        count = 0
        plebs = role.members
        if ctx is not None:
            await ctx.send(f"There are {len(plebs)} people to check.")
        in_server = 0
        for member in plebs:
            count += 1
            if ctx is not None:
                if count % 100 == 0:
                    await ctx.send(f"{count} members checked")
                    
            if await db.islinked(member.id):
                smmoid = await db.get_smmoid(member.id)
                isPleb = await api.pleb_status(smmoid)

                if isPleb is None:  
                    logging.error("THE API IS STUPID")
                    continue
                elif isPleb is True:
                    continue
            
            if member._roles.has(832878414839021598):
                await member.remove_roles(role)  # remove pleb role
            
        if ctx is not None:
            await ctx.send(f"Pleb check finished! {in_server} linked members not in this server")

    @tasks.loop(hours=3, reconnect=True)
    async def update_all_plebs(self):
        await self.plebcheck(None)
        return

    @update_all_plebs.before_loop
    async def before_pleb(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    if config.main_acct:
        await bot.add_cog(Pleb(bot))
        logger.info("Pleb Cog Loaded")
