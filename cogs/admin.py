import discord
from discord.embeds import Embed
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
import asyncio
import time
import logging
import aiofiles
import random
import api
import database as db
from util import checks
import string

dyl = 332314562575597579
server = 444067492013408266

fly = (408, 455, 541, 482)


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_owner()
    @commands.group(aliases=['a'], hidden=True, case_insensitive=True)
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @commands.command()
    @checks.is_owner()
    async def togglepremium(self, ctx, id=None):
        if id is None:
            info = await db.ServerInfo(ctx.guild.id)
            id = info.serverid
        else:
            info = await db.ServerInfo(id)

        await db.set_premium(id, not info.premium)

        embed = Embed(title="Premium Status Changed",
                      description=f"The premium for server {id} has been set to {not info.premium}")
        await ctx.send(embed=embed)

    @commands.command()
    @checks.is_owner()
    async def sql(self, ctx, query: str):
        ret = await db.execute(query)

        await ctx.send(embed=Embed(title="Result", description=f"'''py\n{ret}'''"))

    @commands.cooldown(1, 300, BucketType.guild)
    @commands.command()
    async def topic(self, ctx):
        async with aiofiles.open("assets/starters.txt", mode='r') as f:
            content = await f.read()

        content = content.splitlines()
        line = random.choice(content)

        await ctx.send(line)

    @commands.command()
    @checks.is_verified()
    async def mytoken(self,ctx):
        print('hello world')
        token = await db.get_yearly_token(ctx.author.id)
        if not token:
            letters = string.ascii_letters
            token = ''.join(random.choice(letters)
                                        for i in range(16))
            await db.update_yearly_token(ctx.author.id, token)
        print(token)
        try:
            await ctx.author.send(f"Your access token is: `{token}`. Keep this secret and do not share it with anyone else")
            await ctx.reply("Check your DMs for your access token!")
        except discord.Forbidden:
            await ctx.reply("I am unable to send you any DMs. Please fix your permissions :)")
        

    @commands.command()
    async def supporters(self, ctx, delete: bool = True):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        async with aiofiles.open("assets/supporters.txt", mode='r') as f:
            content = await f.read()

        content = content.splitlines()

        embed = Embed(title="Patreon Supporters",
                      description=f"Want to support my development too? Visit my patreon [here](https://www.patreon.com/SMMOdyl)")
        embed.color = 0xF372D3
        desc = ""
        for supporter in content:
            if len(desc) > 1900:
                embed.add_field(name="⠀", value=desc)
                desc = ""

            desc += (supporter + "\n")

        if desc != "":
            embed.add_field(name="⠀", value=desc)
            msg = await ctx.send(embed=embed)
            if delete:
                await msg.delete(delay=15)

    @commands.command()
    @checks.is_verified()
    async def findmentions(self, ctx, channel: discord.TextChannel, messageid):
        try:
            message = await channel.fetch_message(messageid)
            users = message.raw_mentions

            string = ""

            for user in users:
                string += f"{user} "

            await ctx.send(string)
        except discord.NotFound:
            await ctx.send("Message not found")

        except discord.Forbidden:
            await ctx.send("Not enough permissions")

        except discord.HTTPException:
            await ctx.send("HTTP Error")

    @checks.is_owner()
    @admin.command()
    async def forceremove(self, ctx, smmoid: int):
        try:
            val = await db.remove_user(smmoid)
            if val:
                await ctx.send("Success!")
            else:
                await ctx.send("They weren't removed. Either they never started verification or something else.")
        except Exception as e:
            await ctx.send("Uh oh")
            raise e

    @commands.command()
    async def premium(self, ctx):
        embed = Embed(title="Premium Information")
        string = f"""Are you interested in premium? You can find more information [here](https://patreon.com/smmodyl)
                    """

    @commands.command()
    async def invite(self, ctx):
        embed = Embed(
            title="Invite Me!", description="You can invite me by clicking [here](https://discord.com/api/oauth2/authorize?client_id=787258388752236565&permissions=8&scope=bot)")
        await ctx.send(embed=embed)

    @checks.is_owner()
    @admin.command(hidden=True)
    async def unlink(self, ctx, member: discord.Member):
        if(await db.islinked(member.id)):
            smmoid = await db.get_smmoid(member.id)
            if(await db.remove_user(smmoid)):
                await ctx.send(f"User {smmoid} successfully removed")
            else:
                await ctx.send(f"User {smmoid} was not removed")
                return

            # if await db.is_added(member.id):  # if linked to a guild
            #     leaderrole = ctx.guild.get_role((await db.server_config).leader_role)
            #     ambassadorrole = ctx.guild.get_role((await db.server_config).ambassador_role)

            #     guildid, smmoid = await db.ret_guild_smmoid(member.id)
            #     if(await db.is_leader(member.id)):

            #         ambassadors = await db.all_ambassadors()
            #         guildambs = [
            #             x for x in ambassadors if x.guildid == guildid]

            #         print(
            #             f"{member.name} has been removed as a leader when unlinked")
            #         # if not leader, remove role and update db
            #         await member.remove_roles(leaderrole)
            #         await db.remove_guild_user(smmoid)

            #         if len(guildambs) > 0:
            #             for amb in guildambs:
            #                 user = ctx.guild.get_member(amb.discid)
            #                 print(
            #                     f"{user.name} is not an ambassador because the leader has been unlinked")
            #                 await user.remove_roles(ambassadorrole)
            #                 await db.guild_ambassador_update(amb.discid, False, 0)
            #     else:
            #         # user is an ambassador

            #         print(
            #             f"{member.name} is not an ambassador because they unlinked")
            #         await member.remove_roles(ambassadorrole)
            #         await db.remove_guild_user(smmoid)

        else:
            await ctx.send("This user is not linked.")

    @checks.is_owner()
    @commands.group(aliases=['fv'], hidden=True)
    async def forceverify(self, ctx, member: discord.Member, arg: int):
        try:
            await db.add_new_pleb(arg, member.id, None, verified=True)
            await ctx.send(f"{member.name} has been linked to {arg}")
        except:
            await ctx.send(f"You messed something up or {member.name} already started the verification process. bully dyl or something to fix")

    @admin.command()
    @checks.is_owner()
    async def remove(self, ctx, arg: int):
        try:
            await db.remove_user(arg)
        except Exception as e:
            await ctx.send(e)
            return

    @commands.command()
    @checks.is_owner()
    async def ping(self, ctx):
        start = time.perf_counter()
        message = await ctx.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(content='Pong! {:.2f}ms'.format(duration))

    @admin.command(hidden=True)
    @checks.is_owner()
    async def set_role(self, ctx, *args):

        if not await db.server_added(ctx.guild.id):
            await ctx.send("Please run `^a init` before you run this command!")
            return

        # args should only have len of 1
        if(len(args) != 1):
            await ctx.send("Incorrect Number of Arguments! \n Correct usage: ^ap [role id]")
            return
        roles = ctx.guild.roles
        roleid = args[0]

        # cleanse roleid

        if '@' in roleid:
            roleid = roleid.replace('<', '')
            roleid = roleid.replace('@', '')
            roleid = roleid.replace('>', '')
            roleid = roleid.replace('&', '')

        roleid = int(roleid)
        for role in roles:

            if role.id == roleid:
                await db.add_server_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return

        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return

    @admin.command(aliases=['rb'])
    @checks.is_owner()
    async def rollback(self, ctx):
        await db.rollback()
        await ctx.send("Database Rollback in progress")
        return

    @commands.command(hidden=True)
    @checks.is_owner()
    async def reload(self, ctx, *, cog: str):
        string = f"cogs.{cog}"
        try:
            self.bot.reload_extension(string)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} -{e}')

        else:
            await ctx.send('**SUCCESS!**')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def guildreload(self, ctx, *, cog: str):
        string = f"guildcogs.{cog}"
        try:
            self.bot.reload_extension(string)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} -{e}')

        else:
            await ctx.send('**SUCCESS!**')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def item(self, ctx, arg: int, members: commands.Greedy[discord.Member]):
        string = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if(await api.pleb_status(smmoid)):  # If they a pleb
                string += f"{member.name}: <https://web.simple-mmo.com/senditem/{smmoid}/{arg}>\n"
            else:
                string += f"{member.name} is not a pleb anymore\n"

        await ctx.send(string)

    @commands.command()
    @checks.is_owner()
    @commands.cooldown(1, 30, BucketType.member)
    async def id(self, ctx, members: commands.Greedy[discord.Member]):
        out = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if smmoid is not None:
                out += f"{member.display_name}: <https://web.simple-mmo.com/user/view/{smmoid}>\n"
            else:
                out += f"{member.display_name} is not linked\n"
        await ctx.send(out)


def setup(bot):
    bot.add_cog(Admin(bot))
    print("Admin Cog Loaded")
