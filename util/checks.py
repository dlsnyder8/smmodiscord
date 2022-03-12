import discord
from discord.embeds import Embed
from discord.ext import commands
from sqlalchemy import true
import api
import database as db


dyl = 332314562575597579


def in_main():
    async def predicate(ctx):
        if ctx.guild.id == 444067492013408266:
            return True
        else:
            await ctx.send("This command is only available in the main server")
    return commands.check(predicate)


def has_joined():
    async def predicate(ctx):
        if await db.in_fly(ctx.author.id):
            return True
        else:
            await ctx.send(embed=Embed(
                title="You need to join first",
                description=f"Before you use this command, you need to run `{ctx.prefix}join`"
            ))
            return False

    return commands.check(predicate)


def MI6():
    async def predicate(ctx):
        if ctx.author.id == dyl or ctx.author._roles.has(749919277213155379):
            return True
        else:
            return False

    return commands.check(predicate)


def in_fly_guild():
    async def predicate(ctx):
        if ctx.author.id == dyl:
            return True
        elif ctx.author._roles.has(710315282920636506):
            return True
        else:
            await ctx.send(f"You must have the Friendly role to run this command\n Try running `{ctx.prefix}join` if you are in a Friendly Guild")

    return commands.check(predicate)


def no_bot_channel():
    async def predicate(ctx):
        if ctx.channel.id == 728355657283141735:
            return False
        else:
            return True

    return commands.check(predicate)


def warinfo_linked():
    async def predicate(ctx):
        if await db.warinfo_isadded(ctx.author.id):
            return True
        else:
            await ctx.send(f"If you're linked to the bot and in Friendly, then run `{ctx.prefix}war setup <guildid>`")
            return False

    return commands.check(predicate)


def in_fly():
    async def predicate(ctx):
        if ctx.author.id == dyl:
            return True
        elif ctx.guild.id == 710258284661178418:
            return True
        else:
            await ctx.send("This command is only available in the Friendly Server")
            return False

    return commands.check(predicate)


def is_fly_admin():
    async def predicate(ctx):
        if ctx.author.id == dyl:
            return True
        elif ctx.author._roles.has(719789422178205769):
            return True
        else:
            await ctx.send(f"This command can only be run by Big Friends")
    return commands.check(predicate)


def is_owner():
    async def predicate(ctx):
        if(ctx.author.id == dyl):
            return True
        else:
            message = await ctx.send(
                embed=discord.Embed(
                    title="Not an Admin",
                    description="You must be an administrator to run this command",
                    color=0xff0000
                )
            )

            await message.delete(delay=10)
            return False

    return commands.check(predicate)


def is_verified():
    async def predicate(ctx):
        smmoid = await db.get_smmoid(ctx.author.id)
        if not await db.is_verified(smmoid):
            embed = discord.Embed(
                title="Not Verified",
                description=f"You have not been verified. Run `{ctx.prefix}verify <smmoid>` to start the process",
                color=0x00ff00)

            await ctx.send(
                embed=embed
            )
            return False
        else:
            return True

    return commands.check(predicate)


def is_leader():
    async def predicate(ctx):
        smmoid = (await db.get_smmoid(ctx.author.id))
        # get guild from profile (get_all())
        profile = await api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("You are not in a guild")
            return

        members = await api.guild_members(guildid)
        for member in members:
            if member["user_id"] == smmoid:
                if member["position"] == "Leader":
                    if await db.is_leader(ctx.author.id):
                        return True
                    else:
                        embed = discord.Embed(
                            title="Not Verified",
                            description=f"You have not been verified. Run `{ctx.prefix}g c` if you're a guild leader",
                            color=0x00ff00)

                        await ctx.send(
                            embed=embed
                        )
                        return False
                else:
                    await ctx.send(f"You are only a member of your guild. If you want the Ambassador role, your guild leader will need to connect and run `{ctx.prefix}g aa <ID/@mention>`")
                    return False

        await ctx.send("The code is probably broken. Cry to dyl")
    return commands.check(predicate)


def is_guild_banned():
    async def predicate(ctx):
        return not await db.is_banned(ctx.author.id)
    return commands.check(predicate)
