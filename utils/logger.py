import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
import traceback
import os

class Logger:
    def __init__(self, client):
        self.client = client
    
    async def on_db_update(self, success, context, message):
        try:
            guild = await self.client.fetch_guild(1085444549125611530)
            log_channel = await guild.fetch_channel(1202180199060615168)
            if success:
                msg = f"""
                {os.getenv('LOGGING_PREFIX')}db_log
                Table **{context}** updated successfully
                """
                embed = discord.Embed(
                    description = message,
                    color = Assets.easy
                )
                await log_channel.send(msg, embed = embed)
            else:
                msg = f"""
                {os.getenv('LOGGING_PREFIX')}db_log
                Table **{context}** updated failed
                """
                embed = discord.Embed(
                    description = message,
                    color = Assets.hard
                )
                await log_channel.send(msg, embed = embed)
        except Exception as e:
            print(traceback.format_exc()[:800])
            raise
        return
    
    async def on_score_add(self, member_mention: str, score: int, reason: str):
        guild = await self.client.fetch_guild(1085444549125611530)
        log_channel = await guild.fetch_channel(1089391914664603648)
        embed = discord.Embed(
            description = f"""
            ▸ **Score added:** {member_mention} **+{score}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.easy
        )
        await log_channel.send(embed = embed)

    async def on_score_deduct(self, member_mention: str, score: int, reason: str):
        guild = await self.client.fetch_guild(1085444549125611530)
        log_channel = await guild.fetch_channel(1089391914664603648)
        embed = discord.Embed(
            description = f"""
            ▸ **Score deducted:** {member_mention} **-{abs(score)}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.hard
        )
        await log_channel.send(embed = embed)

    async def on_submission(self, userId, problemId, is_daily):
        guild = await self.client.fetch_guild(1085444549125611530)
        log_channel = await guild.fetch_channel(1087786510817964112)
        embed = discord.Embed(
            description = f"""
            Recorded submission from {userId}.
            Problem: **{problemId}** ({problemId}).
            Daily Challenge: {"Yes" if is_daily else "No"}.
            """,
            color = Assets.hard
        )
        await log_channel.send(embed = embed)

    # All fn below will be changed into on_message fetches
    async def on_member_remove(self, member: discord.Member, reason: str):
        lc_col = self.client.DBClient['LC_db']['LC_config']
        lc_guild = lc_col.find_one({})
        log_channel = await member.guild.fetch_channel(lc_guild['event_channel_id'])
        embed = discord.Embed(
            color = Assets.hard
        )
        embed.add_field(
            name = "Member",
            value = f"{member.name} ({member.mention})"
        )
        embed.add_field(
            name = "ID",
            value = f"{member.id}"
        )
        embed.add_field(
            name = "Member count",
            value = f"{member.guild.member_count - 1}"
        )
        embed.add_field(
            name = "Reason",
            value = reason
        )
        embed.set_author(
            name = "Member kicked"
        )
        await log_channel.send(embed = embed)
