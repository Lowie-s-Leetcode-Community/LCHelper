import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import asyncio
import traceback
import datetime

from database_api_layer.api import db_api

class Daily(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'daily', description = "Returns Leetcode's Daily Challenge")
    async def _daily(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        info = db_api.read_latest_daily()
        url = f"https://leetcode.com/problems/{info['problem']['titleSlug']}"
        difficulty = info['problem']['difficulty']
        color = Assets.easy if difficulty == 'Easy' else Assets.medium if difficulty == 'Medium' else Assets.hard

        embed = discord.Embed(
            title = f"**{info['problem']['id']}. {info['problem']['title']}**",
            url = f"{url}",
            color = color
        )
        embed.add_field(
            name = "Difficulty",
            value = difficulty,
            inline = True
        )
        embed.add_field(
            name = "AC Rate",
            value = "100%",
            inline = True,
        )

        topics = "||" + ",".join(info['problem']['topics']) + "||"
        embed.add_field(
            name = "Topics",
            value = topics,
            inline = False
        )
        display_date = info['generatedDate'].strftime("%b %d, %Y")
        await interaction.followup.send(f"Daily Challenge - {display_date}", embed = embed)

async def setup(client):
    await client.add_cog(Daily(client), guilds=[discord.Object(id=1085444549125611530)])
