import textwrap

import discord
from discord.ext import tasks, commands
import os
import traceback
import datetime
from utils.logger import Logger

COG_START_TIMES = [
    datetime.time(hour=12, minute=00, tzinfo=datetime.timezone.utc)
]

class WeeklyAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        if os.getenv('START_UP_TASKS') == "True":
            self.weekly.start()
        self.logger = Logger(client)

    def cog_unload(self):
        self.weekly.cancel()

    async def create_weekly_thread(self):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel("1085456207067762738")
        week, month = self.get_next_LLC_week_and_month()
        message = (f"Form đăng ký chữa Daily tuần {week} tháng {month} đã chính thức mở. "
                   f"Mọi người đăng ký nhiệt tình nhé. Chúc các bạn một tuần giải thuật vui vẻ.")
        content, firstday, lastday = self.get_registration_announce_msg(message)
        name = f"Đăng ký chữa Daily tuần {week} tháng {month} ({firstday}/{week} - {lastday}/{week})"

        thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread)
        reg_mes = await thread.send(content)
        await reg_mes.add_reaction("2️⃣")
        await reg_mes.add_reaction("3️⃣")
        await reg_mes.add_reaction("4️⃣")
        await reg_mes.add_reaction("5️⃣")
        await reg_mes.add_reaction("6️⃣")
        await reg_mes.add_reaction("7️⃣")
        await reg_mes.add_reaction("8️⃣")
        return

    def next_weekday(self, d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    def get_next_LLC_week_and_month(self):
        d = datetime.date.today()
        next_mon = self.next_weekday(d, 0)
        week_no = int((next_mon.day - 1) / 7) + 1
        month_no = next_mon.month

        return week_no, month_no

    def get_registration_announce_msg(self, message):
        d = datetime.date.today()
        weekdays = []
        next_mon = self.next_weekday(d, 0)
        weekdays.append(next_mon)
        for i in range(6):
            weekdays.append(next_mon + datetime.timedelta(days = i + 1))

        reg_msg = f"""
        Xin chào buổi tối, các thành viên LLC,
        {message}

        2️⃣: Thứ 2, {weekdays[0]}
        3️⃣: Thứ 3, {weekdays[1]} 
        4️⃣: Thứ 4, {weekdays[2]}
        5️⃣: Thứ 5, {weekdays[3]}
        6️⃣: Thứ 6, {weekdays[4]}
        7️⃣: Thứ 7, {weekdays[5]}
        8️⃣: Chủ Nhật, {weekdays[6]}

        Sincerely,
        """
        return textwrap.dedent(reg_msg), weekdays[0].day, weekdays[6].day

    @tasks.loop(time=COG_START_TIMES)
    async def weekly(self):
        if datetime.date.today().weekday() == 5:
            await self.logger.on_automation_event("Weekly ", "create_weekly_form")
            await self.create_weekly_thread()

    @weekly.error
    async def on_error(self, exception):
        guild = await self.client.fetch_guild(self.client.config['serverId'])
        channel = await guild.fetch_channel(self.client.config['serverId'])
        await channel.send(f"Weekly initiate error:\n```py\n{traceback.format_exc()[:800]}```\nPlease re-start.")
        await self.logger.on_automation_event("Weekly", "error found")

        self.weekly.restart()

async def setup(client):
    await client.add_cog(WeeklyAutomation(client), guilds=[discord.Object(id=client.config['serverId'])])

