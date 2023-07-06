import discord
from discord import app_commands
from discord.ext import commands


class help_command(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'help', description = "Các câu lệnh của LCHelper")
    async def _help_command(self, interaction):
        await interaction.response.defer(thinking = True)
        
        embed = discord.Embed(
            color = 0xff822e,
        )
        embed.set_author(
            name = "Những câu lệnh để tương tác với hệ thống LCHelper",
            icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
        )

        embed.add_field(
            name = "🔗  Xác nhận, kết nối tài khoản",
            value = f"""
            `/link {{leetcode_username}}`: Kết nối tài khoản LeetCode với tài khoản Discord trong Lowie’s LeetCode Club. Hướng dẫn cụ thể trong kênh chat <#1092451759890374747>.
            ⠀
            """,
            inline = False
        )
        embed.add_field(
            name = "🗃️  Xem thông tin LLC membership",
            value = f"""
            `/profile`: Các dữ liệu điểm số của thành viên CLB trên hệ thống LLC.\n`/tasks`: Các nhiệm vụ để có thể kiếm điểm trong LLC.
            ⠀
            """,
            inline = False
        )
        embed.add_field(
            name = "📊  Xem các bảng xếp hạng",
            value = f"""
            `/ranklist score`: Bảng xếp hạng tháng điểm số của các thành viên trong CLB.\n`/ranklist streak`: Bảng xếp hạng về chuỗi AC Daily dài nhất trong CLB.
            ⠀
            """,
            inline = False
        )
        embed.add_field(
            name = "📝  LeetCode Problems",
            value = f"""
            `/daily`: Trả về bài Daily trên LeetCode của ngày hôm nay.\n`/gimme`: Chọn một bài LeetCode ngẫu nhiên trên CSDL của LeetCode. Member có thể chọn độ khó và chủ đề mong muốn qua các tham số, và loại những chủ đề không mong muốn.
            """,
            inline = False
        )
        embed.add_field(
            name = "⠀",
            value = "[Chi tiết các câu lệnh có thể được xem tại đây](https://lowie-writes.notion.site/LCHelper-Documentation-d85de63f31144bc383136ab9f5804527?pvs=4)",
        )

        await interaction.followup.send(embed = embed)


async def setup(client):
    await client.add_cog(help_command(client))