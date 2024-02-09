import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
import asyncio

STARTING_STORY_MSG = """
Câu chuyện bắt nguồn từ một buổi Seminar được tổ chức dành cho các anh em ở UET K66-CN8, nơi mà anh già Lowie chia sẻ với các anh em trong khóa về 2 năm bán mình cho tư bản của anh ta.

Trong seminar đó có nêu ra ba cách để các bạn cải thiện hồ sơ của mình trong những năm còn lại trên đại học:

1. Tham gia các sự kiện Hackathon, CTF, Job Fair, …
2. Luyện tập Cấu Giải và kỹ năng giải quyết vấn đề
3. Làm sản phẩm

Trong đó, việc học Cấu Giải là tối quan trọng, khi các ứng viên với kỹ năng Giải thuật tốt luôn được “ưu ái” khi phỏng vấn vào các tập đoàn công nghệ. Việc trở nên thực sự “thành thạo” được bộ môn này, nhiều người vẫn cho rằng là đặc quyền của dân chuyên Toán-Tin, đã được học code từ rất lâu trước khi lên Đại học.

**Lowie’s Leetcode Club** được sinh ra để chứng minh điều đó hoàn toàn sai. Để làm được điều này, chúng mình mong muốn có thể trở thành một chỗ dựa vững chắc cho các bạn, trong quá trình các bạn tìm kiếm những công việc đầu tiên, và thực thi ước mơ của mình.

*Vào ngày 15/03/2023, Lowie’s Leetcode Club (hiện tại là Lowie's Leetcode Community) chính thức được khai sinh với 6 thành viên UET K66-CACLC1 Core Team, cùng khoảng 15 anh em khác tham gia luyện tập.*
"""

Community_MISSION_MSG = """
Sứ mệnh của Lowie’s Leetcode Community ban đầu là tạo môi trường để các bạn luyện tập Leetcode - nền tảng các bài tập phỏng vấn dành cho các bạn giàu tham vọng đỗ được những doanh nghiệp, tập đoàn lớn.

Tới đây, khi các bạn UET **K66 - “first gen”** của Cộng đồng - sẽ bước vào quá trình chuẩn bị hồ sơ và tìm kiếm những cơ hội đầu tiên, cũng là lúc chúng mình sẽ hoạt động mạnh mẽ nhất. Bằng được, mình mong muốn các bạn tham gia Cộng đồng đạt được những gì các bạn mong đợi từ lúc các bạn Verify tài khoản của mình. Động thái đầu tiên, chúng mình đã cho khai giảng Lowie’s Leetcode Class YELLOW - nơi các đơn vị kiến thức trong các bài phỏng vấn ở các doanh nghiệp được mình chia sẻ.

Mình mong muốn, 1 năm nữa, được nhìn thấy những thành viên đầu tiên của Cộng đồng giành lấy được những bản hợp đồng thực tập giá trị ở các doanh nghiệp lớn trong nước (chẳng hạn: VinAI/VinBigData, Kyber Network, …), hay các doanh nghiệp nước ngoài (WorldQuant, DTL, Grab, Shopee, …). Thậm chí, nếu may mắn, chúng ta có thể đào tạo được những Thực tập sinh Google hay Amazon trong Cộng đồng của mình.
"""

Community_ACTIVITIES_MSG = """
Để phục vụ sứ mệnh của Cộng đồng, các hoạt động trong Cộng đồng cũng đã và đang được triển khai dựa vào nhu cầu học tập của các bạn:

- **Daily Problem Editorial:** Nơi các bạn mới học có thể tìm gợi ý/lời giải cho bài tập Daily trên Leetcode, và cũng là nơi các bạn đã có kinh nghiệm có thể tập diễn đạt, trình bày ý tưởng của mình cho các bạn khác trong Cộng đồng.
- **Lowie’s Leetcode Class:** Nơi mà Lowie cùng ban chuyên môn sẽ mở lớp buổi tối để giúp các bạn lấp đầy những lỗ hổng về kiến thức, cũng như kỹ năng phỏng vấn. Lớp học có tính phí, và các bạn có quyền lợi sử dụng 1 năm Leetcode Premium.
- **Chuyên Đề**: Nơi tất cả thành viên trong LLC cùng luyện tập & cọ xát cho một chủ đề nào đó.
- **Bot LC Helper (a.k.a. “Đủ 500 bài LeetCode chưa?”)**: Các bạn đang có thời gian luyện LeetCode, nhưng Cộng đồng đang không có hoạt động gì cho mình? Hãy gõ </help:1130172149659881593> ở các kênh chat trong Discord để Con trai cưng của chúng mình hỗ trợ các bạn luyện tập nhé!
Ngoài ra, chúng mình cũng có một hệ thống BẢNG XẾP HẠNG để các bạn có thể đua điểm với nhau, giành lấy danh hiệu Leetcoders of the Month và những phần quà giá trị khác từ Chủ tịch Cộng đồng.

Các bạn có thể đọc đầy đủ về danh sách các hoạt động trong Cộng đồng ở [ĐÂY](https://hackmd.io/@lowies-leetcode-Community/HkYbivnnn).
"""

