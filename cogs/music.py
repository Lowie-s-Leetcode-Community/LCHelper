import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import datetime
from utils.asset import Assets
import random
import json
import asyncio
import functools
import itertools
import math
import youtube_dl
from youtube_dl import YoutubeDL
from async_timeout import timeout
from discord.ext import commands

# Silence useless bug reports messages
YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_states = {}
        self.loop = False

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = discord.VoiceState(self.client, ctx)
            self.voice_states[ctx.guild.id] = state

        return state
    """
    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)
    """
    @commands.command(name = "join", aliases = ["connect", "hello"])
    async def _join(self, ctx):
        if (ctx.author.voice == None):
            await ctx.send(f"{Assets.red_tick} **You must first join a voice channel!**")
            return
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"{Assets.green_tick} **Joined {channel.mention}**")


    @commands.command(name = "disconnect", aliases = ["dc", "bye"])
    async def _disconnect(self, ctx):
        if (ctx.voice_client == None):
            await ctx.send(f"{Assets.red_tick} **I am not even in a voice channel?**")
            return
        if (ctx.author.voice == None):
            await ctx.send(f"{Assets.red_tick} **You aren't even in a voice channel?**")
            return
        channel = ctx.voice_client.channel
        await ctx.voice_client.disconnect()
        await ctx.send(f"{Assets.green_tick} **Left {channel.mention}**")
        self.loop = False

    @commands.command(name = 'skip', aliases = ["s"])
    async def _skip(self, ctx):
        self.loop = False
        voice_state = discord.utils.get(self.client.voice_clients, guild = ctx.guild)
        if voice_state.is_playing:
            voice_state.stop()
            await ctx.send(f"{Assets.green_tick} **Skipped**")


    @commands.command(name = 'loop')
    async def _loop(self, ctx):
        self.loop = not self.loop
        await ctx.send(f"{Assets.green_tick} **Looping set to {self.loop}**")

    @commands.command(name = 'play', aliases = ["p"])
    async def _play(self, ctx, *, search: str):
        voice_state = discord.utils.get(self.client.voice_clients, guild = ctx.guild)
        if (voice_state == None):
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"{Assets.green_tick} **Joined {channel.mention}**")
        voice_state = discord.utils.get(self.client.voice_clients, guild = ctx.guild)
        async with ctx.typing():
            if not voice_state.is_playing():
                try:
                    with YoutubeDL(YTDL_OPTIONS) as ydl:
                        info = ydl.extract_info(search, download = False)
                except:
                     with YoutubeDL(YTDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{search}", download = False)['entries'][0]

                URL = info['url']
                voice_state.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                embed = discord.Embed(
                    description = f"**🎵 [Now Playing](https://youtube.com/watch?v={info['display_id']})** 🎵",
                    color = 0x3e65f0
                )
                embed.add_field(
                    name = f"Title",
                    value = info["title"],
                    inline = False
                )
                embed.add_field(
                    name = "Channel",
                    value = info["channel"]
                )
                embed.add_field(
                    name = "Upload Date",
                    value = f"{info['upload_date'][6:8]}/{info['upload_date'][4:6]}/{info['upload_date'][0:4]}"
                )
                embed.add_field(
                    name = "Duration",
                    value = str(datetime.timedelta(seconds=int(info["duration"])))
                )
                embed.set_thumbnail(url = info["thumbnail"])
                embed.set_author(
                    name = ctx.author,
                    icon_url = ctx.author.avatar_url
                )
                embed.set_footer(
                    text = f"👀 {info['view_count']} | 👍 {info['like_count']}"
                )
                await ctx.send(embed = embed)
            else:
                await ctx.send("No queue function yet, cry about it")

def setup(client):
    client.add_cog(Music(client))
