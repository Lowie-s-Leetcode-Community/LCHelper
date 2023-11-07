import discord
from discord import app_commands
from discord.ext import tasks, commands

class poll(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name='poll',
                          description="[BETA] don't choose")
    async def polling(self,
                      interaction: discord.Interaction,
                      question: str = None):
        await interaction.response.defer(thinking = True)
        # lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        message = "test poll"
        await interaction.followup.send(message)
        original_mes = await interaction.original_response()
        await original_mes.add_reaction("👍")

async def setup(client):
    await client.add_cog(poll(client), guilds=[discord.Object(id=1085444549125611530)])
