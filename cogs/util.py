import discord
from discord.ext import commands
from util import checks
from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.cooldowns import BucketType
import logging
import database as db
import aiofiles
import random
import string

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Utilities(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
        
    @commands.hybrid_command()
    @checks.is_verified()
    async def findmentions(self, ctx: Context, channel: discord.TextChannel, messageid):
        try:
            message = await channel.fetch_message(messageid)
            users = message.raw_mentions

            string = ""

            for user in users:
                string += f"{user} "

            await ctx.send(string)
        except discord.NotFound:
            await ctx.send("Message not found")

        except discord.Forbidden:
            await ctx.send("Not enough permissions")

        except discord.HTTPException:
            await ctx.send("HTTP Error")
            
    @commands.cooldown(1, 300, BucketType.guild)
    @commands.command()
    async def topic(self, ctx):
        async with aiofiles.open("assets/starters.txt", mode='r') as f:
            content = await f.read()

        content = content.splitlines()
        line = random.choice(content)

        await ctx.send(line)

    
    # TODO Make an app_command
    @commands.command()
    @checks.is_verified()
    async def mytoken(self,ctx):
        token = await db.get_yearly_token(ctx.author.id)
        if not token:
            letters = string.ascii_letters
            token = ''.join(random.choice(letters)
                                        for i in range(16))
            await db.update_yearly_token(ctx.author.id, token)
      
        try:
            await ctx.author.send(f"Your access token is: `{token}`. Keep this secret and do not share it with anyone else")
            await ctx.reply("Check your DMs for your access token!")
        except discord.Forbidden:
            await ctx.reply("I am unable to send you any DMs. Please fix your permissions :)")


    @commands.hybrid_command()
    async def premium(self, ctx: Context):
        embed = Embed(title="Premium Information")
        string = f"""Are you interested in premium? You can find more information [here](https://patreon.com/smmodyl)
                    """
        embed.description = string
        await ctx.reply(embed=embed)
        
    @commands.hybrid_command()
    async def invite(self, ctx: Context):
        embed = Embed(
            title="Invite Me!", description="You can invite me by clicking [here](https://discord.com/api/oauth2/authorize?client_id=787258388752236565&permissions=8&scope=bot)")
        await ctx.send(embed=embed)
        
        
        
async def setup(bot):
    await bot.add_cog(Utilities(bot))
    logger.info("Utilities Cog Loaded")