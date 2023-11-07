import discord
from discord import app_commands
from discord.ext import tasks, commands

import asyncio
import traceback

class ask(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name = 'ask', description = "[BETA] ask something and don't expect the answer")
    async def asking(self,
                     interaction: discord.Interaction,
                     question: str = None):
        await interaction.response.defer(thinking = True)
        # lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        message = "I'm sorry, but next time would you please stop asking me questions. In fact, please never talk to me, ping me or look at me you filthy thing"
        embed = discord.Embed(
                title = "Q&A",
                description = "Q: " + question,
                color = discord.Colour.blue()
                )
        embed.add_field(
                name = "My polite response",
                value = message,
                inline = False
                )
        await interaction.followup.send(embed = embed)
        # print(interaction.data)
        # print(question)
        original_mes = await interaction.original_response()
        await original_mes.add_reaction("👍")

async def setup(client):
    await client.add_cog(
                ask(client),
                guilds=[discord.Object(id=1085444549125611530)])
