import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from datetime import datetime

class RecoverDaily(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name='recover_daily', description="Khôi phục dữ liệu daily của ngày bị chặn")
    @app_commands.describe(
      day = "Ngày khôi phục, viết theo format YYYY-MM-DD.",
      problem_id = "ID của bài tập cần được add."
    )
    @app_commands.checks.has_permissions(administrator = True)
    async def _recover_daily(self, interaction: discord.Interaction, day: str, problem_id: int):
      await interaction.response.defer(thinking = True)
      try:
        day = datetime.strptime(day, "%Y-%m-%d").date()
      except Exception:
        await interaction.followup.send(f"{Assets.red_tick} **Date format error**")
        return
      else:
        await self.client.db_api.create_or_keep_daily_object(problem_id, day)
        await interaction.followup.send(f"{Assets.green_tick} **Daily of {day} is updated to {problem_id}.**")

async def setup(client):
    await client.add_cog(RecoverDaily(client), guilds=[discord.Object(id=client.config['serverId'])])
