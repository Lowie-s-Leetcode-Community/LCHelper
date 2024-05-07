import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
import traceback
import json
import os
from datetime import datetime

class Logger:
    def __init__(self, client):
        self.client = client
    
    async def on_db_update(self, success, context, message):
        try:
            guild = await self.client.fetch_guild(self.client.config['serverId'])
            log_channel = await guild.fetch_channel(self.client.config['databaseLogId'])
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
                json_log = json.loads(message)

                # TODO: refactor to public_log_fwd class
                if isinstance(json_log, dict):
                    if "type" in json_log and json_log["type"] == "Submission":
                        content = json_log["content"]
                        await self.on_submission(
                            content["user"],
                            content["problem"],
                            content["submission"],
                            content["is_daily"]
                        )
                    if "type" in json_log and json_log["type"] == "Score":
                        content = json_log["content"]
                        await self.on_score_add(
                            content['member_mention'],
                            content["delta"],
                            content['reason']
                        )
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
    
    async def on_automation_event(self, context: str, message: str):
        try:
            guild = await self.client.fetch_guild(self.client.config['serverId'])
            log_channel = await guild.fetch_channel(self.client.config['eventLoggingId'])
            await log_channel.send(f"**{context}** automation invoke: **{message}**. Timestamp: **{datetime.now()}**")
        except Exception as e:
            print(traceback.format_exc()[:800])
            raise
        return
    
    async def on_score_add(self, member_mention: str, score: int, reason: str):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        log_channel = await guild.fetch_channel(self.client.config['scoreLogChannelId'])
        embed = discord.Embed(
            description = f"""
            ▸ **Score added:** {member_mention} **+{score}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.easy
        )
        await log_channel.send(embed = embed)

    async def on_score_deduct(self, member_mention: str, score: int, reason: str):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        log_channel = await guild.fetch_channel(self.client.config['scoreLogChannelId'])
        embed = discord.Embed(
            description = f"""
            ▸ **Score deducted:** {member_mention} **-{abs(score)}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.hard
        )
        await log_channel.send(embed = embed)

    async def on_submission(self, user, problem, submission, is_daily):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        log_channel = await guild.fetch_channel(self.client.config['submissionChannelId'])
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
