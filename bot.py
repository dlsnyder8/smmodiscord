import os
from discord.ext import commands
import discord
from discord import Intents
import config
import logging
from util import checks, log

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dev = True

TOKEN = config.TOKEN
DEV_TOKEN = config.DEV_TOKEN
if TOKEN is None or DEV_TOKEN is None:
    logging.error("Bot Token not found in config file")
    quit()
if dev is True:
    TOKEN = DEV_TOKEN


class MyBot(commands.Bot):
    def __init__(self):
        game = discord.Game("Contact @wiredcoding with questions")
        intents = Intents.all()
        if not dev:
            super().__init__(command_prefix='&',intents=intents, activity=game)
        else:
            super().__init__(command_prefix='&&',intents=intents, activity=game)
    # Load extensions
    async def setup_hook(self):
        extra_cogs = config.special_cogs
        if not dev:
            for f in os.listdir('./cogs'):
                if f.endswith('.py') and f[:-3] not in config.ignored_cogs:
                    await self.load_extension(f'cogs.{f[:-3]}')
            for mod in extra_cogs:
                await self.load_extension(f'guildcogs.{mod}')
        else:
            for f in os.listdir('./cogs'):
                if f.endswith('.py'):
                    await self.load_extension(f'cogs.{f[:-3]}')
            for mod in extra_cogs:
                await self.load_extension(f'guildcogs.{mod}')

    async def on_ready(self):
        logging.info(f'{self.user.name} has connected to Discord')
        await log.errorlognoping(self, embed=discord.Embed(title="Bot Started", description="The bot has been restarted"))
        logging.info(f"Tasks have been started")


 
    async def on_guild_join(self,guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await log.joinlog(self, guild, channel)
                await channel.send("Thanks for inviting me! To start using my features, please run `/config setup` to add your server to my database")
                return

        await log.joinlog(self, guild, None)



bot = MyBot().run(TOKEN,root_logger=True)