Community_CORE_TEAM_MSG_1 = """
<@318049602160951297> - Là một người đã có 2 năm kinh nghiệm ở các môi trường doanh nghiệp, và 7 năm kinh nghiệm trong bộ môn Lập trình Thi đấu, anh cả Lowie đã thành lập lên Cộng đồng với hoài bão giúp các anh em xung quanh có thể vươn tới những ước mơ cháy bỏng của mình. ❤️‍🔥❤️‍🔥

Một số thành tích nổi bật:
- Hạng 14 ICPC National Vietnam 2020.
- Hạng 7 ICPC North American PACNW Regional 2019.
- Thành viên đội tuyển Việt Nam tham dự Olympic Tin học Châu Á - Thái Bình Dương 2019.

Xem CV của chủ tịch tại [ĐÂY](https://www.topcv.vn/xem-cv/D10DBgJXAVYGBlNSVQNUAwIFAwdTUFUHUAMGBg92be).
"""

Community_CORE_TEAM_MSG_2 = """
<@683328026943160464> - Là lớp trưởng của K66-CACLC1 (hay cậu thường gọi thân thương: K66A1), Lê Vũ Minh là một vị thủ lĩnh, luôn chăm chỉ và cố gắng làm tốt nhiệm vụ được giao. Bạn là người quản trị server Discord của Cộng đồng từ ngày thành lập đến tận bây giờ. Ngoài ra, bạn cũng đã và đang tham gia phát triển <@738713416914567198> - con trai cưng của Cộng đồng. 🤖🦸‍♂️
"""

Community_CORE_TEAM_MSG_3 = """
<@641562953862086657> - Với thái độ làm việc chuyên nghiệp, cùng khả năng làm việc độc lập xuất sắc khi đã hoàn thành 400 bài LeetCode trước ngày gia nhập Cộng đồng, Dân Trần là một cánh tay phải đắc lực của Chủ tịch. Không những vậy, tư duy sáng tạo và khả năng truyền đạt ý tưởng của Dân chính là nền tảng để giúp cho LLC có thể đi xa hơn. 🧠💪
"""

Community_CORE_TEAM_MSG_4 = """
Là một ban chịu trách nhiệm chính về chất lượng chuyên môn các hoạt động trong Cộng đồng, ban Chuyên Môn là một ban tuy “khó tính”, nhưng luôn hết lòng vì các thành viên trong Cộng đồng. Các thành viên trong ban Chuyên Môn đều là những người đã có những thành tích nhất định trong CV của họ, với các giải thưởng Tin học lớn nhỏ khác nhau. Và họ tham gia vào Core Team, để làm tấm gương sáng cho bất kỳ ai trong Cộng đồng phấn đấu.
"""

Community_CORE_TEAM_MSG_5 = """
Trái ngược với ban Chuyên Môn, thì ban Truyền Thông hay bị “Bí Thuật Toán” 😉. Tuy vậy, họ không bao giờ bị “bí” những ý tưởng. Ngoài việc quản lý kênh truyền thông, bộ mặt của Cộng đồng, họ chính là nguồn tài nguyên ý tưởng dồi dào cho sự phát triển của Cộng đồng. Mục tiêu của họ: biến LLC thành một Đế chế truyền thông lớn trong VNU, ít nhất, về ngành CNTT.
"""

Community_CORE_TEAM_MSG_6 = """
Là những người cha nuôi của con Bot trong Cộng đồng, các thành viên trong ban Tự Động Hóa mang trong tim niềm đam mê to lớn với việc phát triển sản phẩm. Đây cũng là những thành viên “hưởng lợi ngầm” nhiều nhất từ Cộng đồng, khi trong quá trình tham gia, họ tích lũy được kinh nghiệm làm việc, cũng như mang về được những thành phẩm để “flexing” trong hồ sơ của họ 💪😏
"""

