import discord
from discord.ext import commands
from datetime import datetime
import random
import json
class bot_related(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "ping", aliases = ["pong"])
    async def _ping(self, ctx):
        embed = discord.Embed(
            title = "Pong!",
            description = "Calculating...",
            color = 0x03cffc,
            timestamp = ctx.message.created_at
        )
        embed.set_author(
            icon_url = ctx.me.avatar_url,
            name = "Pong!"
        )
        embed.set_footer(
            text = ctx.author,
            icon_url = ctx.author.avatar_url
        )
        response = await ctx.send(embed = embed)
        embed = discord.Embed(
            #title = "Pong!",
            #description = "Here is my ping :)",
            color = 0x03cffc,
            timestamp = ctx.message.created_at)

        diff = response.created_at - ctx.message.created_at
        embed.add_field(
            name = "Ping ⏱️",
            value = f"**{1000*diff.total_seconds():.1f}** ms"
        )
        embed.add_field(
            name = "WebSocket 💓",
            value = f"**{round(self.client.latency*1000, 2)}** ms"
        )
        embed.set_author(
            icon_url = ctx.me.avatar_url,
            name = "Pong!"
        )
        embed.set_footer(
            text = ctx.author,
            icon_url = ctx.author.avatar_url
        )
        await response.edit(embed = embed)

def setup(client):
    client.add_cog(bot_related(client))
