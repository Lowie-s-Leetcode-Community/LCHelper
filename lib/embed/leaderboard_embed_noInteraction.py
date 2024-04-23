import discord
from utils.asset import Assets

color_list = [Assets.easy, Assets.medium, Assets.hard]
medal_list = ["🥇", "🥈", "🥉"]

class LeaderboardEmbed(discord.Embed):
    def __init__(self, title: str, user_list: list, guild: discord.guild):
        super().__init__(
            title=title,
            color=color_list[0]
        )
        self.user_list = user_list
        self.guild = guild
        self.get_ranking_embed()

    def get_discord_username(self, discord_id: str):
        member = discord.utils.find(lambda m: str(m.id) == discord_id, self.guild.members)
        if member:
            return member.name
        else:
            return None

    def get_ranking_embed(self):
        def format_display_string(user, idx):
            rank_idx = medal_list[idx - 1] if idx <= len(medal_list) else f"``{idx}.``"
            discord_username = self.get_discord_username(user['discordId'])
            leetcode_url = f"https://leetcode.com/{user['leetcodeUsername']}"
            return f"{rank_idx} [``{user['leetcodeUsername']}``]({leetcode_url} '{discord_username}'): {user['scoreEarned']}\n"
        
        response = ""
        for idx in range(1,11):
            if idx <= len(self.user_list):
                user = self.user_list[idx - 1]
                response += format_display_string(user, idx)

        self.description = response  
        self.set_thumbnail(
            url = self.guild.icon.url
        )
        return self
    
class RankingView(discord.ui.View):
    def __init__(self, title: str, user_list: list):
        super().__init__(timeout = 120)
        self.title = title
        self.user_list = user_list
        self.response = None