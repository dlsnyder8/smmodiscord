import discord
from discord.ext import commands, tasks
from discord import Embed
from discord.utils import get
from util import checks
import database as db
import random   
import string
import api
import logging

logger = logging.getLogger('discord')


dyl = 332314562575597579


class Pleb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases = ['p'],hidden=True)
    async def pleb(self,ctx):
        if ctx.invoked_subcommand is None:
            pass

    @pleb.command()
    @checks.is_owner()
    async def ispleb(self,ctx,arg):
        smmoid = int(arg)
        ispleb = await api.pleb_status(smmoid)
        if ispleb:
            await ctx.send(f'{smmoid} is a pleb')
        else:
            await ctx.send(f'{smmoid} is not a pleb')
        return
        
    @pleb.command()
    @checks.is_owner()
    async def whois(self,ctx,*, member: discord.Member):
        id = str(member.id)
        users = db.disc_ids(id)
        for user in users:
            await ctx.send(f'user: {user[0]}, verified: {user[1]}')

    @pleb.command()
    @checks.is_owner()
    async def activeplebs(self,ctx):
        plebs = db.active_pleb()
        for pleb in plebs:
            await ctx.send(f'<@!{pleb[1]}>: {pleb[0]} has an active membership')


    @commands.guild_only()
    @commands.command(description="Connects your Discord account with your SMMO account", usage="[SMMO-ID]")
    async def verify(self,ctx, *args):
        # needs 1 arg, smmo id
        if len(args) != 1:
            await ctx.send(embed=Embed(title=f"Verification Process",
                            description="1) Please find your SMMO ID by running `+us YourNameHere` or navigating to your profile on web app and getting the 4-6 digits in the url\n2) Run `&verify SMMOID`\n3) Add the verification key to your motto, then run `&verify SMMOID` again"))
            return

        
        guild = await self.bot.fetch_guild(444067492013408266)

        if guild is None:
            await ctx.send("Bot is not in Main SMMO Server")
            return
        
        smmoid = args[0]

        try:
            int(smmoid)
        except:
            await ctx.send("Argument must be a number")
            return

        # check if verified
        if(db.is_verified(smmoid)):
            await ctx.send("This account has already been linked to a Discord account.")
            return

        if(db.islinked(str(ctx.author.id)) is True):
            await ctx.send(f"Your account is already linked to an SMMO account. If you need to remove this, contact <@{dyl}> on Discord.")
            return

        # check if has verification key in db
        key = db.verif_key(smmoid, str(ctx.author.id))
        if(key is not None):
            
            motto = await api.get_motto(smmoid)
            ispleb = await api.pleb_status(smmoid)

        
            if motto is None:
                await ctx.send(f'Something went wrong. Please contact <@{dyl}> on Discord for help')
                return
            if(key in motto):
                db.update_verified(smmoid, True)
                if ctx.guild.id == 710258284661178418:
                    await ctx.send(f"You are now verified. If you're in Friendly, please run `&join` to be granted access to guild channels. You can remove the verification key from your motto.")
                else:
                    await ctx.send(f'You are now verified! You can remove the verification key from your motto.')
                if ispleb:

                    plebid = db.pleb_id(guild.id)
                    print("plebid is:",plebid)
                    await ctx.author.add_roles(guild.get_role(int(plebid)))

                    channel = self.bot.get_channel(607943777084243973)
                    await channel.send(f"Welcome {ctx.author.mention} to the super secret Supporter chat. Remember to take your shoes off and no running is allowed :)")
                
                
                return

            await ctx.send(f'Verification Failed. Your verification key is: `{key}`')
            await ctx.send(f'Please add this to your motto and run `{ctx.prefix}verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>')
            return

        
        
        else:
            # key in DB, but someone else tried to add it. Generate new key
            if(db.key_init(smmoid) is not None):
                await ctx.send("Someone tried to verify with your ID. Resetting key....")
                letters = string.ascii_letters
                key= "SMMO-" + ''.join(random.choice(letters) for i in range(8))
                db.update_pleb(smmoid, str(ctx.author.id), key)
                await ctx.send(f'Verification Failed. Your verification key is: `{key}`')
                await ctx.send(f'Please add this to your motto and run `{ctx.prefix}verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>')
                return

            # no key in db, generate and add
            # generate verification key, add to db, tell user to add to profile and run command again
            else:
                letters = string.ascii_letters
                key= "SMMO-" + ''.join(random.choice(letters) for i in range(8))
                db.add_new_pleb(smmoid, str(ctx.author.id), key)
                await ctx.send(f'Your verification key is: `{key}` \nPlease add this to your motto and run `{ctx.prefix}verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>')
                return


    
            


def setup(bot):
    bot.add_cog(Pleb(bot))
    print("Pleb Cog Loaded")

