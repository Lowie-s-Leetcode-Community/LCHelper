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
        next_contests = LC_utils.get_next_contests_info()
        embed_1 = ContestEmbed(False, next_contests["weekly"])
        embed_2 = ContestEmbed(True, next_contests["biweekly"])
        embeds = [embed_1, embed_2]
        await interaction.followup.send(f":man_technologist: :ninja: Here are the closest contests we've found!", embeds=embeds)

async def setup(client):
    await client.add_cog(Contest(client), guilds=[discord.Object(id=client.config['serverId'])])
