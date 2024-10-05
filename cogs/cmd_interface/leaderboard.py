import discord
from discord import app_commands
from discord.ext import commands
from lib.embed.interactable_leaderboard_embed import RankingView, InteractableLeaderboardEmbed
from utils.llc_datetime import LLCMonth
from utils.asset import Assets

role_list = ["Leetcoder of the Month", "LLClass Student", "Core Members", "Bot Developer"]


class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    rank_group = app_commands.Group(name = "leaderboard", description = "Ranking Group")

    @rank_group.command(name="current", description="Take a look at LLC's Hall of Fame")
    @app_commands.describe(by_role="User sorted by role")
    @app_commands.choices(
        by_role=[app_commands.Choice(name=role, value=role) for role in role_list]
    )
    async def _leaderboard_current(self, interaction: discord.Interaction, by_role: app_commands.Choice[str] = None):
        await interaction.response.defer(thinking=True)
        # Update current month name
        month = LLCMonth()
        title = f"{month.month_string()} ranking {month.date_range()}\n"

        user_list = self.client.db_api.read_current_month_leaderboard()

        user_list, title = await self.filter_by_role(interaction, user_list, by_role, title)

        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(title, user_list, pages_count, embed_limit)
        embed = InteractableLeaderboardEmbed(title, user_list, 1, pages_count, embed_limit, interaction)

        await interaction.followup.send(embed=embed, view=view)
        view.response = await interaction.original_response()
    
    @rank_group.command(name="previous", description="Take a look at LLC's previous Hall of Fame")
    @app_commands.describe(by_role="User sorted by role")
    @app_commands.choices(
        by_role = [app_commands.Choice(name=role, value=role) for role in role_list]
    )
    async def _leaderboard_previous(self, interaction: discord.Interaction, by_role: app_commands.Choice[str] = None):
        await interaction.response.defer(thinking = True)
        month = LLCMonth(previous=True)
        title = f"{month.month_string()} ranking {month.date_range()}\n"

        user_list = self.client.db_api.read_last_month_leaderboard()

        user_list, title = await self.filter_by_role(interaction, user_list, by_role, title)

        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(title, user_list, pages_count, embed_limit)
        embed = InteractableLeaderboardEmbed(title, user_list, 1, pages_count, embed_limit, interaction)

        await interaction.followup.send(embed=embed, view=view)
        view.response = await interaction.original_response()
    # will definitely need a help guide. Also streak count, ...

    async def filter_by_role(self, interaction, user_list, by_role, title):
        if by_role is not None:
            guild = interaction.guild
            role = discord.utils.get(guild.roles, name=by_role.value)
            user_list = [user for user in user_list if role in guild.get_member(int(user['discordId'])).roles]
            role_emoji = Assets.role_emojies.get(str(role.id), "")
            title += (' ' * ((len(title) - len(by_role.value)) // 2)) 
            title += f"(filtered by: {role_emoji} {by_role.value})"
        return user_list, title

async def setup(client):
    await client.add_cog(Leaderboard(client), guilds=[discord.Object(id=client.config['serverId'])])
