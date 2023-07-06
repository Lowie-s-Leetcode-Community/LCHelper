import discord
from discord import app_commands
from discord.ext import tasks, commands
import asyncio
import datetime
import textwrap
from typing import Optional

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: 
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def get_registration_announce_msg(message):
    d = datetime.date.today()
    next_mon = next_weekday(d, 0)
    next_tue = next_mon + datetime.timedelta(days=1)
    next_wed = next_mon + datetime.timedelta(days=2)
    next_thu = next_mon + datetime.timedelta(days=3)
    next_fri = next_mon + datetime.timedelta(days=4)
    next_sat = next_mon + datetime.timedelta(days=5)
    next_sun = next_mon + datetime.timedelta(days=6)

    reg_msg = f"""
    Xin chào buổi tối, các thành viên LLC,
    {message}

    2️⃣: Thứ 2, {next_mon}
    3️⃣: Thứ 3, {next_tue} 
    4️⃣: Thứ 4, {next_wed}
    5️⃣: Thứ 5, {next_thu}
    6️⃣: Thứ 6, {next_fri}
    7️⃣: Thứ 7, {next_sat}
    8️⃣: Chủ Nhật, {next_sun}

    Sincerely,
    """ 

    return textwrap.dedent(reg_msg)

def get_next_LLC_week_and_month():
    d = datetime.date.today()
    next_mon = next_weekday(d, 0)
    week_no = int(next_mon.day / 7) + 1
    month_no = next_mon.month

    return week_no, month_no


class daily_reg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'start_daily_reg', description = "Khởi tạo một thread đăng ký Chữa Daily của tuần tiếp theo")
    @app_commands.describe(message = "Tin nhắn kèm theo thread đăng ký")
    @app_commands.checks.has_permissions(administrator = True)
    async def _start_daily_reg(self, interaction: discord.Interaction, message: Optional[str] = "__placeholder__"):
        await interaction.response.defer(thinking = True)

        if message == "__placeholder__":
            week, month = get_next_LLC_week_and_month()
            message = f"Form đăng ký chữa Daily tuần {week} tháng {month} đã chính thức mở. Mọi người đăng ký nhiệt tình nhé. Chúc các bạn một tuần giải thuật vui vẻ."

        msg = get_registration_announce_msg(message)
        reg_mes = await interaction.followup.send(content = msg)
        await reg_mes.add_reaction("2️⃣")
        await reg_mes.add_reaction("3️⃣")
        await reg_mes.add_reaction("4️⃣")
        await reg_mes.add_reaction("5️⃣")
        await reg_mes.add_reaction("6️⃣")
        await reg_mes.add_reaction("7️⃣")
        await reg_mes.add_reaction("8️⃣")

async def setup(client):
    await client.add_cog(daily_reg(client))