import discord
import os
from discord.ext import commands
from datetime import datetime
import typing
import urllib
import requests
from utils.asset import Assets

class tools(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "calculate", aliases = ["calc", "math"])
    async def _calc(self, ctx, *, msg):
        msg = msg.replace(" ", "")
        msg2 = urllib.parse.quote(msg)
        r = requests.get(f"http://api.mathjs.org/v4/?expr={msg2}")
        if r.status_code != 200:
            await ctx.send(f"{Assets.red_tick} **Invalid Expression**")
        else:
            msg = msg.replace("+", " + ")
            msg = msg.replace("*", " × ")
            msg = msg.replace("/", " / ")
            msg = msg.replace("-", " - ")
            embed = discord.Embed(
                title = f"{msg} ",
                description = f"= {r.json()}",
                color = 0x03cffc,
                timestamp = ctx.message.created_at
            )
            embed.set_footer(
                text = ctx.author,
                icon_url = ctx.author.avatar_url
            )
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(tools(client))
