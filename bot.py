import os
from discord.ext import commands
import discord
from discord import Intents
from smmolib import checks, log
import config
import logging

# Logging setup?
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
    print("Bot Token not found in .env folder")
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
###########################
#     Local Variables     #

smmo_server = 444067492013408266
test_server = 538144211866746883
fly_server = 710258284661178418

server = smmo_server  # Change this to which ever server the bot is mainly in
bot.server = server
lib_cogs = ['admin', 'help', 'error_handler']


if not dev:
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            bot.load_extension(f'cogs.{f[:-3]}')

    lib_cogs = ['admin', 'help', 'error_handler']
    for mod in lib_cogs:
        bot.load_extension(f'smmolib.{mod}')

else:
    # bot.load_extension('cogs.event')
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            bot.load_extension(f'cogs.{f[:-3]}')

    for mod in lib_cogs:
        bot.load_extension(f'smmolib.{mod}')


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
