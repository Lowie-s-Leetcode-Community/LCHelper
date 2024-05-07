import discord
from utils.asset import Assets

color_list = [Assets.easy, Assets.medium, Assets.hard]
medal_list = ["🥇", "🥈", "🥉"]

class LeaderboardEmbedNoInteraction(discord.Embed):
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
        
    # The Embed description content
    def format_display_string(self, user, idx):
        rank_idx = medal_list[idx - 1] if idx <= len(medal_list) else f"``#{idx}.``"
        discord_username = self.get_discord_username(user['discordId'])
        leetcode_url = f"https://leetcode.com/{user['leetcodeUsername']}"
        return f"{rank_idx} [``{user['leetcodeUsername']}``]({leetcode_url} '{discord_username}'): {user['scoreEarned']}\n"
    
    def get_ranking_response(self):
        response = ""
        for idx in range(1,11):
            if idx <= len(self.user_list):
                user = self.user_list[idx - 1]
                response += self.format_display_string(user, idx)
        return response
    
    def get_ranking_embed(self):
        response = self.get_ranking_response()
        self.description = response  
        self.set_thumbnail(
            url = self.guild.icon.url
        )
        return self
