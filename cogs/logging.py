import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional
import random
import string
import asyncio

class logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    logging_group = app_commands.Group(name = "logging", description = "Logging Group")
    @logging_group.command(name = 'track', description = "Sets a channel to track recent AC submissions")
    @app_commands.describe(channel = "Choose a channel")
    async def _track(self, interaction: discord.Interaction, channel: discord.channel.TextChannel):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_tracking']
        lc_query = {'server_id': interaction.guild_id}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'tracking_channel_id': channel.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'tracking_channel_id': channel.id})
        await interaction.followup.send(f"{Assets.green_tick} **Tracking channel has been set to {channel.mention}**")

    @logging_group.command(name = 'score', description = "Sets a channel to track score updates")
    @app_commands.describe(channel = "Choose a channel")
    async def _track(self, interaction: discord.Interaction, channel: discord.channel.TextChannel):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_tracking']
        lc_query = {'server_id': interaction.guild_id}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'score_log_channel_id': channel.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'score_log_channel_id': channel.id})
        await interaction.followup.send(f"{Assets.green_tick} **Score updates channel has been set to {channel.mention}**")

    async def on_score_add(self, member: discord.Member, score: int, reason: str):
        guild_id = member.guild.id
        lc_col = self.client.DBClient['LC_db']['LC_tracking']
        lc_guild = lc_col.find_one({'server_id': guild_id})
        log_channel = await member.guild.fetch_channel(lc_guild['score_log_channel_id'])
        embed = discord.Embed(
            description = f"""
            ▸ **Score added:** {member.mention} **+{score}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.easy
        )
        await log_channel.send(embed = embed)

    async def on_score_deduct(self, member: discord.Member, score: int, reason: str):
        guild_id = member.guild.id
        lc_col = self.client.DBClient['LC_db']['LC_tracking']
        lc_guild = lc_col.find_one({'server_id': guild_id})
        log_channel = await member.guild.fetch_channel(lc_guild['score_log_channel_id'])
        embed = discord.Embed(
            description = f"""
            ▸ **Score deducted:** {member.mention} **-{score}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.hard
        )
        await log_channel.send(embed = embed)

async def setup(client):
    await client.add_cog(logging(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(logging(client))