HOW_TO_VERIFY_MSG_1 = """
Để tham gia vào các hoạt động Cộng đồng, bạn cần phải link tài khoản LeetCode của bạn với bot của server. Hãy [lập một tài khoản](https://leetcode.com/accounts/signup/) nếu bạn chưa có.

⚠️ Lưu ý, sau 7 ngày kể từ khi gia nhập mà bạn chưa link tài khoản, bạn sẽ tự động bị kick khỏi server. Hãy làm ngay và luôn để tránh bỏ lỡ những điều hay ho ✨
"""
HOW_TO_VERIFY_MSG_2 = """
Đăng nhâp vào tài khoản LeetCode của bạn và vào phần profile.
"""
HOW_TO_VERIFY_MSG_3 = """
Sau khi vào phần profile, bạn hãy nhìn lên cái đường dẫn URL của leetcode. Username ID của bạn sẽ là phần của đường link. Copy cái user ID đó.
"""
HOW_TO_VERIFY_MSG_4 = """
Trong kênh chat <#1090084731560927274>, bạn hãy gõ lệnh </link:1113100702886141993>  của <@738713416914567198>. Paste cái mã user ID của bạn vào tham số username.

Con bot sẽ generate ra một chuỗi kí tự dài 5 chữ. Bạn hãy copy chuỗi kí tự này và thực hiện các bước tiếp theo trong vòng 120 giây.
"""
HOW_TO_VERIFY_MSG_5 = """
Quay trở lại LeetCode, vào `Edit Profile`. Duới mục **Summary**, vào edit và paste cái mã 5 chữ đó vào rồi ấn `Save`.
"""
HOW_TO_VERIFY_MSG_6 = """
Quay trở lại Discord, bấm nút `Verify Me!` trên dòng tin nhắn của con bot. 

Nếu bạn làm các bước trên chính xác, thì bot sẽ báo thành công và bạn sẽ được nhận role <@&1087761988068855890>, chính thức xác nhận bạn là thành viên Cộng đồng 🎉🎉🎉.
"""

