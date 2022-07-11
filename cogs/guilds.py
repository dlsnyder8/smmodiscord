import discord
from discord.ext import commands, tasks
from discord import Embed
from util import checks, log
import api
import database as db
import logging
import string
import random
from discord.ext.commands.cooldowns import BucketType


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

dyl = 332314562575597579


class Guilds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_member_check.start()

    @checks.server_configured()
    @commands.command(description="Connects your Discord account with your SMMO account", usage="[SMMO-ID]")
    async def verify(self, ctx, *args):
        # needs 1 arg, smmo id
        if len(args) != 1:
            await ctx.send(embed=Embed(title="Verification Process",
                                       description=f"""1) Please find your SMMO ID by navigating to your profile on web app and getting the 4-6 digits in the url or if on mobile scrolling to the bottom of your stats page
                                                        2) Run `{ctx.prefix}verify SMMOID`
                                                        3) Add the verification key to your motto, then run `{ctx.prefix}verify SMMOID` again"""))
            return

        smmoid = args[0]

        try:
            smmoid = int(smmoid)
        except ValueError:
            await ctx.send("Argument must be a number. If you typed `<123456>` literally, remove the `< >` and try again.")
            return

        # check if verified
        if(await db.is_verified(smmoid)):
            await ctx.send("This SimpleMMO account has already been linked to a Discord account.")
            return

        if(await db.islinked(ctx.author.id) is True):
            await ctx.send(embed=Embed(title="Already Linked", description=f"Your account is already linked to an SMMO account. If you need to remove this, contact <@{dyl}> on Discord."))
            return

        # check if has verification key in db
        key = await db.verif_key(smmoid, ctx.author.id)
        if(key is not None):

            profile = await api.get_all(smmoid)
            try:
                motto = profile['motto']
            except KeyError:
                await ctx.send(f"A motto cannot be found for this account. This usually means you are trying to link to a deleted account. Ask someone for help to find your SMMO ID")
                return

            if motto is None:
                await ctx.send(f'Something went wrong. Please contact <@{dyl}> on Discord for help')
                return

            if(key in motto):
                await db.update_verified(smmoid, True)
                await ctx.send("You are now verified. You can remove the verification key from your motto.")
                data = await db.server_config(ctx.guild.id)

                if data.guild_role is not None:
                    await ctx.send(f"If you're in the guild, please run `{ctx.prefix}join` to be granted access to guild channels.")

                return

            await ctx.reply(f"Verification Failed. You are trying to connect your account to **{profile['name']}**. Your verification key is: `{key}`")
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

    @commands.command(aliases=['sg', 'gold'])
    @commands.cooldown(1, 30, BucketType.guild)
    async def sendgold(self, ctx, members: commands.Greedy[discord.Member]):
        out = ""
        async with ctx.typing():
            for member in members:
                smmoid = await db.get_smmoid(member.id)
                if smmoid is not None:
                    if await api.safemode_status(smmoid):
                        out += f"{member.display_name}: <https://web.simple-mmo.com/sendgold/{smmoid}>\n"
                    else:
                        out += f"{member.display_name}: <https://web.simple-mmo.com/sendgold/{smmoid}> -- Not in safemode\n"
                else:
                    out += f"{member.display_name} is not linked. No gold for them\n"

            await ctx.send(out)

    @commands.command(aliases=['mush'])
    @checks.is_verified()
    @commands.cooldown(1, 30, BucketType.member)
    async def mushroom(self, ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        await ctx.send(f"Send me mushrooms :) <https://web.simple-mmo.com/senditem/{smmoid}/611>")

    @commands.command()
    @commands.cooldown(1, 30, BucketType.member)
    async def give(self, ctx, itemid: int, members: commands.Greedy[discord.Member]):
        out = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if smmoid is not None:
                out += f"{member.display_name}: <https://web.simple-mmo.com/senditem/{smmoid}/{itemid}>\n"
            else:
                out += f"{member.display_name} is not linked\n"
        await ctx.send(out)

    @commands.command()
    @commands.cooldown(1, 30, BucketType.member)
    async def trade(self, ctx, members: commands.Greedy[discord.Member]):
        out = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)

            if smmoid is not None:
                out += f"{member.display_name}: <https://web.simple-mmo.com/trades/view-all?user_id={smmoid}>\n"
            else:
                out += f"{member.display_name} is not linked\n"
        await ctx.send(out)

    @checks.is_verified()
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60, BucketType.user)
    @checks.server_configured()
    async def join(self, ctx):
        config = await db.server_config(ctx.guild.id)
        if config.guild_role is None:
            await ctx.send("The guild role for this server has not been set up. Please contact an administrator on this server")
            return
        if ctx.author._roles.has(config.guild_role):

            await ctx.send(f"You've already been granted the {config.guild_name} role :)")
            return

        smmoid = await db.get_smmoid(ctx.author.id)

        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("You are not in a guild")
            return

        # if user is in a fly guild....
        if guildid in config.guilds or ctx.author.id == dyl:

            roles_given = ""

            # add fly role
            try:
                await ctx.author.add_roles(ctx.guild.get_role(config.guild_role))
            except discord.Forbidden:
                await ctx.send("I am unable to add roles to this user because either I do not have proper permissions, or my role is not high enough.")
                return
            roles_given += f"<@&{config.guild_role}>"

            if config.non_guild_role is not None:
                try:
                    await ctx.author.remove_roles(ctx.guild.get_role(config.non_guild_role))
                except discord.Forbidden:
                    pass
            if config.log_channel is not None:
                await log.server_log(self.bot, ctx.guild.id, title="User has joined the guild", desc=f"**Roles given to** {ctx.author.mention}\n{roles_given}", id=ctx.author.id)
            channel = self.bot.get_channel(config.welcome_channel)
            if ctx.author.id != dyl:
                try:
                    await channel.send(f"Welcome {ctx.author.mention} to the {config.guild_name} guild!")
                except discord.HTTPException:
                    pass
                except AttributeError:
                    await ctx.reply(f'Welcome to the guild!')
                    message = await ctx.send(f"This message can be moved to another channel by using `{ctx.prefix}config update_welcome #channel`")
                    await message.delete(delay=5)

        else:
            await ctx.send("You are not in the guild. If you think this is a mistake, try contacting your guild leader")
            return

    @commands.command()
    @checks.is_admin()
    async def softcheck(self, ctx, guildrole: discord.Role = None):

        server = await db.ServerInfo(ctx.guild.id)

        guilds = server.guilds
        allmembers = []

        for x in guilds:
            allmembers.extend([x['user_id'] for x in (await api.guild_members(x, server.api_token))])

        guild = self.bot.get_guild(server.serverid)
        if guild is None:
            return

        if guildrole is None:
            guild_role = guild.get_role(server.guild_role)
        else:
            guild_role = guildrole

        if guild_role is None:
            embed = discord.Embed(title="Guild Member Check Failed",
                                  description="It appears that my config is wrong and I cannot find the guild role")
            await ctx.send(embed=embed)
            return

        removed = []
        for member in guild_role.members:
            if await db.islinked(member.id):
                smmoid = await db.get_smmoid(member.id)
                if smmoid not in allmembers:
                    removed.append(f"{member.mention}")
            else:
                removed.append(f'{member.mention}')

        if len(removed) > 0:
            embed = Embed(
                title="Users not in guild"
            )
            splitUsers = [removed[i:i+33]
                          for i in range(0, len(removed), 33)]

            for split in splitUsers:
                embed.add_field(name="Users", value=' '.join(split))
            await ctx.send(embed=embed)

        else:
            await ctx.send("Every is linked and in the guild")

    @tasks.loop(hours=4, reconnect=True)
    async def guild_member_check(self):
        ignored_servers = [710258284661178418]
        await log.log(self.bot, "Guild Member Check Started", " ")

        allservers = await db.all_servers()
        filtered = [x for x in allservers if x.guild_role is not None]
        print(filtered)

        for server in filtered:
            print(server.serverid)
            if server.serverid in ignored_servers:
                continue

            guilds = server.guilds
            allmembers = []

            for x in guilds:
                allmembers.extend([x['user_id'] for x in (await api.guild_members(x, server.api_token))])

            guild = self.bot.get_guild(server.serverid)
            if guild is None:
                continue

            await log.log(self.bot, "Guild Check", f'Checking server {guild.name} ')

            guild_role = guild.get_role(server.guild_role)

            non_guild_role = guild.get_role(server.non_guild_role)

            if guild_role is None:
                log.server_log(self.bot, server.serverid, title="Guild Member Check Failed",
                               desc="It appears that my config is wrong and I cannot find the guild role")
                continue

            removed = []
            for member in guild_role.members:
                if await db.islinked(member.id):
                    smmoid = await db.get_smmoid(member.id)
                    if smmoid not in allmembers:
                        removed.append(f"{member.mention}")
                        await member.remove_roles(guild_role, reason="User has left the guild")
                        if non_guild_role is not None:
                            await member.add_roles(non_guild_role)
                else:
                    await member.remove_roles(guild_role, reason="User has not linked")
                    removed.append(f'{member.mention}')
                    if non_guild_role is not None:
                        await member.add_roles(non_guild_role)
            if len(removed) > 0:
                embed = Embed(
                    title="Users with the guild role removed"
                )
                splitUsers = [removed[i:i+33]
                              for i in range(0, len(removed), 33)]

                for split in splitUsers:
                    embed.add_field(name="Users", value=' '.join(split))

                await log.server_log_embed(self.bot, server.serverid, embed)
                embed.title = f"Users with guild role removed for id: {server.serverid}"
                await log.embedlog(self.bot, embed)

    @guild_member_check.before_loop
    async def before_guild_member_check(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Guilds(bot))
    print("Guilds Cog Loaded")
