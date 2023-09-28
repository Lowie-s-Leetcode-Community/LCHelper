import discord
import sys
from discord import app_commands
from discord.ext import commands
from utils.lc_utils import LC_utils
from ..logging.logging import logging
import random

class fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="gacha", description="Random bonus point")
    async def _gacha(self, interaction: discord.Interaction):
        avatar_url = interaction.user.guild_avatar.url if interaction.user.guild_avatar else interaction.user.display_avatar.url    
        await interaction.response.defer(thinking = True)
        lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        lc_daily_finished = lc_user['daily_task']['finished_today_daily']
        guild = self.client.get_guild(interaction.guild_id)
        member = guild.get_member(lc_user['discord_id'])
        if lc_daily_finished:
            bonus = random.randint(1, 3)
            lc_user['all_time']['score'] += 0
            embed = discord.Embed(
                title = "Gacha",
                description = f"You got {bonus} {'points' if bonus > 1 else 'point'} !",    
                color = 0x03cffc,
                timestamp = interaction.created_at
            )
        else: 
            embed = discord.Embed(
                title = "Gacha",
                description = f"You got to finish daily Leetcode first!",    
                color = 0x03cffc,
                timestamp = interaction.created_at
            )
        embed.set_author(
            name = "Gacha",
            icon_url = self.client.user.display_avatar.url
        )
        embed.set_footer(
            text = interaction.user.display_name,
            icon_url = avatar_url
        )
        await interaction.followup.send(embed = embed)
        if lc_daily_finished:
            await logging.on_score_add(logging(self.client), member = member, score = bonus, reason = 'Gacha!')

    
async def setup(client):
    await client.add_cog(fun(client), guilds=[discord.Object(id=1085444549125611530)])