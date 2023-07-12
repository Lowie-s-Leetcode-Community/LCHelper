import discord
import os
from discord.ext import commands
from discord.ext.commands import Greedy
from typing import Literal, Optional
from datetime import datetime
import typing
from utils.asset import Assets

class control(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "reload", aliases = ["r"])
    @commands.has_permissions(administrator = True)
    async def _reload(self, ctx, *, s: str):
        msg = ""
        if (s == "all"):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.client.unload_extension(f'cogs.{filename[:-3]}')
                    except: continue
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.client.load_extension(f'cogs.{filename[:-3]}')
                        msg += f"{Assets.reload} **cogs.{filename[:-3]}**\n"
                    except Exception as e:
                        msg += f"{Assets.red_tick} **cogs.{filename[:-3]}: `{e}`**\n"
            await ctx.send(msg)
        else:
            t = s.split(" ")
            for i in t:
                try:
                    await self.client.unload_extension(f'cogs.{i}')
                except: msg = msg
                try:
                    await self.client.load_extension(f'cogs.{i}')
                    msg += f"{Assets.reload} **cogs.{i}**\n"
                except Exception as e:
                    msg += f"{Assets.red_tick} **cogs.{i}: `{e}`**\n"
            await ctx.send(msg)

    @commands.command(name = "sync")
    @commands.has_permissions(administrator = True)
    async def sync(self, ctx, guilds: Greedy[discord.Object], spec: Optional[Literal["1", "2", "3", "4"]] = None):
        if not guilds:
            if spec == "1": # Syncing all commands in the current tree to local
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "2": # Syncing all commands from global to local
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "3": # Clearing all commands on local
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            elif spec == "4": # Clearing all commands on global and sync to local (to prevent duplicate commands)
                ctx.bot.tree.clear_commands(guild=None)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"🔁 **Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}**"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

async def setup(client):
    await client.add_cog(control(client), guilds=[discord.Object(id=734653818163298355)])
