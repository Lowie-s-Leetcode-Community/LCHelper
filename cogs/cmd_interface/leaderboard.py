import discord
from discord import app_commands
from discord.ext import commands
from lib.embed.interactable_leaderboard_embed import RankingView, InteractableLeaderboardEmbed
from utils.llc_datetime import LLCMonth
from lib.embed.leaderboard_embed import role_emojies

class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    rank_group = app_commands.Group(name = "leaderboard", description = "Ranking Group")

    @rank_group.command(name = "current", description = "Take a look at LLC's Hall of Fame")
    @app_commands.describe(by_user="User sorted by role")
    @app_commands.choices(by_user=[
        app_commands.Choice(name="Leetcoder of the Month", value="Leetcoder of the Month"),
        app_commands.Choice(name="LLClass Student", value="LLClass Student"),
        app_commands.Choice(name="Core Members", value="Core Members"),
        app_commands.Choice(name="Bot Developer", value="Bot Developer"),
    ])
    async def _leaderboard_current(self, interaction: discord.Interaction, by_user: app_commands.Choice[str] = None):
        await interaction.response.defer(thinking = True)
        # Update current month name
        month = LLCMonth()
        title = f"{month.month_string()} ranking {month.date_range()}\n"

        user_list = self.client.db_api.read_current_month_leaderboard()

        user_list, title = await self.filter_by_role(interaction, user_list, by_user, title)

        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(title, user_list, pages_count, embed_limit)
        embed = InteractableLeaderboardEmbed(title, user_list, 1, pages_count, embed_limit, interaction)

        await interaction.followup.send(embed=embed, view=view)
        view.response = await interaction.original_response()
    
    @rank_group.command(name="previous", description="Take a look at LLC's previous Hall of Fame")
    @app_commands.describe(by_user="User sorted by role")
    @app_commands.choices(by_user=[
        app_commands.Choice(name="Leetcoder of the Month", value="Leetcoder of the Month"),
        app_commands.Choice(name="LLClass Student", value="LLClass Student"),
        app_commands.Choice(name="Core Members", value="Core Members"),
        app_commands.Choice(name="Bot Developer", value="Bot Developer"),
    ])
    async def _leaderboard_previous(self, interaction: discord.Interaction, by_user: app_commands.Choice[str] = None):
        await interaction.response.defer(thinking = True)
        month = LLCMonth(previous=True)
        title = f"{month.month_string()} ranking {month.date_range()}\n"

        user_list = self.client.db_api.read_last_month_leaderboard()

        user_list, title = await self.filter_by_role(interaction, user_list, by_user, title)

        embed_limit = 10
        pages_count = (len(user_list) + (embed_limit - 1)) // embed_limit
        view = RankingView(title, user_list, pages_count, embed_limit)
        embed = InteractableLeaderboardEmbed(title, user_list, 1, pages_count, embed_limit, interaction)

        await interaction.followup.send(embed=embed, view=view)
        view.response = await interaction.original_response()
    # will definitely need a help guide. Also streak count, ...

    async def filter_by_role(self, interaction, user_list, by_user, title):
        if by_user is not None:
            guild = interaction.guild
            role = discord.utils.get(guild.roles, name=by_user.value)
            user_list = [user for user in user_list if role in guild.get_member(int(user['discordId'])).roles]
            role_emoji = role_emojies.get(str(role.id), "")
            title += (' ' * ((len(title) - len(by_user.value)) // 2)) 
            title += f"(filtered by: {role_emoji} {by_user.value})"
        return user_list, title

async def setup(client):
    await client.add_cog(Leaderboard(client), guilds=[discord.Object(id=client.config['serverId'])])
