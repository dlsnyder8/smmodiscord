import discord
from discord import app_commands
from discord.embeds import Embed
from discord.ext import commands
import database as db

dyl = 332314562575597579

def is_owner():
    async def predicate(interaction: discord.Interaction):
        if(interaction.author.id == dyl):
            return True
        else:
            message = await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not dyl",
                    description="You must be dyl to run this command",
                    color=0xff0000
                )
            )

            await message.delete(delay=10)
            return False
    return app_commands.check(predicate)


def is_verified():
    async def predicate(interaction: discord.Interaction):
        smmoid = await db.get_smmoid(interaction.author.id)
        if not await db.is_verified(smmoid):
            embed = discord.Embed(
                title="Not Verified",
                description=f"You have not been verified. Run `/verify <smmoid>` to start the process",
                color=0x00ff00)

            await interaction.response.send_message(
                embed=embed
            )
            return False
        else:
            return True

    return app_commands.check(predicate)

def premium_server():
    async def predicate(interaction: discord.Interaction):
        if await db.premium_server(interaction.guild.id):
            return True
        else:
            await interaction.response.send_message(f"This is a premium only command. Interested in learning more? -> `/premium`")
            return False
    return app_commands.check(predicate)


def server_configured():
    async def predicate(interaction: discord.Interaction):
        if await db.server_added(interaction.guild.id):
            return True

        message = await interaction.response.send_message(f"This server is not initialized. Contact a server admin about this or run `/config init` to setup the server if you are an admin")
        await message.delete(delay=10)
        return False
    return app_commands.check(predicate)


def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.author.id == dyl:
            return True
        if interaction.message.author.guild_permissions.administrator:
            return True
        else:
            await interaction.response.send_message(embed=Embed(
                title="Not Enough Permissions",
                description="You must be an administrator to run this command"
            ), ephemeral=True)
            return False
    return app_commands.check(predicate)