class gl(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "gl-init", description = "Sends initial embeds for info channels")
    @commands.has_any_role(1087746207511757002)
    async def _gl_init(self, ctx):
        channel = await ctx.guild.fetch_channel(1139158245391474800)

        # Embeds in #giới-thiệu-Cộng đồng

        embed1 = discord.Embed(
            title = "📖 Câu chuyện khởi nguồn",
            description = STARTING_STORY_MSG,
            color = discord.Color.red()
        )
        embed1.set_thumbnail(
            url = ctx.guild.icon.url
        )
        await channel.purge(limit = 10)
        msg1 = await channel.send(embed = embed1)

        embed2 = discord.Embed(
            title = "😇 Sứ mệnh của Cộng đồng",
            description = Community_MISSION_MSG,
            color = discord.Color.blue()
        )
        msg2 = await channel.send(embed = embed2)

        embed3 = discord.Embed(
            title = "🏃 Các hoạt động trong Cộng đồng",
            description = Community_ACTIVITIES_MSG,
            color = discord.Color.gold()
        )
        msg3 = await channel.send(embed = embed3)

        embed4 = discord.Embed(
            title = "Đội ngũ 🌟 CORE TEAM 🌟",
            description = "",
            color = discord.Color.green()
        )
        embed4.set_image(
            url = "https://lh3.googleusercontent.com/u/0/drive-viewer/AITFw-x30PDepeeoRJF6Vhdk0Magq_4rWKcJbRA6ZRKcNugenvmzAFHC8W0fB77aY-1vemIznfn5WH7HMEQ3YEwSCfcM7O9I=w1920-h923"
        )
        msg4 = await channel.send(embed = embed4)
        
        embed5 = discord.Embed(
            title = "Ban Quản Trị (a.k.a. The Presidents)",
            color = discord.Color.green()
        )
        embed5.add_field(
            name = f"Chủ tịch - Tô Tuấn Dũng - CN8-K66",
            value = Community_CORE_TEAM_MSG_1,
            inline = False
        )
        embed5.add_field(
            name = f"Phó chủ tịch - Lê Vũ Minh - CN8-K66",
            value = Community_CORE_TEAM_MSG_2,
            inline = False
        )
        embed5.add_field(
            name = f"Phó chủ tịch - Trần Nam Dân - CN8-K66",
            value = Community_CORE_TEAM_MSG_3,
            inline = False
        )
        msg5 = await channel.send(embed = embed5)
        
        await asyncio.sleep(3)

        embed6 = discord.Embed(
            title = "Ban Chuyên Môn (a.k.a. Community Experts)",
            description = Community_CORE_TEAM_MSG_4,
            color = discord.Color.green()
        )
        embed6.add_field(
            name = f"Trưởng ban",
            value = "Vũ Quý Đạt - <@888055463059537983> - CN8-K66",
            inline = False
        )
        embed6.add_field(
            name = f"Phó ban",
            value = "Tạ Xuân Duy - <@418256822902718465> - CN8-K67",
            inline = False
        )
        embed6.add_field(
            name = f"Thành viên",
            value = f"- Lê Đức Anh - <@691975240414265385> - CN8-K68\n- Nguyễn Đức Huy - <@756870314344054835> - CN8-K68",
            inline = False
        )
        msg6 = await channel.send(embed = embed6)

        embed7 = discord.Embed(
            title = "Ban Truyền Thông (a.k.a. PR & Media)",
            description = Community_CORE_TEAM_MSG_5,
            color = discord.Color.green()
        )
        embed7.add_field(
            name = f"Trưởng ban",
            value = "Nguyễn Duy Chiến - <@633872635411038209> - CN8-K66",
            inline = False
        )
        embed7.add_field(
            name = f"Thành viên",
            value = f"- Bồ Quốc Trung - <@556463088983998505> - CN8-K67\n- Trần Gia Khánh - <@702776466265342022> - CN8-K68",
            inline = False
        )
        embed7.set_image(
            url = "https://scontent.fhan2-4.fna.fbcdn.net/v/t39.30808-6/357709046_3420474118213052_3229237850735346573_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=09cbfe&_nc_ohc=9kapCWj1neEAX-WzdJb&_nc_ht=scontent.fhan2-4.fna&oh=00_AfBdBzpVMClFSk6RgQ45mqHVNoQtWIVwhvETvZmobPV5_w&oe=64E3E97B"
        )
        msg7 = await channel.send(embed = embed7)

        embed8 = discord.Embed(
            title = "Ban Tự Động Hoá (a.k.a. Bot Developers)",
            description = Community_CORE_TEAM_MSG_6,
            color = discord.Color.green()
        )
        embed8.add_field(
            name = f"Trưởng ban",
            value = "Lê Anh Duy - <@535811480629542921> - CN8-K68",
            inline = False
        )
        embed8.add_field(
            name = f"Thành viên",
            value = f"Vũ Việt Khánh - <@519418640358047745> - CN8-K66\nPhùng Minh Tuấn Anh - <@699897753802637415> - CN8-K67",
            inline = False
        )
        embed8.set_image(
            url = "https://hackmd.io/_uploads/Sy19Ru3h2.png"
        )
        msg8 = await channel.send(embed = embed8)
        
        NAVIGATION_MSG = ""
        NAVIGATION_MSG += f"1. [Câu chuyện khởi nguồn]({msg1.jump_url})\n"
        NAVIGATION_MSG += f"2. [Sứ mệnh của Cộng đồng]({msg2.jump_url})\n"
        NAVIGATION_MSG += f"3. [Các hoạt động trong Cộng đồng]({msg3.jump_url})\n"
        NAVIGATION_MSG += f"4. [Đội ngũ Core Team]({msg4.jump_url})\n"
        NAVIGATION_MSG += f" - [Ban Quản Trị]({msg5.jump_url})\n"
        NAVIGATION_MSG += f" - [Ban Chuyên Môn]({msg6.jump_url})\n"
        NAVIGATION_MSG += f" - [Ban Truyền Thông]({msg7.jump_url})\n"
        NAVIGATION_MSG += f" - [Ban Tự Động Hoá]({msg8.jump_url})\n"
        embed9 = discord.Embed(
            title = "Mục lục",
            description = NAVIGATION_MSG,
            color = discord.Color.greyple()
        )
        embed9.set_footer(
            text = "Ấn vào link để nhảy đến content tương ứng"
        )
        await channel.send(embed = embed9)
        await asyncio.sleep(3)

        # Embeds in #hướng-dẫn-verify
        channel = await ctx.guild.fetch_channel(1139158370926993499)
        embed1 = discord.Embed(
            title = "📜 Hướng dẫn verify",
            description = HOW_TO_VERIFY_MSG_1,
            color = discord.Color.gold()
        )

        embed2 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_2,
            color = 0xcdb4db
        )
        embed2.set_author(
            name = "Bước 1"
        )
        embed2.set_image(
            url = "https://media.discordapp.net/attachments/1092451759890374747/1092452461748424784/image.png"
        )

        embed3 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_3,
            color = 0xffc8dd
        )
        embed3.set_author(
            name = "Bước 2"
        )
        embed3.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092453040465903616/image.png"
        )

        embed4 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_4,
            color = 0xffafcc,
        )
        embed4.set_author(
            name = "Bước 3"
        )
        embed4.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092453850121777243/image.png"
        )

        embed5 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_5,
            color = 0xbde0fe
        )
        embed5.set_author(
            name = "Bước 4"
        )
        embed5.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092454978926419988/image.png"
        )
        
        embed6 = discord.Embed(
            description = HOW_TO_VERIFY_MSG_6,
            color = 0xa2d2ff
        )
        embed6.set_author(
            name = "Bước 5"
        )
        embed6.set_image(
            url = "https://cdn.discordapp.com/attachments/1092451759890374747/1092455415150809158/image.png"
        )
        
        await channel.purge(limit = 5)
        await channel.send(embeds = [embed1, embed2, embed3, embed4, embed5, embed6])
        await ctx.send(f"{Assets.green_tick} **All embeds sent**")

    
async def setup(client):
    await client.add_cog(gl(client), guilds=[discord.Object(id=client.config['serverId'])])
    #await client.add_cog(gl(client))
