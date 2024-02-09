import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.logger import Logger
import random


class Score(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logger = Logger(client)

    score_group = app_commands.Group(name = "score", description = "Scoring system")
    @score_group.command(name = 'add', description = "Adds score")
    @app_commands.describe(member = "Member to add scores")
    @app_commands.describe(score = "Amount of scores to add (should be positive)")
    @app_commands.describe(reason = "Reason for adding scores")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_add(self, interaction: discord.Interaction, member: discord.Member, score: int, reason: str):
        await interaction.response.defer(thinking = True)
        if score <= 0:
            await interaction.followup.send(f"{Assets.red_tick} **`Score` should be positive. Use `/score deduct` instead.**")
            return
        daily_obj = await self.client.db_api.update_score(str(member.id), score, reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score added.**")
        
    @score_group.command(name = 'deduct', description = "Deducts score")
    @app_commands.describe(member = "Member to deduct scores")
    @app_commands.describe(score = "Amount of scores to deduct (should be positive)")
    @app_commands.describe(reason = "Reason for deducting scores")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_deduct(self, interaction: discord.Interaction, member: discord.Member, score: int, reason: str):
        await interaction.response.defer(thinking = True)
        if score <= 0:
            await interaction.followup.send(f"{Assets.red_tick} **`Score` should be positive. Use `/score add` instead.**")
            return

        daily_obj = await self.client.db_api.update_score(str(member.id), -score, reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score deducted.**")

async def setup(client):
    await client.add_cog(Score(client), guilds=[discord.Object(id=1085444549125611530)])
