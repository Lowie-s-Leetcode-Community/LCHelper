import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
import random

GACHA_RESPONSE_LIST = [
  {
    "response": "Bạn bước vào giảng đường ngay lúc giảng viên bắt đầu điểm danh.",
    "score": 1
  },
  {
    "response": "Đề thi [LeetCode Weekly Contest](https://leetcode.com/contest/) trúng dạng bài bạn vừa học.",
    "score": 1
  },
  {
    "response": "Giảng viên thông báo cuối kỳ thi được dùng tài liệu.",
    "score": 1
  },
  {
    "response": "Bạn vừa có chuỗi 5 trận thắng hạng để leo lên Bạch Kim, mặc dù chỉ biết đánh Yasuo...",
    "score": 1
  },
  {
    "response": "Bạn biết rằng thi thoảng chúng mình có hội Boardgame không? Theo dõi <#1085446365699649536> thường xuyên nhé! :eyes:",
    "score": 1
  },
  {
    "response": "Bạn quá đẹp trai... hoặc xinh gái (các bạn tuyển thêm nữ cho cộng đồng đi hicc :smiling_face_with_tear: ).",
    "score": 1
  },
  {
    "response": "Bạn đi thi kết thúc học phần và trúng tủ.",
    "score": 2
  },
  {
    "response": "Nhắn :beer: lên <#1085444549666680906> để rủ anh Lowie và HaruKatou đi uống bia nhé.",
    "score": 2
  },
  {
    "response": "Bạn quay gacha trên Honkai: Star Rail và roll trúng \{điền tên waifu của bạn vào đây\}!",
    "score": 2
  },
  {
    "response": "Bạn bắt kèo dưới Costa Rica thắng Nhật Bản để x7 lợi nhuận, và thành lập cả cộng đồng chỉ để gáy với họ về điều đó.",
    "score": 3
  },
  # {
  #   "response": "Bạn chơi Pokemon:GO và bắt được MewTwo.",
  #   "score": 3
  # },
]

class Gacha(commands.Cog):
  def __init__(self, client):
    self.client = client

  @app_commands.command(name="gacha", description="Thử thách độ :turtle: của bạn sau khi hoàn thành nhiệm vụ!")
  async def _gacha(self, interaction: discord.Interaction):
    avatar_url = interaction.user.guild_avatar.url if interaction.user.guild_avatar else interaction.user.display_avatar.url

    await interaction.response.defer(thinking=True)
    user_progress = self.client.db_api.read_user_progress(str(interaction.user.id))
    score_earned = user_progress['user_daily']['scoreEarned']
    score_gacha = user_progress['user_daily']['scoreGacha']
    if score_earned < 2:
      embed = discord.Embed(
        description="Bạn chưa hoàn thành nhiệm vụ ngày hôm nay. Hãy đọc </tasks:1107228520679231488> của bạn và ghi ít nhất 2 điểm ngày nhé!",
        color=Assets.hard,
        timestamp=interaction.created_at
      )
      embed.set_author(
        name=f"Kết quả quay Gacha: Chưa hoàn thành nhiệm vụ!",
        icon_url=self.client.user.display_avatar.url
      )
    elif score_gacha > 0:
      embed = discord.Embed(
        description="Bạn đã quay gacha cho ngày hôm nay rồi. Hãy quay trở lại ngày mai nhé^^",
        color=Assets.medium,
        timestamp=interaction.created_at
      )
      embed.set_author(
        name=f"Kết quả quay Gacha! Hẹn mai nhé :)",
        icon_url=self.client.user.display_avatar.url
      )
    else:
      roll = random.choice(GACHA_RESPONSE_LIST)
      result = await self.client.db_api.update_gacha_score(str(interaction.user.id), roll['score'])
      if result['status'] == False:
        await interaction.followup.send("There was a problem in processing your roll. Please try again later!")
        return
      
      embed = discord.Embed(
        description=roll['response'],
        color=Assets.easy,
        timestamp=interaction.created_at
      )
      embed.set_author(
        name=f"Kết quả quay Gacha: Cộng {roll['score']} điểm!",
        icon_url=self.client.user.display_avatar.url
      )

    embed.set_footer(
      text=interaction.user.display_name,
      icon_url=avatar_url
    )

    await interaction.followup.send(embed=embed)
 
async def setup(client):
  await client.add_cog(Gacha(client), guilds=[discord.Object(id=client.config['serverId'])])
