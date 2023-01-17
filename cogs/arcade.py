import discord
from discord import app_commands
from discord.ext import commands
from util import checks, log, app_checks
import logging
import database as db
from discord.ext.commands.cooldowns import BucketType
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Arcade(commands.GroupCog, name="Arcade"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()


    @app_commands.command()
    @app_checks.is_verified()
    @commands.cooldown(1, 5, BucketType.member)
    async def slots(self, interaction: discord.Interaction):
        prizes = {':yen:': 5,
                  ':dollar:': 10,
                  ':euro:': 20,
                  ':pound:': 50,
                  ':coin:': 75,
                  ':moneybag:': 150,
                  ':gem:': 300}

        options = [':yen:',
                   ':dollar:',
                   ':euro:',
                   ':pound:',
                   ':coin:',
                   ':moneybag:',
                   ':gem:']

        user = await db.user_info(interaction.author.id)
        if user.tokens > 0:
            current_tokens = await db.update_arcade_tokens(interaction.author.id, -1)
        else:
            await interaction.response.send_message("You are out of tokens!")
            return

        a1 = random.choices(options, weights=(40, 25, 17, 10, 5, 2, 1))[0]
        a2 = random.choices(options, weights=(40, 25, 17, 10, 5, 2, 1))[0]
        a3 = random.choices(options, weights=(40, 25, 17, 10, 5, 2, 1))[0]
        if a1 == a2 == a3:
            # Award user tickets
            current_tickets = await db.update_arcade_tickets(interaction.author.id, prizes[a1])
            embed = discord.Embed(title="WINNER!")
            embed.description = f'{a1} {a2} {a3}'
            embed.color = 0x008e64
            await interaction.response.send_message(f"You have won {prizes[a1]} :tickets: and you currently have {current_tickets} :tickets:", embed=embed)

        else:
            embed = discord.Embed(title="Try Again")
            embed.description = f'{a1} {a2} {a3}'
            embed.color = 0xff0333
            await interaction.response.send_message(f"You have {current_tokens} :coin: remaining", embed=embed)

    @app_commands.command()
    @app_checks.is_verified()
    @commands.cooldown(1, 5, BucketType.member)
    @app_commands.choices(choice=[
        app_commands.Choice(name='Heads',value='heads'),
        app_commands.Choice(name='Tails',value='tails')
    ])
    async def coinflip(self, interaction: discord.Interaction, choice: app_commands.Choice[str]):
        user = await db.user_info(interaction.author.id)
        if user.tokens <= 0:
            await interaction.response.send_message("You are out of tokens")
            return
        
        current_tokens = await db.update_arcade_tokens(interaction.author.id, -1)
        choice = choice.value
        cf = random.choice(['heads', 'tails'])
        if choice != cf:
            embed = discord.Embed(title="Try Again!")
            embed.description = f"The coin was {cf}. Sorry!"
        else:
            current_tickets = await db.update_arcade_tickets(interaction.author.id, 2)
            embed = discord.Embed(title="Winner!")
            embed.description = f"Congratulations you have won 2 :tickets: and you currently have {current_tickets} :tickets:"

        await interaction.response.send_message(f"You have {current_tokens} :coin: left", embed=embed)

    # @app_commands.command()
    # @app_checks.is_verified()
    # @commands.cooldown(1, 15, BucketType.member)
    # async def timing(self, interaction: discord.Interaction):
    #     user = await db.user_info(interaction.author.id)
    #     if user.tokens <= 0:
    #         await interaction.response.send_message("You are out of tokens!")
    #         return

    #     embed = discord.Embed(title="Start perfect timing?")
    #     embed.description = f"""You are about to start a game of perfect timing. 
    #                             The goal of the game is to respond as close to 10 seconds as possible after the prompt.
    #                             Anything that happens before 10 seconds will not count.
    #                             The game will start once you respond with `confirm`. If you don't want to play, just wait and let the prompt timeout."""

    #     await interaction.response.send_message(embed=embed)

    #     def check(m):
    #         return m.content.lower() in ['confirm'] and m.channel == interaction.channel and m.author == interaction.author

    #     try:
    #         await self.bot.wait_for('message', timeout=20.0, check=check)
    #     except asyncio.TimeoutError:
    #         await interaction.response.send_message("Game has been cancelled")
    #         return

    #     cur_tokens = await db.update_arcade_tokens(interaction.author.id, -1)
    #     start_time = time.time()
    #     embed = discord.Embed(title="Game has started!",
    #                           description="Type `now` in chat as close to 10 seconds after this prompt as possible.")
    #     await interaction.response.send_message(embed=embed)

    #     def check2(m):
    #         return m.content.lower() in ['now'] and m.channel == interaction.channel and m.author == interaction.author
    #     try:
    #         await self.bot.wait_for('message', timeout=20, check=check2)
    #     except asyncio.TimeoutError:
    #         await interaction.response.send_message("Too much time has passed. 0 :tickets: awarded")
    #         return

    #     pure_time = float(f'{(time.time() - start_time):.2f}')
    #     elapsed = float(f'{(pure_time-10):.2f}')

    #     if elapsed < 0.0 or elapsed > 1.0:
    #         tickets = 0
    #     elif elapsed == 0.00:
    #         tickets = 300
    #     elif elapsed <= 0.05:
    #         tickets = 100
    #     elif elapsed <= 0.1:
    #         tickets = 25
    #     elif elapsed <= 0.25:
    #         tickets = 5
    #     elif elapsed <= 0.5:
    #         tickets = 2
    #     elif elapsed <= 1.0:
    #         tickets = 1

    #     cur_tickets = await db.update_arcade_tickets(interaction.author.id, tickets)
    #     embed = discord.Embed(
    #         title="Congratulations!", description=f"You responded in {pure_time} seconds and were awarded {tickets} :tickets:. You now have {cur_tickets} :tickets:")
    #     if tickets == 0:
    #         embed.title = "Better luck next time!"

    #     await interaction.response.send_message(f"You have {cur_tokens} :coin: remaining", embed=embed)

    @app_commands.command(aliases=['rps'])
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 5, BucketType.member)
    @app_commands.choices(choices=[
        app_commands.Choice(name='Rock',value='rock'),
        app_commands.Choice(name='Paper',value='paper'),
        app_commands.Choice(name='Scissors',value='scissors')
    ])
    async def rockpaperscissors(self, interaction: discord.Interaction, choices: app_commands.Choice[str]):
        options = ['rock', 'paper', 'scissors']
        user = await db.user_info(interaction.author.id)
        if user.tokens <= 0:
            await interaction.response.send_message("You are out of tokens!", ephemeral=True)
            return

        cur_tokens = await db.update_arcade_tokens(interaction.author.id, -1)
        cpu_pick = random.choice(options)
        hum_pick = choices.value

        win = None
        if cpu_pick == hum_pick:
            await db.update_arcade_tokens(interaction.author.id, 1)
            await interaction.response.send_message(f"You tied and your token has been refunded. Try again. You have {cur_tokens + 1} :coin:")
            return

        elif cpu_pick == 'rock':
            if hum_pick == 'paper':
                win = True
            else:
                win = False
        elif cpu_pick == 'paper':
            if hum_pick == 'scissors':
                win = True
            else:
                win = False
        else:
            if hum_pick == 'rock':
                win = True
            else:
                win = False

        if win is None:
            await interaction.response.send_message("Something went wrong")
            return

        if win:
            embed = discord.Embed(title="Winner!")
            embed.description = f"You chose {hum_pick}, which beats {cpu_pick}. Congrats!"

            cur_tickets = await db.update_arcade_tickets(interaction.author.id, 3)
            await interaction.response.send_message(f"You won 3 :tickets:. You now have {cur_tickets} :tickets:", embed=embed)
        else:
            embed = discord.Embed(
                title="Try Again!", description=f"You chose {hum_pick}, which lost to {cpu_pick}")
            await interaction.response.send_message(f"You have {cur_tokens} :coin: remaining", embed=embed)

    @app_commands.command()
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 5, BucketType.member)
    @app_commands.choices(choices=[
        app_commands.Choice(name='1',value='1'),
        app_commands.Choice(name='2',value='2'),
        app_commands.Choice(name='3',value='3'),
        app_commands.Choice(name='4',value='4'),
        app_commands.Choice(name='5',value='5'),
        app_commands.Choice(name='6',value='6')
    ])
    async def diceroll(self, interaction: discord.Interaction, choices: app_commands.Choice[str]):
        user = await db.user_info(interaction.author.id)
        if user.tokens <= 0:
            await interaction.response.send_message(f"You don't have enough tokens to play!")
            return
        options = ['1', '2', '3', '4', '5', '6']

        cur_tokens = await db.update_arcade_tokens(interaction.author.id, -1)
        hum_pick = choices.value
        cpu_pick = random.choice(options)

        if hum_pick == cpu_pick:
            cur_tickets = await db.update_arcade_tickets(interaction.author.id, 6)
            embed = discord.Embed(title="Winner!", description=f"Your stupendous choice of {hum_pick} has won yourself 6 tickets")
            await interaction.response.send_message(f"You now have {cur_tickets} :tickets:", embed=embed)

        else:
            embed = discord.Embed(title="Try Again!", description=f"The computer chose {cpu_pick}! You have {cur_tokens} :coin: remaining.") 
            await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_checks.is_verified()
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        user = await db.user_info(interaction.author.id if member is None else member.id)
        if user is None:
            await interaction.response.send_message("That user is not linked", ephemeral=True)
            return

        embed = discord.Embed(title='Arcade Profile')
        embed.description = f"Profile information for: {interaction.author.mention if member is None else member.mention}"
        embed.add_field(name="Tokens", value=f"{user.tokens} :coin:")
        embed.add_field(name="Tickets", value=f"{user.tickets} :tickets:")
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_checks.is_owner()
    async def economy(self, interaction: discord.Interaction, hidden:bool=True):
        data = await db.all_arcade_info()

        total_tokens = sum(x.tokens for x in data)
        total_tickets = sum(x.tickets for x in data)

        embed = discord.Embed(title="Arcade Economy")
        embed.add_field(name="Tickets", value=total_tickets, inline=True)
        embed.add_field(name="Tokens", value=total_tokens, inline=True)

        await interaction.response.send_message(embed=embed,ephemeral=hidden)

    @app_commands.command(name="Add Tokens")
    @checks.is_owner()
    async def token_add(self, interaction: discord.Interaction, tokens: int, members: commands.Greedy[discord.Member]):

        for member in members:
            current_tokens = await db.update_arcade_tokens(member.id, tokens)
            embed = discord.Embed(
                title='Tokens Changed', description=f'{member.mention} now has {current_tokens} :coin:')
            await interaction.response.send_message(embed=embed)

    @app_commands.command(aliases=['addticket', 'addtickets'])
    @checks.is_owner()
    async def ticket_add(self, interaction: discord.Interaction, tokens: int, members: commands.Greedy[discord.Member]):
        for member in members:
            current_tokens = await db.update_arcade_tickets(member.id, tokens)
            embed = discord.Embed(
                title='Tokens Changed', description=f'{member.mention} now has {current_tokens} :tickets:')
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Arcade(bot))
    logger.info("Arcade Cog Loaded")
