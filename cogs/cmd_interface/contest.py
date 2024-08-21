import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from lib.embed.contest_embed import ContestEmbed
from utils.lc_utils import LC_utils

class Contest(commands.Cog):
    def __init__(self, client):
        self.client = client

    contest_group = app_commands.Group(name="contest", description="Join contest and compete with fellow community members!")
    @contest_group.command(name = 'list', description = "List recent and upcoming Leetcode contests")
    async def _contest(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        next_contests = LC_utils.get_next_contests_info()[:4]
        embeds = list(map(lambda x: ContestEmbed(x), next_contests))
        await interaction.followup.send(f":man_technologist: :ninja: Here are the closest contests we've found!", embeds=embeds)

async def setup(client):
    await client.add_cog(Contest(client), guilds=[discord.Object(id=client.config['serverId'])])
