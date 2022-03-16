import discord
from discord.ext import commands, tasks
from discord import Embed
from discord.utils import get
from smmolib import checks
from smmolib import database as db
import random
import string
from smmolib import api
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

    @commands.guild_only()
    @commands.command(description="Connects your Discord account with your SMMO account", usage="[SMMO-ID]")
    async def verify(self, ctx, *args):
        # needs 1 arg, smmo id
        if len(args) != 1:
            await ctx.send(embed=Embed(title="Verification Process",
                                       description="1) Please find your SMMO ID by running `+us YourNameHere` or navigating to your profile on web app and getting the 4-6 digits in the url\n2) Run `&verify SMMOID`\n3) Add the verification key to your motto, then run `&verify SMMOID` again"))
            return

        guild = await self.bot.fetch_guild(444067492013408266)

        if guild is None:
            await ctx.send("Bot is not in Main SMMO Server")
            return

        smmoid = args[0]

        try:
            smmoid = int(smmoid)
        except:
            await ctx.send("Argument must be a number")
            return

        # check if verified
        if(await db.is_verified(smmoid)):
            await ctx.send("This account has already been linked to a Discord account.")
            return

        if(await db.islinked(ctx.author.id) is True):
            await ctx.send(embed=Embed(title="Already Linked", description=f"Your account is already linked to an SMMO account. If you need to remove this, contact <@{dyl}> on Discord."))
            return

        # check if has verification key in db
        key = await db.verif_key(smmoid, ctx.author.id)
        if(key is not None):

            profile = await api.get_all(smmoid)
            motto = profile['motto']
            ispleb = profile['membership'] == 1
            # motto = await api.get_motto(smmoid)
            # ispleb = await api.pleb_status(smmoid)

            if motto is None:
                await ctx.send(f'Something went wrong. Please contact <@{dyl}> on Discord for help')
                return
            if(key in motto):
                await db.update_verified(smmoid, True)
                if ctx.guild.id == 710258284661178418:
                    await ctx.send("You are now verified. If you're in Friendly, please run `&join` to be granted access to guild channels. You can remove the verification key from your motto.")
                else:
                    await ctx.send('You are now verified! You can remove the verification key from your motto.')
                if ispleb:

                    plebid = (await db.server_config(guild.id)).pleb_role
                    print("plebid is:", plebid)
                    await ctx.author.add_roles(guild.get_role(int(plebid)))

                    channel = self.bot.get_channel(607943777084243973)
                    await channel.send(f"Welcome {ctx.author.mention} to the super secret Supporter chat. Remember to take your shoes off and no running is allowed :)")

                return

            await ctx.reply(f"Verification Failed. You are trying to connect your account to {profile['name']}. Your verification key is: `{key}`")
            await ctx.send(f'Please add this to your motto and run `{ctx.prefix}verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>')
            return

        else:
            # key in DB, but someone else tried to add it. Generate new key
            if(await db.key_init(smmoid) is not None):
                await ctx.send("Someone tried to verify with your ID. Resetting key....")
                letters = string.ascii_letters
                key = "SMMO-" + ''.join(random.choice(letters)
                                        for i in range(8))
                await db.update_pleb(smmoid, ctx.author.id, key)
                await ctx.reply(f'Your new verification key is: `{key}`')
                await ctx.send(f'Please add this to your motto and run `{ctx.prefix}verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>')
                return

            # no key in db, generate and add
            # generate verification key, add to db, tell user to add to profile and run command again
            else:
                letters = string.ascii_letters
                key = "SMMO-" + ''.join(random.choice(letters)
                                        for i in range(8))
                await db.add_new_pleb(smmoid, ctx.author.id, key)
                await ctx.reply(f'Your verification key is: `{key}` \nPlease add this to your motto and run `{ctx.prefix}verify {smmoid}` again!\n <https://web.simple-mmo.com/changemotto>')
                return

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

    @tasks.loop(hours=3)
    async def update_all_plebs(self):
        await self.plebcheck()
        return

    @update_all_plebs.before_loop
    async def before_pleb(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Pleb(bot))
    print("Pleb Cog Loaded")
