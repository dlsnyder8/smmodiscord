import discord
from discord import app_commands
from discord.embeds import Embed
import database as db
import api

dyl = 332314562575597579

def is_owner():
    async def predicate(interaction: discord.Interaction):
        if(interaction.user.id == dyl):
            return True
        else:
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Not dyl",
                        description="You must be dyl to run this command",
                        color=0xff0000
                    ), ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Not dyl",
                        description="You must be dyl to run this command",
                        color=0xff0000
                    ), ephemeral=True
                )
            
            return False
    return app_commands.check(predicate)


def is_verified():
    async def predicate(interaction: discord.Interaction):
        smmoid = await db.get_smmoid(interaction.user.id)
        if not await db.is_verified(smmoid):
            embed = discord.Embed(
                title="Not Verified",
                description=f"You have not been verified. Run `/verify <smmoid>` to start the process",
                color=0x00ff00)
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
            
            return False
        return True

    return app_commands.check(predicate)

def premium_server():
    async def predicate(interaction: discord.Interaction):
        if await db.premium_server(interaction.guild.id):
            return True
        else:
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Not Premium",
                        description="This is a premium only command. Interested in learning more? -> `/premium`",
                        color=0xff0000
                    )
                )
            else:
                # Convert to discord.Embed
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Not Premium",
                        description="This is a premium only command. Interested in learning more? -> `/premium`",
                        color=0xff0000
                    )
                )
            return False
    return app_commands.check(predicate)


def server_configured():
    async def predicate(interaction: discord.Interaction):
        if await db.server_added(interaction.guild.id):
            return True

        if interaction.response.is_done():
            message = await interaction.followup.send(
                embed=discord.Embed(
                    title="Not Configured",
                    description=f"This server is not initialized. Contact a server admin about this or run `/config init` to setup the server if you are an admin",
                    color=0xff0000
                ), ephemeral=True
            )
        else:
            message = await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Configured",
                    description=f"This server is not initialized. Contact a server admin about this or run `/config init` to setup the server if you are an admin",
                    color=0xff0000
                ), ephemeral=True
            )
            
        await message.delete(delay=10)
        return False
    return app_commands.check(predicate)

def is_leader():
    async def predicate(interaction: discord.Interaction):
        smmoid = (await db.get_smmoid(interaction.user.id))
        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await interaction.response.send_message("You are not in a guild")
            return

        members = await api.guild_members(guildid)
        for member in members:
            if member["user_id"] == smmoid:
                if member["position"] == "Leader":
                    if await db.is_leader(interaction.user.id):
                        return True
                    else:
                        embed = discord.Embed(
                            title="Not Verified",
                            description=f"You have not been verified. Run `/gm connect` if you're a guild leader",
                            color=0x00ff00)

                        await interaction.response.send(
                            embed=embed
                        )
                        return False
                else:
                    await interaction.response.send(f"You are only a member of your guild. If you want the Ambassador role, your guild leader will need to connect and run `/g aa <ID/@mention>`")
                    return False

        await interaction.response.send("The code is probably broken. Cry to dyl")
    return app_commands.check(predicate)


def is_admin():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id == dyl:
            return True
        if interaction.user.guild_permissions.administrator:
            return True
        else:
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=Embed(
                        title="Not Enough Permissions",
                        description="You must be an administrator to run this command"
                    ), ephemeral=True)
            else:
                await interaction.response.send_message(embed=Embed(
                    title="Not Enough Permissions",
                    description="You must be an administrator to run this command"
                ), ephemeral=True)
            return False
    return app_commands.check(predicate)


def is_guild_banned():
    async def predicate(interaction: discord.Interaction):
        return not await db.is_banned(interaction.user.id)
    return app_commands.check(predicate)