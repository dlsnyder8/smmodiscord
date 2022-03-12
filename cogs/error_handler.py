import discord
import traceback
import sys
from discord.ext import commands
import logging
from util.log import *


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

dyl = 332314562575597579


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        # error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            message = await ctx.send(f'{ctx.invoked_with} has been disabled.')
            await ctx.message.delete(delay=15)
            await message.delete(delay=1)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')
            else:
                await ctx.send("Invalid Argument")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing input!")

        elif isinstance(error, discord.ext.commands.CommandOnCooldown):
            if ctx.author.id != dyl:
                errorembed = discord.Embed(title="Slow your roll",
                                           description=f"You're on a cooldown. Please try again in {error.retry_after:.2f} Second(s)!")
                message = await ctx.send(embed=errorembed)
                await message.delete(delay=error.retry_after)
                await ctx.message.delete(delay=5)

            else:
                await ctx.reinvoke()

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Permission Denied")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot does not have enough permissions to perform that action")

        elif isinstance(error, commands.CommandInvokeError):
            error = error.original

            if isinstance(error, discord.Forbidden):

                await ctx.send(f"Discord doesn't let that happen")
                return

            if isinstance(error, discord.HTTPException):
                await ctx.send(f"HTTP Exception:\n{error.text}")
                return
            try:
                logger.error(
                    f"{error.__class__.__name__}: {error} (In {ctx.command.name})\n"
                    f"Traceback:\n{''.join(traceback.format_tb(error.__traceback__))}"
                )
            except:
                pass
            try:
                await errorlog(self.bot, embed=Embed(title=f"Something has fucked up.", description=f"Run by {ctx.author.mention} in channel {ctx.channel.mention}:\n{error}"))
            except discord.HTTPException:
                await errorlog(self.bot, embed=Embed(title="Big Uwu fucky", description="Description too big, but something really fucked up"))
            await ctx.send("Something has gone pretty hecking bad. Contact Dyl asap")

        else:
            embed = discord.Embed(
                title="Error", description=f"Ignoring exception in command {ctx.command}. Run by {ctx.author.mention} in channel {ctx.channel.mention}")
            # embed.add_field("Status", error.status)
            # embed.add_field("Discord Code",error.code)
            # embed.add_field("Error",str(dir(error)))
            await errorlognoping(self.bot, embed)

            # await ctx.send(embed=discord.Embed(title="Error",description='Ignoring exception in command {}:'.format(ctx.command)))
            # await ctx.send(embed=discord.Embed(title="Traceback",description=traceback.format_exc()))
            # traceback.print_exception(
            #     type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
    print("Error Handler Loaded")
