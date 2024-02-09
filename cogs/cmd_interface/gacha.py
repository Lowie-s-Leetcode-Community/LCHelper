import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.logger import Logger
import random

class Gacha(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.logger = Logger(client)

  @app_commands.command(name="gacha", description="Random bonus point")
  async def _gacha(self, interaction: discord.Interaction):
    avatar_url = interaction.user.guild_avatar.url if interaction.user.guild_avatar else interaction.user.display_avatar.url
    await interaction.response.defer(thinking=True)
    lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
    lc_col = self.client.DBClient['LC_db']['LC_users']
    lc_gacha = (lc_user['daily_task']['gacha'] != -1)
    lc_daily_finished = lc_user['daily_task']['finished_today_daily']
    guild = self.client.get_guild(interaction.guild_id)
    member = guild.get_member(lc_user['discord_id'])
    bonus = min([random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)])

    if lc_daily_finished and lc_gacha is False:
      lc_user['current_month']['score'] += bonus
      lc_user['all_time']['score'] += bonus
      lc_user['daily_task']['gacha'] = bonus
      lc_query = {'$set': lc_user}
      lc_col.update_one({'discord_id': member.id}, lc_query)
      embed = discord.Embed(
        description=f"You got {bonus} {'points' if bonus > 1 else 'point'}!",
        color=0x03cffc,
        timestamp=interaction.created_at
      )
      await self.logger.on_score_add(member=member, score=bonus, reason='Gacha!')
    elif lc_daily_finished and lc_gacha is True:
      embed = discord.Embed(
        description=f"You already got your bonus point today!",
        color=0x03cffc,
        timestamp=interaction.created_at
      )
    else:
      embed = discord.Embed(
        description=f"You have to finish daily Leetcode first!",
        color=0x03cffc,
        timestamp=interaction.created_at
      )
    embed.set_author(
      name="Gacha",
      icon_url=self.client.user.display_avatar.url
    )
    embed.set_footer(
      text=interaction.user.display_name,
      icon_url=avatar_url
    )
    await interaction.followup.send(embed=embed)
 
async def setup(client):
  await client.add_cog(Gacha(client), guilds=[discord.Object(id=client.config['serverId'])])
