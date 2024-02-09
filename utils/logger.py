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

    async def on_submission(self, user, problem, submission, is_daily):
        guild = await self.client.fetch_guild(1085444549125611530)
        log_channel = await guild.fetch_channel(1087786510817964112)
        embed_color = Assets.easy if problem['difficulty'] == 'Easy' else Assets.medium if problem['difficulty'] == 'Medium' else Assets.hard
        submission_str = f"▸ **Submitted:** <t:{int(submission['timestamp'])}:R>"
        if is_daily:
            submission_str = "▸ 🗓️ **Daily challenge**\n" + submission_str
        embed = discord.Embed(
            title = f"[SOLVED] **{problem['id']}. {problem['title']}**",
            description = submission_str,
            url = f"https://leetcode.com/problem/{problem['titleSlug']}",
            color = embed_color
        )
        discord_mention = f"<@{user['discordId']}>"
        embed.add_field(
            name = "Author",
            value = discord_mention
        )
        embed.add_field(
            name = "Problem difficulty",
            value = problem['difficulty'],
        )
        embed.add_field(
            name = "Topics",
            value = f"|| {', '.join(problem['topics'])} ||",
        )
        embed.add_field(
            name = "Submission",
            value = f"[Check out the solution!](https://leetcode.com/submissions/detail/{submission['id']})"
        )
        leetcode_username = user['leetcodeUsername']
        leetcode_url = f"https://leetcode.com/{leetcode_username}"
        embed.set_author(
            name = f"Author: {leetcode_username}",
            icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
            url = leetcode_url
        )
        user = await self.client.fetch_user(int(user['discordId']))
        avatar_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
        if user.avatar != None:
            avatar_url = user.avatar.url
        embed.set_thumbnail(
            url = avatar_url
        )

        await log_channel.send(f":new: AC Alert!", embed = embed)

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
