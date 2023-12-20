import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from ..logging.logging import logging
import random
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

    # Command deprecated.
    # @score_group.command(name = 'monthly_reset', description = "Reset the server's monthly score")
    # @app_commands.checks.has_permissions(administrator = True)
    # async def _score_reset(self, interaction: discord.Interaction):
    #     await interaction.response.defer(thinking = True)

    #     lc_col = self.client.DBClient['LC_db']['LC_users']
    #     users = list(lc_col.find())
    #     for user in users:
    #         user['current_month']['score'] = 0
    #         lc_query = {'$set': user}
    #         lc_col.update_one({'discord_id': user['discord_id']}, lc_query)
    #     await logging.on_score_reset(logging(self.client), member_count = len(users))
    #     msg = "Reset the score of " + str(len(users)) + " LLC members!"
    #     await interaction.followup.send(msg)

    

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
        elif lc_daily_finished and lc_gacha is True:
            embed = discord.Embed(
                description=f"You already got your bonus point today!",
                color=0x03cffc,
                timestamp=interaction.created_at
            )
        else:
            embed = discord.Embed(
                description=f"You got to finish daily Leetcode first!",
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
        if lc_daily_finished:
            await logging.on_score_add(logging(self.client), member=member, score=bonus, reason='Gacha!')
    

async def setup(client):
    await client.add_cog(score(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(score(client))
