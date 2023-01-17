
from discord import Embed, app_commands
import discord
from discord.ext import commands
from util import checks, app_checks
import api
import logging
import database as db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dyl = 332314562575597579


class Config(commands.GroupCog, name="Guild Config"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command()
    @app_checks.is_admin()
    async def config(self, interaction: discord.Interaction):
        
        data = await db.server_config(interaction.guild.id)
        if data is None:
            await interaction.response.send_message(f"To view the configuration, you first need to run `/config init` to setup the server")
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
                            Diamond Amount: {data.diamond_amount:,} gold
                            """

        embed.add_field(name="Want to change these?",
                        value=f"Run `/config options` to see a list of commands to change these values")

        await interaction.response.send_message(embed=embed)
        return

    @app_commands.command(name='init', description="Sets up bot in server", aliases=['initialize'])
    @app_checks.is_admin()
    async def init(self, interaction: discord.Interaction):
        guild = interaction.guild

        if await db.server_added(guild.id):
            await interaction.response.send_message("Server has already been initialized")
            return
        try:
            await db.add_server(guild.id, guild.name)
            await interaction.response.send_message(f"Server successfully initialized. To start configuring your server, please run `/config guide` to get a brief overview of the different options")
            return
        except:
            await interaction.response.send_message(f"Something went wrong. Contact <@{dyl}> on Discord for help")
            return

    @app_commands.command()
    @app_checks.is_admin()
    async def guide(self, interaction: discord.Interaction):
        info = f"""Congratulations on starting your guild! To complete setting up the bot to start your member management, you need to do a few things:
        1) Tell the bot which guild members should be in -- `/help config guilds` (You can set multiple guilds if you want to include related guilds)
        2) Set your guild name -- `/help config guild_name`
        3) Start having your members verify with the bot -- `/verify` for more information on this process
           You can see which members would lose their guild role by running `/softcheck @GuildRole`. There is a 10 minute cooldown for this command
        4) Once enough members have verified, set your guild role and welcome channel in the configuration. **NOTE:** Setting a guild role will make the bot start removing roles from users who have not verified or are not in the guild.
        5) If you set a Non-Guild Member role, then the bot will attempt to remove it before giving a user the Guild role and replace it when the user's Guild role is removed
        6) Set a logging channel so that you have a record of when people join and are removed from the guild, as well as you will receive notifications here when things go wrong and for announcements
        7) Setting an API Token is optional for now, but in the future it will be required for more intensive API tasks. It is recommended to do this in a private channel in your server so other people do not get your API key.
        
        *Congratulations!* Your guild is ready to go

        For new members who join your guild, they will need to complete two steps:
        1) Verify with the bot to link their Discord and SMMO Accounts together -- `/verify` for more info
        2) Type `/join` to be given the guild role if they are in the guild.

        More info can be found by running `/config` to see your current configuration or `/config options` to see all of the commands for changing the config values
        """

        embed = discord.Embed(title="Embed Guide")
        embed.description = info
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def options(self, interaction: discord.Interaction):
        options = f"""**All commands will start with `/config`**
                    diamonds <Diamond Ping (True/False)> <Diamond Role> <Diamond Channel> <Amount>
                    guild_role <@mention guild role>
                    non_guild_role <@mention non guild role>
                    api_token <API Token> -- Use in private channel
                    guild_name <name of guild>
                    guilds <Guild1> [Guild2] [Guild3]...
                    logging <Mention channel>
                    welcome <Mention channel>
                    """

        await interaction.response.send_message(embed=Embed(title="Configuration Options", description=options))

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    @app_checks.premium_server()
    async def diamonds(self, interaction: discord.Interaction, active: bool = False, role: discord.Role = None, channel: discord.TextChannel = None, amount=2000000):
        if active is False:
            await db.enable_diamond_ping(interaction.guild.id)
            await interaction.response.send_message("Diamond Pings have been disabled for this guild")
            return

        else:
            if role is None or channel is None:
                await interaction.response.send_message("You must specify both the role to be pinged and the channel to put notifications in")
                return
            await db.enable_diamond_ping(interaction.guild.id, True)
            await db.add_diamond_channel(interaction.guild.id, channel.id)
            await db.add_diamond_role(interaction.guild.id, role.id)
            await db.change_diamond_amount(interaction.guild.id, amount)

            await interaction.response.send_message(embed=Embed(title="Updated", description=f"Channel: {channel.mention}\nRole: {role.mention}"))

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def guild_role(self, interaction: discord.Interaction, role: discord.Role):
        await db.change_guild_role(interaction.guild.id, role.id)
        await interaction.response.send_message("Role updated")

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def non_guild_role(self, interaction: discord.Interaction, role: discord.Role):
        await db.change_non_guild_role(interaction.guild.id, role.id)
        await interaction.response.send_message("Role updated")

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def api_token(self, interaction: discord.Interaction, token: str = None):
        if token is None:
            await db.update_token(interaction.guild.id, None)
            await interaction.response.send_message("Token deleted")
            return
        token_id = await api.me(token)
        if token_id is None:
            await interaction.response.send_message("This is not a valid API Token")
            return

        smmoid = await db.get_smmoid(interaction.author.id)
        if int(smmoid) != token_id:
            await interaction.response.send_message("This API Token is not owned by the same account that you have connected to your Discord Account.")
            return

        await db.update_token(interaction.guild.id, token)
        await interaction.response.send_message("API Token verified")

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def guild_name(self, interaction: discord.Interaction, name: str):
        if len(name) > 64:
            await interaction.response.send_message("The name must be fewer than 64 characters")
            return

        await db.update_guild_name(interaction.guild.id, name)
        await interaction.response.send_message("Guild name updated")

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def guilds(self, interaction: discord.Interaction, guilds: commands.Greedy[int]):
        if len(guilds) < 1:
            await interaction.response.send_message("You must specify at least 1 guild. If you're having issues, you may need to remove any punctuation between numbers")
            return

        for guild in guilds:
            if guild < 1:
                await interaction.response.send_message(f"{guild} is an invalid ID")
                return
        if not all([isinstance(item, int) for item in guilds]):
            await interaction.response.send_message("One of the supplied guilds is not a valid number")
            return

        await db.update_guilds(interaction.guild.id, guilds)
        await interaction.response.send_message(f"{guilds} have been added to your config")

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def logging(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.update_logging(interaction.guild.id, channel.id)

        await interaction.response.send_message(f"logs will now be sent to {channel.mention}")

    @app_commands.command()
    @app_checks.is_admin()
    @app_checks.is_verified()
    @app_checks.server_configured()
    async def welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await db.update_welcome(interaction.guild.id, channel.id)

        await interaction.response.send_message(f"Welcome messages will now be sent to {channel.mention}")


async def setup(bot):
    await bot.add_cog(Config(bot))
    logger.info("Config Cog Loaded")
