import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.logger import Logger
import random

from database_api_layer.api import DatabaseAPILayer

class score(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logger = Logger(client)
        self.db_api = DatabaseAPILayer(client)

    score_group = app_commands.Group(name = "score", description = "Scoring system")
    @score_group.command(name = 'add', description = "Adds score")
    @app_commands.describe(member = "Member to add scores")
    @app_commands.describe(score = "Amount of scores to add (should be positive)")
    @app_commands.describe(reason = "Reason for adding scores")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_add(self, interaction: discord.Interaction, member: discord.Member, score: int, reason: str):
        await interaction.response.defer(thinking = True)

        daily_obj = self.db_api.update_score(str(member.id), score)
        if (daily_obj == None):
            await interaction.followup.send(f"The bot is bug-ed in score add, contact bot dev")
            return

        # lc_col = self.client.DBClient['LC_db']['LC_users']
        # lc_user = lc_col.find_one({'discord_id': member.id})
        # lc_user['current_month']['score'] += score
        # lc_user['all_time']['score'] += score
        # lc_query = {'$set': lc_user}
        # lc_col.update_one({'discord_id': member.id}, lc_query)
        await self.logger.on_score_add(member = member, score = score, reason = reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score added.**")
        
    @score_group.command(name = 'deduct', description = "Deducts score")
    @app_commands.describe(member = "Member to deduct scores")
    @app_commands.describe(score = "Amount of scores to deduct (should be positive)")
    @app_commands.describe(reason = "Reason for deducting scores")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_deduct(self, interaction: discord.Interaction, member: discord.Member, score: int, reason: str):
        await interaction.response.defer(thinking = True)
        
        daily_obj = self.db_api.update_score(str(member.id), -score)
        if (daily_obj == None):
            await interaction.followup.send(f"The bot is bug-ed in score deduct, contact bot dev")
            return

        await self.logger.on_score_deduct(member = member, score = score, reason = reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score deducted.**")

async def setup(client):
    await client.add_cog(score(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(score(client))
