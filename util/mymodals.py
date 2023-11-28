import discord
from discord import ui
import logging
import database as db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Unlink(ui.Modal, title="Unlink Confirmation"):        
        confirm = ui.TextInput(label=f'Type Confirm to unlink your discord account')
        async def on_submit(self, interaction: discord.Interaction):
            if self.confirm.value.lower() != 'confirm':
                await interaction.response.send_message("Looks like you didn't type 'confirm', so you haven't been unlinked")
                return
            smmoid = await db.get_smmoid(interaction.user.id)
            if(await db.remove_user(smmoid)):
                await interaction.response.send_message("Your account has been successfully disconnected")
                return
            await interaction.response.send_message("Something has gone wrong", ephemeral=True)
            
        async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
            logger.error(error)
            await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
            
        async def on_timeout(self, interaction: discord.Interaction) -> None:
            await interaction.response.send_message("Oops! You didn't respond in time.")
            