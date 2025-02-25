import discord
from discord.ext import commands

from utils.asset import Assets


class bot_related(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ping", aliases=["pong"])
    async def _ping(self, ctx):
        bot_avatar_url = (
            ctx.me.guild_avatar.url
            if ctx.me.guild_avatar
            else ctx.me.display_avatar.url
        )
        author_avatar_url = (
            ctx.author.guild_avatar.url
            if ctx.author.guild_avatar
            else ctx.author.display_avatar.url
        )
        embed = discord.Embed(
            title="Pong!",
            description="Calculating...",
            color=0x03CFFC,
            timestamp=ctx.message.created_at,
        )
        embed.set_author(icon_url=bot_avatar_url, name="Pong!")
        embed.set_footer(text=ctx.author.name, icon_url=author_avatar_url)
        response = await ctx.send(embed=embed)
        embed = discord.Embed(color=Assets.easy, timestamp=ctx.message.created_at)

        diff = response.created_at - ctx.message.created_at
        embed.add_field(
            name="Ping ⏱️", value=f"**{1000 * diff.total_seconds():.1f}** ms"
        )
        embed.add_field(
            name="WebSocket 💓", value=f"**{round(self.client.latency * 1000, 2)}** ms"
        )
        embed.set_author(icon_url=bot_avatar_url, name="Pong!")
        embed.set_footer(text=ctx.author.name, icon_url=author_avatar_url)
        await response.edit(embed=embed)


async def setup(client):
    await client.add_cog(bot_related(client))
