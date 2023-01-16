import discord
from discord import Embed, app_commands
from discord.ext import commands
from util import checks
from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.cooldowns import BucketType
import logging
import database as db
import api
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
    async def findmentions(self, ctx: Context, channel: discord.TextChannel, messageid: int):
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
            
    @app_commands.command(name="Send Gold", description="Generate a link to the web app 'Send Gold' page if the mentioned user is linked")
    @commands.cooldown(1, 30, BucketType.guild)
    async def sendgold(self, interaction: discord.Interaction, members: commands.Greedy[discord.Member]):
        out = ""
        await interaction.response.defer(thinking=True)
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if smmoid is not None:
                if await api.safemode_status(smmoid):
                    out += f"{member.display_name}: <https://web.simple-mmo.com/sendgold/{smmoid}>\n"
                else:
                    out += f"{member.display_name}: <https://web.simple-mmo.com/sendgold/{smmoid}> -- Not in safemode\n"
            else:
                out += f"{member.display_name} is not linked. No gold for them\n"

        await interaction.followup.send(out)

    @app_commands.command(name='mushroom', description="Sends the link so people can easily send you mushrooms")
    @checks.is_verified()
    @commands.cooldown(1, 30, BucketType.member)
    async def mushroom(self, interaction: discord.Interaction):
        smmoid = await db.get_smmoid(interaction.author.id)
        await interaction.response.send_message(f"Send me mushrooms :) <https://web.simple-mmo.com/senditem/{smmoid}/611>")

    @app_commands.command(name="Item Link", description="Generates the link to send an item to any number of users who are linked.")
    @commands.cooldown(1, 30, BucketType.member)
    async def give(self, interaction: discord.Interaction, itemid: int, members: commands.Greedy[discord.Member]):
        await interaction.response.defer(thinking=True)
        out = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)
            if smmoid is not None:
                out += f"{member.display_name}: <https://web.simple-mmo.com/senditem/{smmoid}/{itemid}>\n"
            else:
                out += f"{member.display_name} is not linked\n"
        await interaction.followup.send(out)

    @app_commands.command(description="Generates the trade link for linked members")
    @commands.cooldown(1, 30, BucketType.member)
    async def trade(self, interaction: discord.Interaction, members: commands.Greedy[discord.Member]):
        await interaction.response.defer(thinking=True)
        out = ""
        for member in members:
            smmoid = await db.get_smmoid(member.id)

            if smmoid is not None:
                out += f"{member.display_name}: <https://web.simple-mmo.com/trades/view-all?user_id={smmoid}>\n"
            else:
                out += f"{member.display_name} is not linked\n"
        await interaction.followup.send(out)
            
    @commands.cooldown(1, 300, BucketType.guild)
    @app_commands.command()
    async def topic(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        async with aiofiles.open("assets/starters.txt", mode='r') as f:
            content = await f.read()

        content = content.splitlines()
        line = random.choice(content)

        await interaction.followup.send(line)

    
    # TODO Make an app_command
    @app_commands.command()
    @checks.is_verified()
    async def mytoken(self,interaction: discord.Interaction):
        token = await db.get_yearly_token(interaction.author.id)
        if not token:
            letters = string.ascii_letters
            token = ''.join(random.choice(letters)
                                        for i in range(16))
            await db.update_yearly_token(interaction.author.id, token)
      
        
            await interaction.response.send_message(f"Your access token is: `{token}`. Keep this secret and do not share it with anyone else",ephemeral=True)
           
        

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