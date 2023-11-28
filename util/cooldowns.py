import discord
import typing

def custom_is_me(rate: int, per: float):
    def is_me(interaction: discord.Interaction) -> typing.Optional[discord.app_commands.Cooldown] | None:
        if interaction.user.id == 332314562575597579:
            return None
        else:
            return discord.app_commands.Cooldown(rate,per)
    return is_me


class BucketType():
    Member = lambda i: (i.guild_id, i.user.id)
    Guild = lambda i: (i.guild_id)