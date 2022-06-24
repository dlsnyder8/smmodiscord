import os
from discord.ext import commands
import discord
from discord import Intents
import config
import logging
from util import checks, log

# Logging setup
logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

dev = False

TOKEN = config.TOKEN
DEV_TOKEN = config.DEV_TOKEN

if TOKEN is None or DEV_TOKEN is None:
    print("Bot Token not found in config file")
    quit()

if dev is True:
    TOKEN = DEV_TOKEN

# Set discord intents
intents = Intents.all()
game = discord.Game("Contact dyl#8008 with questions")

if not dev:
    bot = commands.Bot(command_prefix='&', intents=intents,
                       activity=game)
else:
    bot = commands.Bot(command_prefix='&&', intents=intents,
                       activity=game)

extra_cogs = config.special_cogs
if not dev:
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            bot.load_extension(f'cogs.{f[:-3]}')
    for mod in extra_cogs:
        bot.load_extension(f'guildcogs.{mod}')

else:
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            bot.load_extension(f'cogs.{f[:-3]}')
    for mod in extra_cogs:
        bot.load_extension(f'guildcogs.{mod}')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord')
    await log.errorlognoping(bot, embed=discord.Embed(title="Bot Started", description="The bot has been restarted"))
    print(f"Tasks have been started")


@checks.is_owner()
@bot.command(aliases=["kill"], hidden=True)
async def restart(ctx):
    await ctx.send("Senpai, why you kill me :3")
    await bot.close()


bot.run(TOKEN)
