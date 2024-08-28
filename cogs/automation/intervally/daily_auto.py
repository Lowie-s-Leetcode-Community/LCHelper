import datetime
import os
import random
import traceback

import discord
from discord import app_commands
from discord.ext import commands, tasks

from lib.embed.contest_embed import ContestEmbed
from lib.embed.problem import ProblemEmbed
from utils.asset import Assets
from utils.lc_utils import LC_utils
from utils.llc_datetime import get_today
from utils.logger import Logger

COG_START_TIMES = [
    datetime.time(hour=0, minute=5, tzinfo=datetime.timezone.utc)
]

class DailyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.daily.start()
        self.logger = Logger(client)

    async def cog_unload(self):
        self.daily.cancel()

    async def create_new_daily_object(self):
        # {'date': '2024-02-09', 'link': 'https://leetcode.com/problems/largest-divisible-subset/', 'title': 'Largest Divisible Subset', 'title_slug': 'largest-divisible-subset', 'id': '368'}
        daily_challenge_info = LC_utils.get_daily_challenge_info()
        await self.client.db_api.create_or_keep_daily_object(daily_challenge_info['id'], get_today())
        return daily_challenge_info

    async def create_daily_thread(self, daily_challenge_info):
        # Creating daily thread
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        name = f"[{daily_challenge_info['date']}] LeetCode P{daily_challenge_info['id']}"
        thread = await channel.create_thread(name = name, type = discord.ChannelType.public_thread)

        # Calling /daily automatically
        daily_obj = self.client.db_api.read_latest_daily_object()
        problem = daily_obj['problem']
        embed = ProblemEmbed(problem)

        display_date = daily_obj['generatedDate'].strftime("%b %d, %Y")
        
        await thread.send(f"Daily Challenge - {display_date}", embed = embed)
        return
    
    async def remind_unverified(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel("1090084731560927274")
        random_prompts = [
            f"{Assets.blob_victory} {Assets.blob_victory} Hãy sử dụng lệnh {Assets.link_command} để kết nối tài khoản Leetcode của mình và khám phá những tính năng độc đáo của chúng mình nhé!",
            f"Hãy {Assets.link_command} tài khoản bằng LLC Assistant để luyện tập cùng chúng mình nào! {Assets.blob_taco} {Assets.blob_taco}",
            f"Ồ, chào bạn. Có vẻ bạn quên {Assets.link_command} tài khoản Leetcode nè! {Assets.blob_maman} {Assets.blob_taco}",
            f":eyes: :eyes: Bạn có biết, {Assets.link_command} tài khoản Leetcode với chúng mình sẽ giúp bạn đạt mục tiêu dễ dàng hơn?",
            f":100: :100: :100: :100: :100: Đã có trên 200 người {Assets.link_command} tài khoản với chúng mình. Một phần không nhỏ đã đạt được mục tiêu 500 bài. Liệu bạn có phải người tiếp theo? {Assets.blob_taco} {Assets.blob_taco}",
            f":beers: :game_die: {Assets.link_command} tài khoản, tham gia cùng server, để không bỏ lỡ thông báo mới nhất về các buổi offline nhé! {Assets.blob_taco} {Assets.blob_taco} {Assets.blob_taco}",
            f":eyes: {Assets.blob_taco} {Assets.blob_taco} Chúng mình có bí kíp code khủng mà vẫn được chạm cỏ thường xuyên. :eyes: :eyes: -> {Assets.link_command}",
        ]
        prompt = random.choice(random_prompts)
        await channel.send(f"<@&{self.client.config['unverifiedRoleId']}> {prompt}")

    async def contest_remind(self):
        next_contests = LC_utils.get_next_contests_info()
        current_time = datetime.datetime.now()
        time_in_24h = current_time + datetime.timedelta(days=1)
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['dailyThreadChannelId'])
        embeds = []
        for contest in next_contests:
            if current_time.timestamp() <= contest["timestamp"] <= time_in_24h.timestamp():
                embeds.append(ContestEmbed(contest))

        if len(embeds) == 0:
            return

        message = f"<@&{self.client.config['verifiedRoleId']}> :bangbang: :ninja: There is a contest today!"
        await channel.send(message, embeds=embeds)

    @tasks.loop(time=COG_START_TIMES)
    async def daily(self):
        await self.logger.on_automation_event("Daily", "start-daily")
        await self.logger.on_automation_event("Daily", "create_new_daily_object()")
        daily_challenge_info = await self.create_new_daily_object()
        await self.logger.on_automation_event("Daily", "create_daily_thread()")
        await self.create_daily_thread(daily_challenge_info)
        await self.logger.on_automation_event("Daily", "contest_remind()")
        await self.contest_remind()
        await self.logger.on_automation_event("Daily", "remind_unverified()")
        await self.remind_unverified()
        await self.logger.on_automation_event("Daily", "end-daily")

    @daily.error
    async def on_error(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"Daily initiate error:\n```py\n{traceback.format_exc()[:800]}```\nPlease re-start.")
        await self.logger.on_automation_event("Daily", "error found")

        self.daily.restart()

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def stop_daily(self, ctx):
        self.daily.stop()
        await ctx.send(f"{Assets.green_tick} **Daily task stopped.**")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def start_daily(self, ctx):
        self.daily.start()
        await ctx.send(f"{Assets.green_tick} **Daily task started.**")

    @app_commands.command(name="daily_simulate", description="Simulate a daily crawl cycle.")
    @app_commands.checks.has_permissions(administrator = True)
    async def _daily_simulate(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        await self.daily()
        await interaction.followup.send(f"{Assets.green_tick} **Daily Task finished**")

async def setup(client):
    await client.add_cog(DailyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])
