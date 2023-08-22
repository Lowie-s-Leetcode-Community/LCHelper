import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional
      
class lc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'profile', description = "Returns a Leetcode profile")
    @app_commands.describe(username = "Specify a username. Left empty if you want to check yours")
    @app_commands.describe(member = "Specify a member. Left empty if you want to check yours")
    async def _profile(self, interaction: discord.Interaction, username: Optional[str] = None, member: Optional[discord.Member] = None):
        await interaction.response.defer(thinking = True)

        lc_col = self.client.DBClient['LC_db']['LC_users']
        lc_result = None
        if username == None and member == None:
            lc_query = {'discord_id': interaction.user.id}
            lc_result = lc_col.find_one(lc_query)
            if not lc_result:
                await interaction.followup.send(f"{Assets.red_tick} **Please specify an username, a member, or link your account with `/link`**")
                return
            else: username = lc_result['lc_username']
        elif username and member:
            await interaction.followup.send(f"{Assets.red_tick} **Choose either not both :woozy_face:**")
            return
        elif member:
            lc_query = {'discord_id': member.id}
            lc_result = lc_col.find_one(lc_query)
            if not lc_result:
                await interaction.followup.send(f"{Assets.red_tick} **This member hasn't linked an account yet**")
                return
            else: username = lc_result['lc_username']
        else:
            lc_query = {'lc_username': username}
            lc_result = lc_col.find_one(lc_query)
        
        info = LC_utils.get_user_profile(username)
        embed = discord.Embed(
            description = f"""
            ▸ **Name:** {info['profile']['name'] if info['profile']['name'] != "" else "N/A"}
            ▸ **Location:** {info['profile']['country']}
            ▸ **Total active days:** {info['calendar']['total_active_days']}
            ▸ **Max active days streak:** {info['calendar']['streak']}
            """,
            color = 0xffffff
        )
        embed.add_field(
            name = "📝 Problems",
            value = f"""
            ▸ **Rank:** #{info['profile']['rank'] if info['profile']['rank'] != "" else "N/A"}
            ▸ **Solved:** {info['problem']['solved']['all']}/{info['problem']['total_problem']['all']} ({info['problem']['percentage']['all']}%)
            {Assets.blank} ▸ **Easy:** {info['problem']['solved']['easy']}/{info['problem']['total_problem']['easy']} ({info['problem']['percentage']['easy']}%)
            {Assets.blank} ▸ **Medium:** {info['problem']['solved']['medium']}/{info['problem']['total_problem']['medium']} ({info['problem']['percentage']['medium']}%)
            {Assets.blank} ▸ **Hard:** {info['problem']['solved']['hard']}/{info['problem']['total_problem']['hard']} ({info['problem']['percentage']['hard']}%)
            """,
            inline = True
            # Special space characters
        )
        embed.add_field(
            name = "📊 Contests",
            value = f"""
            ▸ **Rank:** {'#' + str(info['contest']['global_rank']) if info['contest']['global_rank'] else "N/A"}
            ▸ **Rating:** {info['contest']['rating'] if info['contest']['rating'] else "N/A"}
            ▸ **Top:** {str(info['contest']['top_percentage']) + '%' if info['contest']['top_percentage'] else "N/A"}
            ▸ **Attended contest:** {info['contest']['contest_count'] if info['contest']['contest_count'] else 0}
            """,
            inline = True
        )
        if lc_result:   
            embed.add_field(
                name = "🏡 In-server",
                value = f"""
                ▸ **All-time**:
                {Assets.blank} ▸ **Max daily streak:** {lc_result['all_time']['max_daily_streak']}
                {Assets.blank} ▸ **Current daily streak:** {lc_result['all_time']['current_daily_streak']}
                {Assets.blank} ▸ **Score:** {lc_result['all_time']['score']}

                ▸ **Current month**:
                {Assets.blank} ▸ **Max daily streak:** {lc_result['current_month']['max_daily_streak']}
                {Assets.blank} ▸ **Current daily streak:** {lc_result['current_month']['current_daily_streak']}
                {Assets.blank} ▸ **Score:** {lc_result['current_month']['score']}
                """,
                inline = False
            )
        embed.set_author(
            name = f"LeetCode profile for {username}",
            icon_url = "https://assets.leetcode.com/users/leetcode/avatar_1568224780.png",
            url = info['profile']['link']
        )
        embed.set_thumbnail(
            url = info['profile']['avatar']
        )
        await interaction.followup.send(embed = embed)

    @app_commands.command(name = 'verify', description = "Sets a role for verified members")
    @app_commands.describe(role = "Choose a role")
    @app_commands.checks.has_permissions(administrator = True)
    async def _verify(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_config']
        lc_query = {}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'verified_role_id': role.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'verified_role_id': role.id})
        await interaction.followup.send(f"{Assets.green_tick} **Verified role has been set to {role.mention}**")

    @app_commands.command(name = 'serverstats', description = "Server statistics fof LLC")
    @app_commands.checks.has_permissions(administrator = True)
    async def _serverstats(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_users']
        embed = discord.Embed(
            title = "Server stats",
            color = discord.Color.blue()
        )
        embed.add_field(
            name = "Total members", 
            value = f"{interaction.guild.member_count}"
        )
        role = discord.utils.find(lambda m: m.id == 1087761988068855890, interaction.guild.roles)
        embed.add_field(
            name = "Verified members",
            value = len(role.members)
        )
        lc_member = list(lc_col.find())
        active_member_count = 0
        for member in lc_member:
            if member['current_month']['score'] > 0: active_member_count += 1
        
        embed.add_field(
            name = "Active members",
            value = f"{active_member_count}"
        )
    
        await interaction.followup.send(embed = embed)

async def setup(client):
    await client.add_cog(lc(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(lc(client))
