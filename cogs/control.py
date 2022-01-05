import discord
import os
from discord.ext import commands
from datetime import datetime
import typing
from utils.asset import Assets

class control(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "reload", aliases = ["r"])
    @commands.is_owner()
    async def _reload(self, ctx, *, s: str):
        msg = ""
        if (s == "all"):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        self.client.unload_extension(f'cogs.{filename[:-3]}')
                    except: continue
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        self.client.load_extension(f'cogs.{filename[:-3]}')
                        msg += f"🔁 **cogs.{filename[:-3]}**\n"
                    except Exception as e:
                        msg += f"{Assets.red_tick} **cogs.{filename[:-3]}: `{e}`**\n"
            await ctx.send(msg)
        else:
            t = s.split(" ")
            for i in t:
                try:
                    self.client.unload_extension(f'cogs.{i}')
                except: msg = msg
                try:
                    self.client.load_extension(f'cogs.{i}')
                    msg += f"🔁 **cogs.{i}**\n"
                except Exception as e:
                    msg += f"{Assets.red_tick} **cogs.{i}: `{e}`**\n"
            await ctx.send(msg)


def setup(client):
    client.add_cog(control(client))
