import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from lib.embed.problem import ProblemEmbed

class Daily(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'daily', description = "Returns Leetcode's Daily Challenge")
    async def _daily(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        msg = create_daily_embed()
        await interaction.followup.send(f"Daily Challenge - {msg['display_date']}", embed = msg['embed'])

    def create_daily_embed(self):
        daily_obj = self.client.db_api.read_latest_daily_object()
        problem = daily_obj['problem']
        embed = ProblemEmbed(problem)

        display_date = daily_obj['generatedDate'].strftime("%b %d, %Y")
        return {"display_date": display_date, "embed": embed}

async def setup(client):
    await client.add_cog(Daily(client), guilds=[discord.Object(id=client.config['serverId'])])
