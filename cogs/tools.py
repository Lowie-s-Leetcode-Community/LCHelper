import discord
import os
from discord.ext import commands
from datetime import datetime
import typing
import urllib
import requests
from utils.asset import Assets

def name_check(emoji_name):
    emoji_name = emoji_name.replace(" ", "_")
    if len(emoji_name) > 32:
        return False
    for i in range(len(emoji_name)):
        if not ('a' <= emoji_name[i].lower() <= 'z' or '0' < emoji_name[i] < '9' or emoji_name[i] == '_'):
            return False
    return emoji_name

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
                icon_url = ctx.author.avatar.url
            )
            await ctx.send(embed=embed)


    def perms(ctx):
        return ctx.author.id in [382534096427024385, 535811480629542921, 683328026943160464]

    """
    @commands.command(name = "cpp", aliases = ["compile", "amongus"])
    @commands.check(perms)
    async def _cpp(self, ctx, *, code):
        if "system" in code:
            await ctx.send("What you t")
        if "`" in code:
            code = "\n".join(code.split("\n")[1:-1])
        if "include" not in code: 
            code = "#include <bits/stdc++.h>\nusing namespace std;\nsigned main() {\n" + code + "\n}"

        with open("amongus.cpp", "w") as f:
            f.write(code)

        data = ""
        try:   
            os.system("g++ amongus.cpp -o amongus 2>error.txt && amongus >amongus.txt ")

            with open("error.txt", "r") as f:
                data = f.read()
                if (data != ""):
                    raise TypeError("Compile Error")

            with open("amongus.txt", "r") as f:
                data = f.read()
                await ctx.send(f"```\n{data}\n```")

        except TypeError:
            with open("error.txt", "r") as f:
                await ctx.send(f"```\n{data[:min(len(data), 1900)]}\n```")

        except:
            await ctx.send("Something went wrong. You still suck.")
    
    """
    @commands.group(name = "emote", aliases = ["emoji", "yoink"])
    async def _emote(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title = "Emoji Commands group",
                color = 0xaaff00,
                timestamp = ctx.message.created_at
            )
            embed.add_field(
                name = "Available commands:",
                value = "`add`, `remove`, `view`, `rename`",
                inline = True
            )
            embed.add_field(
                name = "Alias:",
                value = f"`emote`, `yoink`",
                inline = False
            )
            embed.set_footer(
                text = ctx.author,
                icon_url = ctx.message.author.avatar.url
            )
            await ctx.send(embed = embed)

    @_emote.command(name = "add")
    async def _add(self, ctx, emoji: typing.Union[discord.PartialEmoji, str], *, emoji_name: str = None):
        if isinstance(emoji, discord.PartialEmoji):
            if emoji.is_unicode_emoji():
                await ctx.send("You tried to add a default emoji. Your insane")
                return
            if emoji.is_custom_emoji():
                if emoji_name == None: emoji_name = emoji.name
                else: emoji_name = name_check(emoji_name)
                if emoji_name == False:
                    await ctx.send(f"{Assets.red_tick} Invalid Emoji Name")
                    return
                resp = requests.get(emoji.url)
                emoji_added = await ctx.guild.create_custom_emoji(name = emoji_name, image = resp.content)
                await ctx.send(f"{Assets.green_tick} **Emote Added:** {emoji_added} - `:{emoji_name}:`")
        elif isinstance(emoji, str):
            if emoji_name == None: emoji_name = "Unnamed"
            else: emoji_name = name_check(emoji_name)
            if emoji_name == False:
                await ctx.send(f"{Assets.red_tick} **Invalid Emoji Name**")
                return
            resp = requests.get(emoji)
            emoji_added = await ctx.guild.create_custom_emoji(name = emoji_name, image = resp.content)
            await ctx.send(f"{Assets.green_tick} **Emote Added: {emoji_added} - `:{emoji_name}:`**")
                #await ctx.send(f"{Assets.red_tick} **Invalid Input**")
        else: await ctx.send(f"{Assets.red_tick} **Something gone wrong**")


    @_emote.command(name = "remove", aliases = ["delete"])
    async def _remove(self, ctx, *, emoji: typing.Union[discord.PartialEmoji, str]):
        if isinstance(emoji, discord.PartialEmoji):
            guild_emoji = discord.utils.find(lambda m: m == emoji, ctx.guild.emojis)
            if guild_emoji:
                await guild_emoji.delete()
                await ctx.send(f"{Assets.green_tick} **Emote Removed: `:{guild_emoji.name}:`**")
            else: await ctx.send(f"{Assets.red_tick} **Emote Not Found**")
        elif isinstance(emoji, str):
            emoji = name_check(emoji)
            if emoji == None:
                await ctx.send(f"{Assets.red_tick} **Emote Not Found**")
                return
            guild_emoji = discord.utils.find(lambda m: m.name == emoji, ctx.guild.emojis)
            if guild_emoji:
                await guild_emoji.delete()
                await ctx.send(f"{Assets.green_tick} **Emote Removed: `:{guild_emoji.name}:`**")
            else: await ctx.send(f"{Assets.red_tick} **Emote Not Found**")

    @_emote.command(name = "view")
    async def _view(self, ctx, *, emoji: typing.Union[discord.PartialEmoji, str]):
        if isinstance(emoji, discord.PartialEmoji):
            await ctx.send(emoji.url)
        else:
            emoji = name_check(emoji)
            if emoji == None:
                await ctx.send(f"{Assets.red_tick} **Emote Not Found**")
                return
            guild_emoji = discord.utils.find(lambda m: m.name == emoji, ctx.guild.emojis)
            if guild_emoji: await ctx.send(guild_emoji.url)
            else: await ctx.send(f"{Assets.red_tick} **Emote Not Found**")

    @_emote.command(name = "rename")
    async def _rename(self, ctx, emoji: typing.Union[discord.PartialEmoji, str], *, emoji_name: str):
        guild_emoji = discord.utils.find(lambda m: m == emoji or m.name == emoji, ctx.guild.emojis)
        if guild_emoji:
            f = name_check(emoji_name)
            if f == False:
                await ctx.send(f"{Assets.red_tick} Invalid Emoji Name")
                return
            old_name = guild_emoji.name
            await guild_emoji.edit(name = f)
            await ctx.send(f"{Assets.green_tick} **Emote Renamed: {guild_emoji} - `:{old_name}:` -> `:{emoji_name}:`**")
        else: await ctx.send(f"{Assets.red_tick} **Emote Not Found**")

async def setup(client):
    await client.add_cog(tools(client))
