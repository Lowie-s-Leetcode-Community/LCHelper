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

    def get_discord_username(self, discord_id: str):
        member = discord.utils.find(lambda m: str(m.id) == discord_id, self.guild.members)
        if member:
            return member.name
        return None

    def get_role_emojies(self, user):
        res = ""
        member = discord.utils.find(lambda m: str(m.id) == user['discordId'], self.guild.members)
        for role, emoji in Assets.role_emojies.items():
            m_role = member.get_role(int(role))
            if m_role == None:
                continue
            res += emoji
            break
        return res

    # The Embed description content
    def format_display_string(self, user, idx):
        rank_idx = medal_list[idx - 1] if idx <= len(medal_list) else f"``#{idx}.``"
        discord_username = self.get_discord_username(user['discordId'])
        leetcode_url = f"https://leetcode.com/{user['leetcodeUsername']}"
        return f"{rank_idx} [``{user['leetcodeUsername']}``]({leetcode_url} '{discord_username}') {self.get_role_emojies(user)}: {user['scoreEarned']}\n"

    def get_ranking_response(self):
        response = ""
        # get the first 10 users in the list
        for idx in range(10):
            if idx <= len(self.user_list):
                user = self.user_list[idx]
                response += self.format_display_string(user, idx + 1)
        return response

    def get_ranking_embed(self):
        response = self.get_ranking_response()
        self.description = response  
        self.set_thumbnail(
            url = self.guild.icon.url
        )
        return self
