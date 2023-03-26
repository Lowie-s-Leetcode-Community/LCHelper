import discord
from discord import FFmpegPCMAudio
from discord import app_commands
from discord.ext import commands
import datetime
from utils.asset import Assets
import random
import json
import asyncio
import functools
import itertools
import math
import yt_dlp
from yt_dlp import YoutubeDL
from async_timeout import timeout

# Silence useless bug reports messages
YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_states = {}
        self.queue = {}
        self.np = {}
        self.loop = {}

    async def queue_check(self, interaction):
        if self.loop[interaction.guild_id] == True:
            query = self.np[interaction.guild_id]
            await self.play_music(interaction, query, True, False)
            return

        if interaction.guild_id in self.queue:
            if len(self.queue[interaction.guild_id]):
                query = self.queue[interaction.guild_id][0]
                self.queue[interaction.guild_id].pop(0)
                await self.play_music(interaction, query, True, True)

        return

    def get_query_info(self, interaction, query):
        try:
            with YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(query, download = False)
        except:
            with YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download = False)['entries'][0]

        return {
            "url": info["url"], 
            "display_id": info["display_id"],
            "title": info["title"],
            "channel": info["channel"],
            "upload_date": info["upload_date"],
            "duration": info["duration"],
            "view_count": info["view_count"],
            "like_count": info["like_count"],
            "thumbnail": info["thumbnail"],
            "requester": interaction.user.mention
        }

    async def play_music(self, interaction, query, loaded = False, first_play = True):
        info = (query if loaded else self.get_query_info(interaction, query))
        voice_state = discord.utils.get(self.client.voice_clients, guild = interaction.guild)
        event = asyncio.Event()
        voice_state.play(FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS), after = lambda _: self.client.loop.call_soon_threadsafe(event.set))
        self.np[interaction.guild_id] = info
        if first_play:
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
            embed.add_field(
                name = "Requester", 
                value = info["requester"]
            )
            embed.set_thumbnail(url = info["thumbnail"])
            embed.set_footer(
                text = f"👀 {info['view_count']} | 👍 {info['like_count']}"
            )
            await interaction.followup.send(embed = embed)
        await event.wait()
        await self.queue_check(interaction)
    
    @app_commands.command(name = "join", description = "Join your voice channel!")
    async def _join(self, interaction: discord.Interaction):
        if (interaction.user.voice == None):
            await interaction.response.send_message(f"{Assets.red_tick} **You must first join a voice channel!**")
            return
        channel = interaction.user.voice.channel
        try:    
            await channel.connect()
        except discord.ClientException:
            pass
        except:
            await interaction.response.send_message(f"{Assets.red_tick} **Something went wrong, please try later.**")
            return
        await interaction.response.send_message(f"{Assets.green_tick} **Joined {channel.mention}**")

    
    @app_commands.command(name = "disconnect", description = "Leave the current voice channel.")
    async def _disconnect(self, interaction: discord.Interaction):
        if (interaction.guild.voice_client == None):
            await interaction.response.send_message(f"{Assets.red_tick} **I am not even in a voice channel?**")
            return
        author = interaction.guild.get_member(interaction.user.id)
        if (author.voice == None):
            await interaction.response.send_message(f"{Assets.red_tick} **You aren't even in a voice channel?**")
            return
        channel = interaction.guild.voice_client.channel
        self.loop[interaction.guild_id] = False
        self.queue[interaction.guild_id] = []
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(f"{Assets.green_tick} **Left {channel.mention}**")

    
    @app_commands.command(name = 'skip', description = "Skip the current playing song")
    async def _skip(self, interaction: discord.Interaction):
        voice_state = discord.utils.get(self.client.voice_clients, guild = interaction.guild)
        if voice_state.is_playing:
            voice_state.stop()
            await interaction.response.send_message(f"{Assets.green_tick} **Skipped**")
            self.queue_check(interaction)

    @app_commands.command(name = 'play', description = "Play a song!")
    @app_commands.describe(query = "Enter the song name or link on Youtube!")
    async def _play(self, interaction: discord.Interaction, query: str):
        voice_state = discord.utils.get(self.client.voice_clients, guild = interaction.guild)
        author = interaction.guild.get_member(interaction.user.id)
        await interaction.response.defer(thinking = True)
        if (voice_state == None):
            channel = author.voice.channel
            try:    
                await channel.connect()
            except discord.ClientException:
                pass
            except:
                await interaction.followup.send(f"{Assets.red_tick} **Something went wrong, please try later.**")
                return
            await interaction.followup.send(f"{Assets.green_tick} **Joined {channel.mention}**")

        if interaction.guild_id not in self.loop:
            self.loop[interaction.guild_id] = False
        if not interaction.guild.voice_client.is_playing():
            await self.play_music(interaction, query)
        else:  
            info = self.get_query_info(interaction, query)
            if interaction.guild_id in self.queue:
                self.queue[interaction.guild_id].append(info)
            else:
                self.queue[interaction.guild_id] = [info]
            
            embed = discord.Embed(
                description = f"🎵** Added to queue** 🎵",
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
            embed.add_field(
                name = "Queue length",
                value = f"{len(self.queue[interaction.guild_id])} song" + ("s" if len(self.queue[interaction.guild_id]) > 1 else "")
            )
            embed.set_thumbnail(url = info["thumbnail"])
            embed.set_footer(
                text = f"👀 {info['view_count']} | 👍 {info['like_count']}"
            )
            await interaction.followup.send(embed = embed)
    
    @app_commands.command(name = 'queue', description = "Display the queue!")
    async def _queue(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        total_time = 0
        if interaction.guild_id not in self.queue or len(self.queue[interaction.guild_id]) == 0:
            await interaction.followup.send("Nothing to see here")
            return
        
        song_list = ""
        for i in range(0, len(self.queue[interaction.guild_id])):
            info = self.queue[interaction.guild_id][i]
            song_list += f"`{i + 1}.` [{info['title']}](https://youtube.com/watch?v={info['display_id']}) **[{datetime.timedelta(seconds=int(info['duration']))}]** | {info['requester']}\n\n"
            total_time += int(info['duration'])
        
        try:
            np_info = self.np[interaction.guild_id]
            np_msg = f"[{np_info['title']}](https://youtube.com/watch?v={np_info['display_id']}) **[{datetime.timedelta(seconds=int(np_info['duration']))}]** | {np_info['requester']}"
        except:
            np_info = None 
            np_msg = ""
        embed = discord.Embed(
            color = discord.Color.orange()
        )
        embed.description = f"""
        **Now playing:**
        {np_msg}

        **Up Next:**    
        {song_list}
        """
        embed.add_field(
            name = "Queue length",
            value = f"{len(self.queue[interaction.guild_id])} song" + ("s" if len(self.queue[interaction.guild_id]) > 1 else "")
        )
        embed.add_field(
            name = "Queue duration",
            value = f"{datetime.timedelta(seconds=int(info['duration']))}"
        )
        embed.set_author(
            name = f"Queue for {interaction.guild.name}",
            icon_url = interaction.guild.icon.url if interaction.guild.icon else None
        )
        embed.set_thumbnail(
            url = np_info["thumbnail"] if np_info else None
        )
        embed.set_footer(
            text = f"{interaction.user.name}#{interaction.user.discriminator}",
            icon_url = interaction.user.display_avatar.url
        )

        await interaction.followup.send(embed = embed)
    
    @app_commands.command(name = 'loop', description = "Toggle looping!")
    async def _loop(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        self.loop[interaction.guild_id] = not self.loop[interaction.guild_id]
        
        await interaction.followup.send(f"{Assets.green_tick} **Looping set to {self.loop[interaction.guild_id]}**")
        


async def setup(client):
    #await client.add_cog(Music(client), guilds=[discord.Object(id=1085444549125611530)])
    await client.add_cog(Music(client))
