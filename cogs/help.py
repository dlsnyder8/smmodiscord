import discord
import traceback
import sys
from discord.ext import commands
from discord.ext.commands.core import command
import logging

logger = logging.getLogger('discord')


class MyHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help")
        for cog, commands in mapping.items():

            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [
                self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(
                    command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command))
        alias = command.aliases
        if alias:
            embed.add_field(
                name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):

        embed = discord.Embed(title=self.get_command_signature(group))
        alias = group.aliases
        if alias:
            embed.add_field(
                name="Aliases", value=", ".join(alias), inline=False)

        filtered = await self.filter_commands(group.commands, sort=True)
        command_signatures = [self.get_command_signature(c) for c in filtered]
        if command_signatures:
            embed.add_field(name="Commands", value="\n".join(
                command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = MyHelp(verify_checks=False)
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
    print("Help Cog Loaded")
