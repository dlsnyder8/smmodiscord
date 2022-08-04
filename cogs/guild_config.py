
from discord import Embed
import discord
from discord.ext import commands
from util import checks
import api
import logging
import database as db

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

dyl = 332314562575597579


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @checks.is_admin()
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            # List current config

            data = await db.server_config(ctx.guild.id)
            if data is None:
                await ctx.send(f"To view the configuration, you first need to run `{ctx.prefix}config init` to setup the server")
                return

            embed = Embed(title="Current Server Config")
            embed.description = f"""Serverid: {data.serverid}
                                Guild Role: {f'<@&{data.guild_role}>' if data.guild_role is not None else 'Not set'}
                                Non-Guild Role: {f'<@&{data.non_guild_role}>' if data.non_guild_role is not None else 'Not set'}
                                API token: {'Set' if data.api_token is not None else 'Not Set'}
                                Guild Name: {data.guild_name if data.guild_name is not None else 'Not Set'}
                                Guilds: {data.guilds}
                                Logging Channel: {f'<#{data.log_channel}>' if data.log_channel is not None else 'Not set'}
                                Welcome Channel: {f'<#{data.welcome_channel}>' if data.welcome_channel is not None else 'Not Set'}
                                **Premium**
                                Premium: {data.premium}
                                Diamond Ping: {data.diamond_ping}
                                Diamond Role: {f'<@&{data.diamond_role}>' if data.diamond_role is not None else 'Not set'}
                                Diamond Channel: {f'<#{data.diamond_channel}>' if data.diamond_channel is not None else 'Not set'}
                                """

            embed.add_field(name="Want to change these?",
                            value=f"Run `{ctx.prefix}config options` to see a list of commands to change these values")

            await ctx.send(embed=embed)
            return

    @config.command(name='init', description="Sets up bot in server", aliases=['initialize'])
    @checks.is_admin()
    async def init(self, ctx):
        guild = ctx.guild

        if await db.server_added(guild.id):
            await ctx.send("Server has already been initialized")
            return
        try:
            await db.add_server(guild.id, guild.name)
            await ctx.send(f"Server successfully initialized. To start configuring your server, please run `{ctx.prefix}config guide` to get a brief overview of the different options")
            return
        except:
            await ctx.send(f"Something went wrong. Contact <@{dyl}> on Discord for help")
            return

    @config.command()
    @checks.is_admin()
    async def guide(self, ctx):
        info = f"""Congratulations on starting your guild! To complete setting up the bot to start your member management, you need to do a few things:
        1) Tell the bot which guild members should be in -- `{ctx.prefix}help config guilds` (You can set multiple guilds if you want to include related guilds)
        2) Set your guild name -- `{ctx.prefix}help config guild_name`
        3) Start having your members verify with the bot -- `{ctx.prefix}verify` for more information on this process
           You can see which members would lose their guild role by running `{ctx.prefix}softcheck @GuildRole`. There is a 10 minute cooldown for this command
        4) Once enough members have verified, set your guild role and welcome channel in the configuration. **NOTE:** Setting a guild role will make the bot start removing roles from users who have not verified or are not in the guild.
        5) If you set a Non-Guild Member role, then the bot will attempt to remove it before giving a user the Guild role and replace it when the user's Guild role is removed
        6) Set a logging channel so that you have a record of when people join and are removed from the guild, as well as you will receive notifications here when things go wrong and for announcements
        7) Setting an API Token is optional for now, but in the future it will be required for more intensive API tasks. It is recommended to do this in a private channel in your server so other people do not get your API key.
        
        *Congratulations!* Your guild is ready to go

        For new members who join your guild, they will need to complete two steps:
        1) Verify with the bot to link their Discord and SMMO Accounts together -- `{ctx.prefix}verify` for more info
        2) Type `{ctx.prefix}join` to be given the guild role if they are in the guild.

        More info can be found by running `{ctx.prefix}config` to see your current configuration or `{ctx.prefix}config options` to see all of the commands for changing the config values
        """

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def options(self, ctx):
        options = f"""**All commands will start with {ctx.prefix}config**
                    diamonds <Diamond Ping (True/False)> <Diamond Role> <Diamond Channel>
                    guild_role <@mention guild role>
                    non_guild_role <@mention non guild role>
                    api_token <API Token> -- Use in private channel
                    guild_name <name of guild>
                    guilds <Guild1> [Guild2] [Guild3]...
                    logging <Mention channel>
                    welcome <Mention channel>
                    """

        await ctx.send(embed=Embed(title="Configuration Options", description=options))

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    @checks.premium_server()
    async def diamonds(self, ctx, active: bool = False, role: discord.Role = None, channel: discord.TextChannel = None):
        if active is False:
            await db.enable_diamond_ping(ctx.guild.id)
            await ctx.send("Diamond Pings have been disabled for this guild")
            return

        else:
            if role is None or channel is None:
                await ctx.send("You must specify both the role to be pinged and the channel to put notifications in")
                return
            await db.enable_diamond_ping(ctx.guild.id, True)
            await db.add_diamond_channel(ctx.guild.id, channel.id)
            await db.add_diamond_role(ctx.guild.id, role.id)

            await ctx.send(embed=Embed(title="Updated", description=f"Channel: {channel.mention}\nRole: {role.mention}"))

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def guild_role(self, ctx, role: discord.Role):
        await db.change_guild_role(ctx.guild.id, role.id)
        await ctx.send("Role updated")

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def non_guild_role(self, ctx, role: discord.Role):
        await db.change_non_guild_role(ctx.guild.id, role.id)
        await ctx.send("Role updated")

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def api_token(self, ctx, token: str = None):
        if token is None:
            await db.update_token(ctx.guild.id, None)
            await ctx.send("Token deleted")
            return
        token_id = await api.me(token)
        if token_id is None:
            await ctx.reply("This is not a valid API Token")
            return

        smmoid = await db.get_smmoid(ctx.author.id)
        if int(smmoid) != token_id:
            await ctx.reply("This API Token is not owned by the same account that you have connected to your Discord Account.")
            return

        await db.update_token(ctx.guild.id, token)
        await ctx.send("API Token verified")

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def guild_name(self, ctx, name: str):
        if len(name) > 64:
            await ctx.send("The name must be fewer than 64 characters")
            return

        await db.update_guild_name(ctx.guild.id, name)
        await ctx.send("Guild name updated")

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def guilds(self, ctx, guilds: commands.Greedy[int]):
        if len(guilds) < 1:
            await ctx.send("You must specify at least 1 guild. If you're having issues, you may need to remove any punctuation between numbers")
            return

        for guild in guilds:
            if guild < 1:
                await ctx.send(f"{guild} is an invalid ID")
                return
        if not all([isinstance(item, int) for item in guilds]):
            await ctx.send("One of the supplied guilds is not a valid number")
            return

        await db.update_guilds(ctx.guild.id, guilds)
        await ctx.send(f"{guilds} have been added to your config")

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def logging(self, ctx, channel: discord.TextChannel):
        await db.update_logging(ctx.guild.id, channel.id)

        await ctx.send(f"logs will now be sent to {channel.mention}")

    @config.command()
    @checks.is_admin()
    @checks.is_verified()
    @checks.server_configured()
    async def welcome(self, ctx, channel: discord.TextChannel):
        await db.update_welcome(ctx.guild.id, channel.id)

        await ctx.send(f"Welcome messages will now be sent to {channel.mention}")


def setup(bot):
    bot.add_cog(Config(bot))
    print("Config Cog Loaded")
