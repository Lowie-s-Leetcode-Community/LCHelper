import discord
from discord.ext import commands
from redis import Redis

from utils.asset import Assets


class RedisAdmin(commands.Cog):
    #   2 functions to test write and read features.
    #   it write and read on a Hash structure in redis module, named "testing"
    #   other functionality, including arrays, streams, please ask chatGPT or
    # refer to Redis doc.
    def __init__(self, client):
        self.client = client
        self.redis: Redis = client.redis

    @commands.command(name="redis_write")
    @commands.has_any_role(1087746207511757002)
    async def _write(self, ctx, key: str, value: str):
        self.redis.hset("testing", key, value)
        embed = discord.Embed(
            title=":diamonds: Redis Set",
            description=f"Value at {key} is set to {value}!",
            color=Assets.medium,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(
            text=ctx.author.name,
        )
        await ctx.send(embed=embed)

    @commands.command(name="redis_read")
    @commands.has_any_role(1087746207511757002)
    async def _read(self, ctx, key: str):
        value = self.redis.hget("testing", key)
        desc_str = f"Value at {key} doesn't exist!"

        if value is not None:
            desc_str = f"Value at {key} is {value}!"

        embed = discord.Embed(
            title=":diamonds: Redis Get",
            description=desc_str,
            color=Assets.hard if value is None else Assets.easy,
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(
            text=ctx.author.name,
        )
        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(RedisAdmin(client))
