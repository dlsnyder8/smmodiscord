import discord
from discord.embeds import Embed
from discord.ext import commands
from discord import app_commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Greedy, Context
from typing import Literal, Optional
import typing
import time
import logging
import aiofiles
import api
import database as db
from util import checks

dyl = 332314562575597579
server = 444067492013408266

fly = (408, 455, 541, 482)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_owner()
    @commands.group(aliases=['a'], hidden=True, case_insensitive=True)
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
        
    @app_commands.command()
    async def choices(self, interaction: discord.Interaction, discord: discord.Member=None, userid:int=None):
        await interaction.response.send_message(discord if discord is not None else userid)
        
    @checks.is_owner()
    @commands.hybrid_command(aliases=["kill"], hidden=True)
    async def restart(self,ctx: Context):
        await ctx.send("Senpai, why you kill me :3")
        await self.close()
    
    @commands.command(description="""
                    `~` - Sync everything to current guild
                    `*` - Copy global commands to local guild
                    `^` - Clear all commands in current guild
                    """)
    @checks.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.hybrid_command()
    @checks.is_owner()
    async def togglepremium(self, ctx: Context, id: int = None):
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


    @commands.command()
    async def supporters(self, ctx: Context, delete: bool = True):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        async with ctx.typing:
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

   
    @checks.is_owner()
    @admin.command()
    async def forceremove(self, ctx: Context, smmoid: int):
        try:
            val = await db.remove_user(smmoid)
            if val:
                await ctx.send("Success!")
            else:
                await ctx.send("They weren't removed. Either they never started verification or something else.")
        except Exception as e:
            await ctx.send("Uh oh")
            raise e

    

    @checks.is_owner()
    @admin.command(hidden=True)
    async def unlink(self, ctx: Context, member: discord.Member):
        if(await db.islinked(member.id)):
            smmoid = await db.get_smmoid(member.id)
            if(await db.remove_user(smmoid)):
                await ctx.send(f"User {smmoid} successfully removed")
            else:
                await ctx.send(f"User {smmoid} was not removed")
                return
        else:
            await ctx.send("This user is not linked.")

    @checks.is_owner()
    @commands.hybrid_command(aliases=['fv'], hidden=True)
    async def forceverify(self, ctx:Context, member: discord.Member, arg: int):
        try:
            await db.add_new_pleb(arg, member.id, None, verified=True)
            await ctx.send(f"{member.name} has been linked to {arg}")
        except:
            await ctx.send(f"You messed something up or {member.name} already started the verification process. bully dyl or something to fix")

    @admin.command()
    @checks.is_owner()
    async def remove(self, ctx:Context, arg: int):
        try:
            await db.remove_user(arg)
        except Exception as e:
            await ctx.send(e)
            return

    @commands.command()
    @checks.is_owner()
    async def ping(self, ctx:Context):
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

    @admin.command(aliases=['rb'], hidden=True)
    @checks.is_owner()
    async def rollback(self, ctx: Context):
        await db.rollback()
        await ctx.send("Database Rollback in progress")
        return

    @commands.command(hidden=True)
    @checks.is_owner()
    async def reload(self, ctx, *, cog: str):
        string = f"cogs.{cog}"
        try:
            await self.bot.reload_extension(string)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} -{e}')

        else:
            await ctx.send('**SUCCESS!**')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def guildreload(self, ctx, *, cog: str):
        string = f"guildcogs.{cog}"
        try:
            await self.bot.reload_extension(string)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} -{e}')

        else:
            await ctx.send('**SUCCESS!**')

    @commands.command(hidden=True)
    @checks.is_owner()
    async def item(self, ctx:Context, arg: int, members: commands.Greedy[discord.Member]):
        string = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if(await api.pleb_status(smmoid)):  # If they a pleb
                string += f"{member.name}: <https://web.simple-mmo.com/senditem/{smmoid}/{arg}>\n"
            else:
                string += f"{member.name} is not a pleb anymore\n"

        await ctx.send(string)

    @commands.hybrid_command()
    @commands.cooldown(1, 30, BucketType.member)
    async def id(self, ctx:Context, members: commands.Greedy[discord.Member]):
        out = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if smmoid is not None:
                out += f"{member.display_name}: <https://web.simple-mmo.com/user/view/{smmoid}>\n"
            else:
                out += f"{member.display_name} is not linked\n"
        await ctx.send(out)


async def setup(bot):
    await bot.add_cog(Admin(bot))
    logger.info("Admin Cog Loaded")
