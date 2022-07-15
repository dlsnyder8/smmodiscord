import discord
from discord.ext import commands
from util import checks, log
import api
import logging
import database as db
from discord.ext.commands.cooldowns import BucketType
import random
import asyncio
import time

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Arcade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['arc'], hidden=True)
    async def arcade(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @commands.command()
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 5, BucketType.member)
    async def slots(self, ctx):
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

        user = await db.user_info(ctx.author.id)
        if user.tokens > 0:
            current_tokens = await db.update_arcade_tokens(ctx.author.id, -1)
        else:
            await ctx.reply("You are out of tokens!")
            return

        a1 = random.choices(options, weights=(40, 25, 17, 10, 5, 2, 1))[0]
        a2 = random.choices(options, weights=(40, 25, 17, 10, 5, 2, 1))[0]
        a3 = random.choices(options, weights=(40, 25, 17, 10, 5, 2, 1))[0]
        if a1 == a2 == a3:
            # Award user tickets
            current_tickets = await db.update_arcade_tickets(ctx.author.id, prizes[a1])
            embed = discord.Embed(title="WINNER!")
            embed.description = f'{a1} {a2} {a3}'
            embed.color = 0x008e64
            await ctx.reply(f"You have won {prizes[a1]} :tickets: and you currently have {current_tickets} :tickets:", embed=embed)

        else:
            embed = discord.Embed(title="Try Again")
            embed.description = f'{a1} {a2} {a3}'
            embed.color = 0xff0333
            await ctx.reply(f"You have {current_tokens} :coin: remaining", embed=embed)

    @commands.command()
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 5, BucketType.member)
    async def coinflip(self, ctx, choice: str = None):
        user = await db.user_info(ctx.author.id)
        if user.tokens <= 0:
            await ctx.reply("You are out of tokens")
            return

        await ctx.reply(f'Please select `heads` or `tails` and type your choice into this channel')
        choices = ['heads', 'tails']

        def check(m):
            return m.content.lower() in choices and ctx.author == m.author and ctx.channel == m.channel

        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.reply("You waited too long to select an option and the game has timed out")
            return

        current_tokens = await db.update_arcade_tokens(ctx.author.id, -1)

        choice = msg.content.lower()

        cf = random.choice(['heads', 'tails'])
        if choice != cf:
            embed = discord.Embed(title="Try Again!")
            embed.description = f"The coin was {cf}. Sorry!"
        else:
            current_tickets = await db.update_arcade_tickets(ctx.author.id, 2)
            embed = discord.Embed(title="Winner!")
            embed.description = f"Congratulations you have won 2 :tickets: and you currently have {current_tickets} :tickets:"

        await ctx.reply(f"You have {current_tokens} :coin: left", embed=embed)

    @commands.command()
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 15, BucketType.member)
    async def timing(self, ctx):
        user = await db.user_info(ctx.author.id)
        if user.tokens <= 0:
            await ctx.reply("You are out of tokens!")
            return

        embed = discord.Embed(title="Start perfect timing?")
        embed.description = f"""You are about to start a game of perfect timing. 
                                The goal of the game is to respond as close to 10 seconds as possible after the prompt.
                                Anything that happens before 10 seconds will not count.
                                The game will start once you respond with `confirm`. If you don't want to play, just wait and let the prompt timeout."""

        await ctx.reply(embed=embed)

        def check(m):
            return m.content.lower() in ['confirm'] and m.channel == ctx.channel and m.author == ctx.author

        try:
            await self.bot.wait_for('message', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await ctx.reply("Game has been cancelled")
            return

        cur_tokens = await db.update_arcade_tokens(ctx.author.id, -1)
        start_time = time.time()
        embed = discord.Embed(title="Game has started!",
                              description="Type `now` in chat as close to 10 seconds after this prompt as possible.")
        await ctx.reply(embed=embed)

        def check2(m):
            return m.content.lower() in ['now'] and m.channel == ctx.channel and m.author == ctx.author
        try:
            await self.bot.wait_for('message', timeout=20, check=check2)
        except asyncio.TimeoutError:
            await ctx.reply("Too much time has passed. 0 :tickets: awarded")
            return

        pure_time = time.time() - start_time
        elapsed = float(f'{pure_time-10:.2f}')

        if elapsed < 0.0 or elapsed > 1.0:
            tickets = 0
        elif elapsed == 0.00:
            tickets = 300
        elif elapsed <= 0.05:
            tickets = 100
        elif elapsed <= 0.1:
            tickets = 25
        elif elapsed <= 0.25:
            tickets = 5
        elif elapsed <= 0.5:
            tickets = 2
        elif elapsed <= 1.0:
            tickets = 1

        cur_tickets = await db.update_arcade_tickets(ctx.author.id, tickets)
        embed = discord.Embed(
            title="Congratulations!", description=f"You responded in {pure_time} seconds and were awarded {tickets} :tickets:. You now have {cur_tickets} :tickets:")
        if tickets == 0:
            embed.title = "Better luck next time!"

        await ctx.reply(f"You have {cur_tokens} :coin: remaining", embed=embed)

    @commands.command(aliases=['rps'])
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 5, BucketType.member)
    async def rockpaperscissors(self, ctx):
        chan = ctx.channel
        author = ctx.author
        options = ['rock', 'paper', 'scissors']
        user = await db.user_info(ctx.author.id)
        if user.tokens <= 0:
            await ctx.reply("You are out of tokens!")
            return

        def check(m):
            return m.content.lower() in options and m.channel == chan and m.author == author

        await ctx.reply("Game has started. Please respond with `rock`, `paper`, or `scissors` to play")
        try:
            msg = await self.bot.wait_for('message', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await ctx.reply("You did not respond in time.")
            return

        cur_tokens = await db.update_arcade_tokens(ctx.author.id, -1)

        cpu_pick = random.choice(options)
        hum_pick = msg.content.lower()

        win = None
        if cpu_pick == hum_pick:
            await db.update_arcade_tokens(ctx.author.id, 1)
            await ctx.reply(f"You tied and your token has been refunded. Try again. You have {cur_tokens + 1} :coin:")
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
            await ctx.reply("Something went wrong")
            return

        if win:
            embed = discord.Embed(title="Winner!")
            embed.description = f"You chose {hum_pick}, which beats {cpu_pick}. Congrats!"

            cur_tickets = await db.update_arcade_tickets(ctx.author.id, 3)
            await ctx.reply(f"You won 3 :tickets:. You now have {cur_tickets} :tickets:", embed=embed)
        else:
            embed = discord.Embed(
                title="Try Again!", description=f"You chose {hum_pick}, which lost to {cpu_pick}")
            await ctx.reply(f"You have {cur_tokens} :coin: remaining", embed=embed)

    @commands.command()
    @checks.is_verified()
    @checks.in_main()
    @commands.cooldown(1, 5, BucketType.member)
    async def diceroll(self, ctx):
        user = await db.user_info(ctx.author.id)
        if user.tokens <= 0:
            await ctx.reply(f"You don't have enough tokens to play!")
            return
        await ctx.reply("Reply with a number 1 through 6")
        options = ['1', '2', '3', '4', '5', '6']

        def check(m):
            return m.author == ctx.author and ctx.channel == m.channel and m.content.lower() in options

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=20.0)

        except asyncio.TimeoutError:
            await ctx.reply("You waited too long to say anything")
            return

        cur_tokens = await db.update_arcade_tokens(ctx.author.id, -1)
        hum_pick = msg.content.lower()
        cpu_pick = random.choice(options)

        if hum_pick == cpu_pick:
            cur_tickets = await db.update_arcade_tickets(ctx.author.id, 6)
            embed = discord.Embed("Winner!")
            embed.description(
                f"Your stupendous choice of {hum_pick} has won yourself 6 tickets")
            await msg.reply(f"You now have {cur_tickets} :tickets:", embed=embed)

        else:
            embed = discord.Embed(title="Try Again!")
            embed.description = f"The computer chose {cpu_pick}! You have {cur_tokens} :coin: remaining."
            await msg.reply(embed=embed)

    @arcade.command()
    @checks.is_verified()
    async def profile(self, ctx, member: discord.Member = None):
        user = await db.user_info(ctx.author.id if member is None else member.id)
        if user is None:
            await ctx.send("That user is not linked")
            return

        embed = discord.Embed(title='Arcade Profile')
        embed.description = f"Profile information for: {ctx.author.mention if member is None else member.mention}"
        embed.add_field(name="Tokens", value=f"{user.tokens} :coin:")
        embed.add_field(name="Tickets", value=f"{user.tickets} :tickets:")
        await ctx.reply(embed=embed)

    @arcade.command(aliases=['addtoken', 'addtokens'])
    @checks.is_owner()
    async def token_add(self, ctx, tokens: int, members: commands.Greedy[discord.Member]):

        for member in members:
            current_tokens = await db.update_arcade_tokens(member.id, tokens)
            embed = discord.Embed(
                title='Tokens Changed', description=f'{member.mention} now has {current_tokens} :coin:')
            await ctx.send(embed=embed)

    @arcade.command(aliases=['addticket', 'addtickets'])
    @checks.is_owner()
    async def ticket_add(self, ctx, tokens: int, members: commands.Greedy[discord.Member]):
        for member in members:
            current_tokens = await db.update_arcade_tickets(member.id, tokens)
            embed = discord.Embed(
                title='Tokens Changed', description=f'{member.mention} now has {current_tokens} :tickets:')
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Arcade(bot))
    print("Arcade Cog Loaded")
