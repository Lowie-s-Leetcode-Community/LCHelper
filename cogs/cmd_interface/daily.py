import discord
from discord import app_commands
from discord.ext import tasks, commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
import os
import asyncio
import traceback
import datetime

class Daily(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'daily', description = "Returns Leetcode's Daily Challenge")
    async def _daily(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        daily_obj = self.client.db_api.read_latest_daily_object()
        problem = daily_obj['problem']

        info = LC_utils.get_problem_info(problem['titleSlug'])

        embed = discord.Embed(
            title = f"**{info['title']}**",
            url = f"{info['link']}",
            color = Assets.easy if info['difficulty'] == 'Easy' else Assets.medium if info['difficulty'] == 'Medium' else Assets.hard
        )
        embed.add_field(
            name = "Difficulty",
            value = info['difficulty'],
            inline = True
        )
        embed.add_field(
            name = "AC Count", 
            value = f"{info['total_AC']}/{info['total_submissions']}",
            inline = True,
        )
        embed.add_field(
            name = "AC Rate",
            value = str(info['ac_rate'])[0:2] + "%",
            inline = True,
        )
        tag_list = ""
        for name, link in info['topics'].items():
            tag_list += f"[``{name}``]({link}), "
        tag_list = "||" + tag_list + "||"
        embed.add_field(
            name = "Topics",
            value = tag_list,
            inline = False
        )
        embed.set_footer(
            text = f"{info['likes']} 👍 • {info['dislikes']} 👎"
        )
        display_date = daily_obj['generatedDate'].strftime("%b %d, %Y")
        await interaction.followup.send(f"Daily Challenge - {display_date}", embed = embed)        

async def setup(client):
    await client.add_cog(Daily(client), guilds=[discord.Object(id=client.config['serverId'])])
