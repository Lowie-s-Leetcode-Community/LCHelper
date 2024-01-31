import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets

class Logger:
    def __init__(self, client):
        self.client = client
    
    async def on_db_update(self, success, context, message):
        try:
            guild = await self.client.fetch_guild(1085444549125611530)
            log_channel = await guild.fetch_channel(1202180199060615168)
            if success:
                embed = discord.Embed(
                    description = f"""
                        Table **{context}** updated successfully
                        """,
                        color = Assets.easy
                )
                await log_channel.send(embed = embed)
            else:
                embed = discord.Embed(
                    description = f"""
                        Table **{context}** updated failed :(
                        Message: {message}
                        """,
                        color = Assets.hard
                )
                await log_channel.send(embed = embed)
        except Exception as e:
            print(traceback.format_exc())
        return
    
    # All fn below will be changed into on_message fetches
    async def on_score_add(self, member: discord.Member, score: int, reason: str):
        guild_id = member.guild.id
        lc_col = self.client.DBClient['LC_db']['LC_config']
        lc_guild = lc_col.find_one({})
        log_channel = await member.guild.fetch_channel(lc_guild['score_log_channel_id'])
        embed = discord.Embed(
            description = f"""
            ▸ **Score added:** {member.mention} **+{score}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.easy
        )
        await log_channel.send(embed = embed)

    async def on_score_deduct(self, member: discord.Member, score: int, reason: str):
        lc_col = self.client.DBClient['LC_db']['LC_config']
        lc_guild = lc_col.find_one({})
        log_channel = await member.guild.fetch_channel(lc_guild['score_log_channel_id'])
        embed = discord.Embed(
            description = f"""
            ▸ **Score deducted:** {member.mention} **-{score}**
            ▸ **Reason:** {reason}
            """,
            color = Assets.hard
        )
        await log_channel.send(embed = embed)

    async def on_score_reset(self, member_count: int):
        lc_col = self.client.DBClient['LC_db']['LC_config']
        lc_guild = lc_col.find_one({})
        guild = await self.client.fetch_guild(1085444549125611530)
        log_channel = await guild.fetch_channel(lc_guild['event_channel_id'])
        msg = "Reset the score of " + str(member_count) + " LLC members!"
        await log_channel.send(msg)

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
