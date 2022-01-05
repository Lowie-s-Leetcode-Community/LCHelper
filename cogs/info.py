import discord
from discord.ext import commands
from random import randint
import time
from datetime import datetime
from utils.asset import Assets
import typing
import calendar

start_time = datetime.now()

class info(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.command(name = "userinfo", aliases = ["ui", "user"])
    async def info(self, ctx, user: typing.Union[discord.Member, int] = None):
        if user == None:
            member = ctx.author
        else:
            if isinstance(user, discord.Member):
                try:
                    member = ctx.guild.get_member(user.id)
                except:
                    member = user
            elif isinstance(user, int):
                try:
                    member = await self.client.fetch_user(user)
                except:
                    member = None
            elif isinstance(user, discord.ClientUser):
                await ctx.send("y u stalking me??!?")
                return
            else:
                member = None
        """
        await ctx.send(f"{user} - {type(user)}")
        await ctx.send(f"{member}.")
        """
        if isinstance(member, discord.Member):
            embed = discord.Embed(
                title = f"Information for user {member}",
                description = "",
                color = 0x03cffc,
                timestamp = ctx.message.created_at,
                author = ctx.message.author
            )
            created_at_time = str(time.mktime(member.created_at.timetuple()))[:-2]
            embed.add_field(
                name = "Created At:",
                value = f"<t:{created_at_time}>\n (<t:{created_at_time}:R>)",
                inline = True
            )
            embed.add_field(
                name = "ID:",
                value = member.id,
                inline = True
            )

            embed.add_field(
                name = "Avatar URL:",
                value = f"[Here]({member.avatar_url})",
                inline = True
            )
            """Line Break"""
            status = member.status
            if status is discord.Status.online: status_icon = Assets.online
            elif status is discord.Status.idle: status_icon = Assets.idle
            elif status is discord.Status.dnd: status_icon = Assets.dnd
            elif status is discord.Status.offline: status_icon = Assets.offline
            else: status_icon = ""
            embed.add_field(
                name = "Status:",
                value = f"{status_icon} {str(member.status).capitalize()}",
                inline = True
            )

            embed.add_field(
                name = "Animated Pfp?",
                value = member.is_avatar_animated(),
                inline = True
            )
            embed.add_field(
                name = "Bot?",
                value = "Confirmed" if (member.bot) else "System Bot" if (member.system) else "No",
                inline = True
            )

            joined_at_time = str(time.mktime(member.joined_at.timetuple()))[:-2]
            embed.add_field(
                name = "Server Join Date",
                value = f"<t:{joined_at_time}>\n (<t:{joined_at_time}:R>)",
                inline = True
            )

            embed.add_field(
                name = "Highest Role:",
                value = f"{member.top_role} \n ({member.color})",
                inline = True
            )

            embed.add_field(
                name = "Nickname:",
                value = member.nick,
                inline = True
            )

            embed.set_thumbnail(
                url = member.avatar_url
            )
            embed.set_footer(
                #text = f"Requested by {ctx.message.author} - Today at {ctx.message.created_at.today().strftime('%H:%M')}",
                text = ctx.author,
                icon_url = ctx.message.author.avatar_url
            )
            await ctx.send(embed=embed)
        elif isinstance(member, discord.User):
            user = member
            embed = discord.Embed(
                title = f"Information for user {user.name}#{user.discriminator}",
                color = 0x03cffc,
                timestamp = ctx.message.created_at
            )
            created_at_time = str(time.mktime(user.created_at.timetuple()))[:-2]
            embed.add_field(
                name = "Created At:",
                value = f"<t:{created_at_time}>\n (<t:{created_at_time}:R>)",
                inline = True
            )
            embed.add_field(
                name = "ID:",
                value = user.id,
                inline = True
            )

            embed.add_field(
                name = "Avatar URL:",
                value = f"[Here]({user.avatar_url})",
                inline = True
            )

            embed.add_field(
                name = "Animated Pfp?",
                value = user.is_avatar_animated(),
                inline = True
            )
            embed.add_field(
                name = "Bot?",
                value = "Confirmed" if (user.bot) else "System Bot" if (user.system) else "No",
                inline = True
            )

            embed.set_thumbnail(
                url = user.avatar_url
            )
            embed.set_footer(
                #text = f"Requested by {ctx.message.author} - Today at {ctx.message.created_at.today().strftime('%H:%M')}",
                text = ctx.author,
                icon_url = ctx.message.author.avatar_url
            )
            await ctx.send(embed=embed)
        else: await ctx.send(f"{Assets.red_tick} **Invalid Arguments Passed**")

    @commands.command(name = "serverinfo", aliases = ["si", "server"])
    async def _serverinfo(self, ctx):
        server = ctx.message.guild
        servername = server.name
        embed = discord.Embed(
            title = f"Information for `{servername}` Server",
            description = "",
            color = 0x03cffc,
            timestamp = ctx.message.created_at,
            author = ctx.message.author
        )
        created_at_time = str(time.mktime(server.created_at.timetuple()))[:-2]
        embed.add_field(
            name = "Created At:",
            value = f"<t:{created_at_time}>\n (<t:{created_at_time}:R>)",
            inline = True
        )
        embed.add_field(
            name = "Server Owner:",
            value = server.owner,
            inline = True
        )
        embed.add_field(
            name = "Server Icon:",
            value = f"[Here]({str(ctx.guild.icon_url)})",
            inline = True
        )
        embed.add_field(
            name = "Server ID:",
            value = server.id,
            inline = True
        )
        embed.add_field(
            name = "Member Count:",
            value = server.member_count,
            inline = True
        )
        embed.add_field(
            name = "Verification Level:",
            value = server.verification_level,
            inline = True
        )
        f = server.afk_channel
        res = "None"
        if (f != None): res = f"<#{f.id}>"

        embed.add_field(
            name = "AFK channel:",
            value = res,
            inline = True
        )

        embed.add_field(
            name = "AFK timeout:",
            value = f"{server.afk_timeout} seconds",
            inline = True
        )
        embed.add_field(
            name = "\u200b",
            value = "\u200b",
            inline = True
        )
        embed.set_thumbnail(
            url = ctx.message.guild.icon_url
        )
        guild_fetched = await ctx.bot.fetch_guild(ctx.guild.id)
        online_count = 0
        bot_count = 0
        for i in ctx.guild.members:
            if (str(i.status) == "online"): online_count += 1
            if (i.bot): bot_count += 1

        embed.add_field(
            name = "Members:",
            value = f"""Total: **{len(server.members)}**/{guild_fetched.max_members}
            Online: **{online_count}**/{len(server.members)}
            Offline: **{len(server.members) - online_count}**/{len(server.members)}
            Bots: **{bot_count}**/{len(server.members)}
            """,
            inline = True
        )
        embed.add_field(
            name = "Channels:",
            value = f"""
            Total: **{len(server.channels)}**/500
            Text: **{len(server.text_channels)}**/{len(server.channels)}
            Voice: **{len(server.voice_channels)}**/{len(server.channels)}
            Stage: **{len(server.stage_channels)}**/{len(server.channels)}
            """,
            inline = True
        )

        max_emojis = 100
        if server.premium_tier == 1: max_emojis = 200
        elif server.premium_tier == 2: max_emojis = 300
        elif server.premium_tier == 3: max_emojis = 500
        embed.add_field(
            name = "Other stuff:",
            value = f"""Roles: **{len(server.roles)}**/250
            Emojis: **{len(server.emojis)}**/{max_emojis}
            Boosts: **{ctx.guild.premium_subscription_count}**
            """,
            inline = True
        )
        embed.set_footer(
            #text = f"Requested by {ctx.message.author} - Today at {ctx.message.created_at.today().strftime('%H:%M')}",
            text = ctx.author,
            icon_url = ctx.message.author.avatar_url
        )
        await ctx.send(embed = embed)

    @commands.command(name = "botinfo", aliases = ["bi", "binfo"])
    async def _botinfo(self, ctx):
        bot_member = await ctx.guild.fetch_member(self.client.user.id)
        embed = discord.Embed(
            title = "My Info!",
            descrition = "",
            color = 0x03cffc,
            timestamp = ctx.message.created_at,
            author = ctx.message.author
        )
        created_at_time = str(time.mktime(bot_member.created_at.timetuple()))[:-2]
        embed.add_field(
            name = "Created At:",
            value = f"<t:{created_at_time}>\n (<t:{created_at_time}:R>)",
            inline = True
        )

        embed.add_field(
            name = "ID:",
            value = bot_member.id,
            inline = True
        )
        embed.add_field(
            name = "Avatar URL:",
            value = f"[Here]({bot_member.avatar_url})",
            inline = True
        )
        joined_at_time = str(time.mktime(bot_member.joined_at.timetuple()))[:-2]
        embed.add_field(
            name = "Joined At:",
            value = f"<t:{joined_at_time}>\n (<t:{joined_at_time}:R>)",
            inline = True
        )

        embed.add_field(
            name = "Highest Role:",
            value = f"{bot_member.top_role} \n ({bot_member.color})",
            inline = True
        )

        embed.add_field(
            name = "Nickname:",
            value = bot_member.nick,
            inline = True
        )
        owner = (await self.client.application_info()).owner
        embed.add_field(
            name = "Owner:",
            value = f"{owner}",
            inline = True
        )
        embed.add_field(
            name = "Looking:",
            value = f"{len(self.client.guilds)} servers",
            inline = True
        )
        embed.add_field(
            name = "Library:",
            value = f"discord.py ({discord.__version__})",
            inline = True
        )
        embed.add_field(
            name = "Commands:",
            value = f"{len(self.client.commands)}",
            inline = True
        )
        embed.add_field(
            name = "Best Bot??!?",
            value = f"True",
            inline = True
        )
        embed.set_thumbnail(
            url = bot_member.avatar_url
        )

        embed.set_footer(
            text = ctx.author,
            icon_url = ctx.author.avatar_url
        )
        await ctx.send(embed = embed)


    @commands.command(name = "status")
    async def _status(self, ctx, member: discord.Member = None):
        if member == None: member = ctx.author
        status = member.activities
        embed = discord.Embed(
            title = f"{member}'s status",
            color = 0xff00cc
        )
        mstatus = member.status
        if mstatus is discord.Status.online: status_icon = Assets.online
        elif mstatus is discord.Status.idle: status_icon = Assets.idle
        elif mstatus is discord.Status.dnd: status_icon = Assets.dnd
        elif mstatus is discord.Status.offline: status_icon = Assets.offline
        else: status_icon = ""
        embed.add_field(
            name = "Status:",
            value = f"{status_icon} {str(member.status).capitalize()}",
            inline = True
        )

        for i in status:
            if (i.type == discord.ActivityType.custom):
                embed.add_field(name = f"Custom: ", value = f"{i.name}", inline = True)
                continue
            elif (i.type == discord.ActivityType.listening):
                if i.name == "Spotify":
                    embed.add_field(
                        name = f"{i.type.name.capitalize()}:",
                        value = f"**Spotify** - Song: {i.title} - {i.artist.replace(';', ',')}",
                        inline = False
                    )
                else:
                    try:
                        resp = f"{i.name} ({str(datetime.now() - datetime.fromtimestamp(calendar.timegm(i.timestamps['start'].timetuple())))[:-7]})"
                    except: resp = f"{i.name}"
                    embed.add_field(
                        name = f"{i.type.name.capitalize()}:",
                        value = resp,
                        inline = False
                    )
                continue
            elif (i.type == discord.ActivityType.playing):
                embed.add_field(
                    name = f"{i.type.name.capitalize()}:",
                    value = f"{i.name} ({str(datetime.now() - datetime.fromtimestamp(calendar.timegm(i.start.timetuple())))[:-7]})",
                    inline = False
                )
                continue
            elif (i.type == discord.ActivityType.streaming):
                embed.add_field(
                    name = f"{i.type.name.capitalize()}:",
                    value = f"**[{i.platform}]({i.url})** - {i.name} - playing {i.game}",
                    inline = False
                )
                continue
            elif (i.type == discord.ActivityType.watching):
                try:
                    resp = f"{i.name} ({str(datetime.now() - datetime.fromtimestamp(calendar.timegm(i.timestamps['start'].timetuple())))[:-7]})"
                except: resp = f"{i.name}"
                embed.add_field(
                    name = f"{i.type.name.capitalize()}:",
                    value = resp,
                    inline = False
                )
                continue
            elif (i.type == discord.ActivityType.competing):
                try:
                    resp = f"{i.name} ({str(datetime.now() - datetime.fromtimestamp(calendar.timegm(i.timestamps['start'].timetuple())))[:-7]})"
                except: resp = f"{i.name}"
                embed.add_field(
                    name = f"{i.type.name.capitalize()}:",
                    value = resp,
                    inline = False
                )
                continue
        await ctx.send(embed = embed)


    @commands.command(name = "avatar", aliases = ["av"])
    async def _avatar(self, ctx, obj: discord.User = None):
        if obj == None: obj = ctx.author
        embed = discord.Embed(
            title = f"{obj}'s avatar:",
            description = "",
            color = 0x03cffc,
            timestamp = ctx.message.created_at
        )
        embed.set_image(url = obj.avatar_url)
        embed.set_footer(
            text = ctx.author,
            icon_url = ctx.author.avatar_url
        )
        await ctx.send(embed = embed)
def setup(client):
    client.add_cog(info(client))
