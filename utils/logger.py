import discord
from utils.asset import Assets
import traceback
import json
import os
from datetime import datetime
from lib.embed.submission_embed import SubmissionEmbed

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
        submission['is_daily'] = is_daily
        discord_user = await self.client.fetch_user(int(user['discordId']))
        user['avatar'] = discord_user.avatar 
        embed = SubmissionEmbed(user, problem, submission)

        await log_channel.send(f":new: AC Alert!", embed = embed)
