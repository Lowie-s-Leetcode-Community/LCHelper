import discord
from discord import app_commands
from discord.ext import commands
from lib.embed.interactable_leaderboard_embed import RankingView, InteractableLeaderboardEmbed
from utils.llc_datetime import get_month_string, get_previous_month_string, get_current_date_range, get_previous_date_range

class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    rank_group = app_commands.Group(name = "leaderboard", description = "Ranking Group")
    @rank_group.command(name = "current", description = "Take a look at LLC's Hall of Fame")
    async def _leaderboard_current(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        # Update current month name
        title = f"{get_month_string()} ranking {get_current_date_range()}"

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
        title = f"{get_previous_month_string()} ranking {get_previous_date_range()}"
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
