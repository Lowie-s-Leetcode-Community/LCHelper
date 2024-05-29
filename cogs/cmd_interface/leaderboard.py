import discord
import sys
from discord import app_commands
from discord.ext import commands
import datetime
import typing
from utils.asset import Assets
import traceback
import aiohttp
import json
from lib.embed.interactable_leaderboard_embed import RankingView, InteractableLeaderboardEmbed
class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    rank_group = app_commands.Group(name = "leaderboard", description = "Ranking Group")
    @rank_group.command(name = "current", description = "Take a look at LLC's Hall of Fame")
    async def _leaderboard_current(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        # Update current month name
        title = "Current month ranking"
        user_list = self.client.db_api.read_current_month_leaderboard()
        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(title, user_list, pages_count, embed_limit)
        embed = InteractableLeaderboardEmbed(title, user_list, 1, pages_count, embed_limit, interaction)

        await interaction.followup.send(embed=embed, view=view)
        view.response = await interaction.original_response()
    
    @rank_group.command(name = "previous", description = "Take a look at LLC's previous Hall of Fame")
    async def _leaderboard_previous(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        # Update current month name
        title = "Previous month ranking"
        user_list = self.client.db_api.read_last_month_leaderboard()
        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(title, user_list, pages_count, embed_limit)
        embed = InteractableLeaderboardEmbed(title, user_list, 1, pages_count, embed_limit, interaction)

        await interaction.followup.send(embed=embed, view=view)
        view.response = await interaction.original_response()
    # will definitely need a help guide. Also streak count, ...

async def setup(client):
    await client.add_cog(Leaderboard(client), guilds=[discord.Object(id=client.config['serverId'])])
