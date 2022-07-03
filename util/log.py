import discord
import logging
from datetime import datetime, timezone
import database as db


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def test(self, ctx, desc: str):
    await self.genlog(ctx, title="testing", desc=desc)


async def log(bot, title: str, desc: str):
    channel = bot.get_channel(790666439673643028)
    embed = discord.Embed(
        title=title,
        description=desc,
        timestamp=datetime.now(timezone.utc),
        color=0x00ff00
    )

    await channel.send(embed=embed)


async def flylog2(bot, title: str, desc: str):
    channel = bot.get_channel(770177350758563850)
    embed = discord.Embed(
        title=title,
        description=desc,
        timestamp=datetime.now(timezone.utc),
        color=0x00ff00
    )

    await channel.send(embed=embed)


async def flylog3(bot, embed):
    channel = bot.get_channel(770177350758563850)
    await channel.send(embed=embed)


async def flylog(bot, title: str, desc: str, userid):
    channel = bot.get_channel(770177350758563850)  # Actual log channel
    # channel = bot.get_channel(868565628695494716) #shit-code-only channel
    embed = discord.Embed(
        title=title,
        description=desc,
        timestamp=datetime.now(timezone.utc),
        color=0x008e64
    )
    embed.set_footer(text=f"ID: {userid}")
    await channel.send(embed=embed)


async def server_log(bot, guildid, title: str, desc: str, id=None):
    config = await db.server_config(guildid)
    channel = bot.get_channel(config.log_channel)

    embed = discord.Embed(title=title, description=desc,
                          timestamp=datetime.now(timezone.utc), color=0xff84ef)

    if id is not None:
        embed.set_footer(text=f"ID: {id}")

    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        pass


async def server_log_embed(bot, guildid, embed):
    config = await db.server_config(guildid)
    channel = bot.get_channel(config.log_channel)

    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        pass


async def errorlog(bot, embed):
    channel = bot.get_channel(943599869795397642)

    await channel.send("<@332314562575597579>", embed=embed)
    return


async def errorlognoping(bot, embed):
    channel = bot.get_channel(943599869795397642)

    await channel.send("ERROR", embed=embed)
    return


async def joinlog(bot, guild, channel):
    if channel is not None and channel.permissions_for(guild.me).create_instant_invite:
        invite = await channel.create_invite(max_age=0, max_uses=10, reason='For Bot admin to join for setup and for any issues')

    embed = discord.Embed(title='Bot Join',
                          description=f"""ID: {guild.id}
                                            Name: {guild.name}
                                            Owner: <@{guild.owner_id}>
                                            Invite: {'None' if channel is None else invite} """)
    chan = bot.get_channel(993149782975582239)
    await chan.send(embed=embed)
