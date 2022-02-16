import discord
import traceback
import sys
from discord.ext import commands
import logging
from util.log import *



logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
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
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            message = await ctx.send(f'{ctx.command} has been disabled.')
            await ctx.message.delete(delay=5)
            await message.delete(delay=5)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing input!")

        elif isinstance(error, discord.ext.commands.CommandOnCooldown):
            if ctx.author.id != dyl:
                errorembed = discord.Embed(title="Slow your roll",
                description=f"You're on a cooldown. Please try again in {error.retry_after:.2f} Second(s)!")
                message = await ctx.send(embed=errorembed)
                await message.delete(delay=5)
                await ctx.message.delete(delay=5)


            else:
                await ctx.reinvoke()

       


        else:
            await errorlog(self.bot,embed=discord.Embed(title="Error",description=f"Ignoring exception in command {ctx.command}. Run by {ctx.author.mention} in guild {ctx.guild.name}"))

            #await ctx.send(embed=discord.Embed(title="Error",description='Ignoring exception in command {}:'.format(ctx.command)))
            #await ctx.send(embed=discord.Embed(title="Traceback",description=traceback.format_exc()))
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
    print("Error Handler Loaded")