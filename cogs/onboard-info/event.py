import discord
import asyncio
import datetime 
import time
from discord.ext import commands, tasks
from utils.asset import Assets
from ..logging.logging import logging

class event(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.member_prune.start()

    def cog_unload(self):
        self.member_prune.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title = "Welcome to Lowie's LeetCode Club",
            description = """
            Xin chào các anh chị em đến với CLB LeetCode <:leetcode:1085915048167358554> của anh Daniel Tô! <:old_fb_love:1085916076434530345>

            Checklist các việc cần làm và nên làm ngay để không bỏ lỡ những spicy content của LLC:
            """,
            color = discord.Color.red()
        )
        embed.add_field(
            name = "Tìm hiểu thêm về CLB",
            value = "👉 <#1139158245391474800>",
            inline = False
        )
        embed.add_field(
            name = "Verify bản thân",
            value = "👉 <#1139158370926993499>",
            inline = False
        )
        embed.add_field(
            name = "Mời thêm bạn bè 😍",
            value = "👉 https://discord.gg/BrSzUsWp2w",
            inline = False
        )
        embed.set_thumbnail(
            url = member.guild.icon.url
        )
        embed.set_author(
            name = f"{member.name}",
            icon_url = member.avatar.url if member.avatar else member.default_avatar.url
        )
    
        channel = await member.guild.fetch_channel(1139158423846531162)
        await channel.send(content = f"{member.mention}", embed = embed)

    @tasks.loop(seconds = 120)
    async def member_prune(self):
        # Waiting for internal cache, I suppose
        await self.client.wait_until_ready()
        await asyncio.sleep(5)

        guild = self.client.get_guild(1085444549125611530)
        for member in list(guild.members):
            lc_query = self.client.DBClient['LC_db']['LC_config'].find_one({})
            time_before_kick = lc_query['time_before_kick']

            if len(member.roles) == 1 and int(datetime.datetime.now().timestamp()) - int(member.joined_at.timestamp()) > time_before_kick:
                kicked_reason = "Unverified for 7 days"

                # Logging 
                await logging.on_member_remove(logging(self.client), member = member, reason = kicked_reason)

                # Wait for the log to be post
                await asyncio.sleep(5)

                # Actually kick the member
                await member.kick(reason = kicked_reason)


async def setup(client):
    await client.add_cog(event(client))
