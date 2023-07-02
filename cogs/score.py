import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from .logging import logging
from typing import Optional
import random
import string
import asyncio

class score(commands.Cog):
    def __init__(self, client):
        self.client = client

    score_group = app_commands.Group(name = "score", description = "Scoring system")
    @score_group.command(name = 'add', description = "Adds score")
    @app_commands.describe(member = "Member to add scores")
    @app_commands.describe(score = "Amount of scores to add (should be positive)")
    @app_commands.describe(reason = "Reason for adding scores")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_add(self, interaction: discord.Interaction, member: discord.Member, score: int, reason: str):
        await interaction.response.defer(thinking = True)

        lc_col = self.client.DBClient['LC_db']['LC_users']
        lc_user = lc_col.find_one({'discord_id': member.id})
        lc_user['current_month']['score'] += score
        lc_user['all_time']['score'] += score
        lc_query = {'$set': lc_user}
        lc_col.update_one({'discord_id': member.id}, lc_query)
        await logging.on_score_add(logging(self.client), member = member, score = score, reason = reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score added.**")
        
    @score_group.command(name = 'deduct', description = "Deducts score")
    @app_commands.describe(member = "Member to deduct scores")
    @app_commands.describe(score = "Amount of scores to deduct (should be positive)")
    @app_commands.describe(reason = "Reason for deducting scores")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_deduct(self, interaction: discord.Interaction, member: discord.Member, score: int, reason: str):
        await interaction.response.defer(thinking = True)

        lc_col = self.client.DBClient['LC_db']['LC_users']
        lc_user = lc_col.find_one({'discord_id': member.id})
        lc_user['current_month']['score'] -= score
        lc_user['all_time']['score'] -= score
        lc_query = {'$set': lc_user}
        lc_col.update_one({'discord_id': member.id}, lc_query)
        await logging.on_score_deduct(logging(self.client), member = member, score = score, reason = reason)
        await interaction.followup.send(f"{Assets.green_tick} **Score deducted.**")

    @score_group.command(name = 'monthly_reset', description = "Reset the server's monthly score")
    @app_commands.checks.has_permissions(administrator = True)
    async def _score_reset(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)

        lc_col = self.client.DBClient['LC_db']['LC_users']
        users = list(lc_col.find())
        for user in users:
            user['current_month']['score'] = 0
            lc_query = {'$set': user}
            lc_col.update_one({'discord_id': user['discord_id']}, lc_query)
        await logging.on_score_reset(logging(self.client), member_count = len(users))
        msg = "Reset the score of " + str(len(users)) + " LLC members!"
        await interaction.followup.send(msg)

async def setup(client):
    await client.add_cog(score(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(score(client))
