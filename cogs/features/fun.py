import json
import discord
from utils.asset import Assets
from discord import app_commands
from discord.ext import commands
from ..logging.logging import logging
import random
import requests

class fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    global bonus

    @app_commands.command(name="gacha", description="Random bonus point")
    async def _gacha(self, interaction: discord.Interaction):
        avatar_url = interaction.user.guild_avatar.url if interaction.user.guild_avatar else interaction.user.display_avatar.url    
        await interaction.response.defer(thinking = True)
        lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        lc_col = self.client.DBClient['LC_db']['LC_users']
        lc_daily_finished = lc_user['daily_task']['finished_today_daily']
        guild = self.client.get_guild(interaction.guild_id)
        member = guild.get_member(lc_user['discord_id'])
        if lc_daily_finished:
            global bonus
            bonus = random.randint(1, 3)
            lc_user['current_month']['score'] += 0
            lc_user['all_time']['score'] += 0
            lc_query = {'$set': lc_user}
            lc_col.update_one({'discord_id': member.id}, lc_query)
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



    @app_commands.command(name="ask", description="Ask random shiet things")
    @app_commands.choices(
    difficulty = [
        app_commands.Choice(name = "Easy", value = "easy"),
        app_commands.Choice(name = "Medium", value = "medium"),
        app_commands.Choice(name = "Hard", value = "hard"),
    ],
    type = [
        app_commands.Choice(name = 'True / False', value = 'boolean'),
        app_commands.Choice(name = 'Multiple Choice', value = 'multiple')
    ]
    )
    async def _ask(
        self, 
        interaction: discord.Interaction,
        difficulty: app_commands.Choice[str] = None,
        type: app_commands.Choice[str] = None
    ):
        difficulty_value = difficulty.value if difficulty else 'easy'
        type_value = type.value if type else 'multiple'
        response = requests.get(f'https://opentdb.com/api.php?amount=1&difficulty={difficulty_value}&type={type_value}');
        await interaction.response.defer(thinking=True)
        data = json.loads(response.content)
        print(data)
        # quiz = data.get('results')[0]
        embed = discord.Embed(
            title = 'question',
        )
        await interaction.followup.send(embed = embed)


    
async def setup(client):
    await client.add_cog(fun(client), guilds=[discord.Object(id=1085444549125611530)])