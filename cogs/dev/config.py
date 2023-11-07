import discord
import os
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
from utils.asset import Assets

class config(commands.Cog):
    def __init__(self, client):
        self.client = client

    
    #@app_commands.command(name = 'settings')
    #async def _settings(self, interaction: discord.Interaction):
    #    await interaction.response.defer(thinking = True)
    #
    #    embed = discord.Embed(
    #        title = "Current config for LLC",
    #        description = """
    #        `event_multiplier_weekly_bonus`: 1x
    #        `event_multiplier_topic_bonus`: 1x
    #        `event_multiplier_topic_list`: ['binary_search', 'sorting']
    #        """,
    #        color = discord.Colour.red()
    #    )
    #    await interaction.followup.send(embed = embed)
    
async def setup(client):
    await client.add_cog(config(client), guilds=[discord.Object(id=1085444549125611530)])
