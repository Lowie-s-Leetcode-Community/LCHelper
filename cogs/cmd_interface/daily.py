import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import asyncio
import traceback
import datetime
from ..automation.intervally.daily_auto import create_daily_challenge

class Daily(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'daily', description = "Returns Leetcode's Daily Challenge")
    async def _daily(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        
        await create_daily_challenge(interaction.followup, self.client.db_api.read_latest_daily_object())

async def setup(client):
    await client.add_cog(Daily(client), guilds=[discord.Object(id=client.config['serverId'])])
