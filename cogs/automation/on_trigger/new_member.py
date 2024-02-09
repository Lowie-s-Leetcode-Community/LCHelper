import discord
import asyncio
import datetime 
import time
from discord.ext import commands, tasks
from utils.asset import Assets
from utils.logger import Logger
import os

class NewMember(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logger = Logger(client)

    def cog_unload(self):
        self.member_prune.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        unverified_role = member.guild.get_role(self.client.config["unverifiedRoleId"])
        await member.add_roles(unverified_role)
        embed = discord.Embed(
            title = "Welcome to the Lowie's LeetCode Community",
            description = """
            Xin chào các anh chị em đến với Cộng đồng LLC <:leetcode:1085915048167358554> của anh Lowie! <:old_fb_love:1085916076434530345>

            Checklist các việc cần làm và nên làm ngay để không bỏ lỡ những spicy content của LLC:
            """,
            color = discord.Color.red()
        )
        embed.add_field(
            name = "Tìm hiểu thêm về Cộng đồng",
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
        embed.add_field(
            name = "Theo dõi Bí Thuật Toán, trang content chia sẻ kiến thức của tụi mình",
            value = "👉 https://www.facebook.com/bi.thuat.toan",
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

async def setup(client):
    await client.add_cog(NewMember(client))
