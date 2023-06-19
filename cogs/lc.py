import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional, Union
import random
import string
import asyncio
import datetime

class TestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 30)

    @discord.ui.button(label = "Click click", style = discord.ButtonStyle.secondary, emoji = "👀")
    async def call_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the thing")
    
class ConfirmView(discord.ui.View):
    def __init__(self, client, code, username, user_id):
        super().__init__(timeout = 60)
        self.code = code
        self.client = client
        self.username = username
        self.user_id = user_id
        self.response = None
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            child.label = "Timeout!"
            child.emoji = "⏰"
        await self.response.edit(view = self)


    @discord.ui.button(label = "Verify Me!", style = discord.ButtonStyle.primary)
    async def call_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.user.id == self.user_id
        await interaction.response.defer(thinking = True)
        user_info = LC_utils.get_user_profile(self.username)
        if len(user_info['profile']['summary']) >= 5 and user_info['profile']['summary'][0:5] == self.code:
            lc_db = self.client.DBClient['LC_db']
            lc_col = lc_db['LC_users']
            lc_query = {'discord_id': interaction.user.id}
            lc_result = lc_col.find_one(lc_query)
            if lc_result:
                lc_update = {'$set': {'lc_username': self.username}}
                lc_col.update_one(lc_query, lc_update)
            else:
                lc_col.insert_one({'discord_id': interaction.user.id, 'lc_username': self.username})

            # Also updating the necessary info
            recent_info = LC_utils.get_recent_ac(self.username, 20)
            tmp_query = {
                'all_time': {
                    'max_daily_streak': 0,
                    'current_daily_streak': 0,
                    'score': 0
                },
                'current_month': {
                    'max_daily_streak': 0,
                    'current_daily_streak': 0,
                    'score': 0
                },
                'previous_month': {
                    'max_daily_streak': 0,
                    'current_daily_streak': 0,
                    'score': 0
                },
                'daily_task': {
                    'finished_today_daily': False,
                    'scores_earned_excluding_daily': 0,
                    'easy_solved': 0,
                    'medium_solved': 0,
                    'hard_solved': 0
                },
                'solved': []
            }
            if len(recent_info) == 0:
                tmp_query['recent_ac'] = {
                    "id": None,
                    "title": None,
                    "titleSlug": None,
                    "timestamp": str(int(datetime.datetime.timestamp(datetime.datetime.now())))
                }
            else: tmp_query['recent_ac'] = recent_info[0]
        
            lc_update = {'$set': tmp_query}
            lc_col.update_one(lc_query, lc_update)
            
            try:
                lc_query = {'server_id': interaction.guild_id}
                lc_result = lc_db['LC_tracking'].find_one(lc_query)
                role_id = lc_result['verified_role_id']
                member = await interaction.guild.fetch_member(interaction.user.id)
                role = discord.utils.get(interaction.guild.roles, id = role_id)
                await member.add_roles(role)
            except:
                pass

            await interaction.followup.send(content = f"{Assets.green_tick} **Account linked successfully.**")

        else: await interaction.followup.send(content = f"{Assets.red_tick} **Unmatched code. Please try again.**")

        
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        await interaction.followup.send(error)
        
class lc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'link', description = "Links your Discord with a LeetCode account")
    @app_commands.describe(username = "Specify a username")
    async def _link(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking = True)
        user_info = LC_utils.get_user_profile(username)
        if user_info:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 5))   
            view = ConfirmView(code = code, username = username, user_id = interaction.user.id, client = self.client)
            await interaction.followup.send(f"**Please paste this code `{code}` at the start of your [profile summary](https://leetcode.com/profile/).**", view = view)
            view.response = await interaction.original_response()
        else:
            await interaction.followup.send(f"{Assets.red_tick} **Username doesn't exist, please double check.**")
            

    @app_commands.command(name = 'daily', description = "Returns Leetcode's Daily Challenge")
    async def _daily(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        
        # Getting the daily challenge

        # daily_info = LC_utils.get_daily_challenge_info()
        daily_info = self.client.DBClient['LC_db']['LC_daily'].find_one()['daily_challenge']
        info = LC_utils.get_problem_info(daily_info['title_slug'])

        embed = discord.Embed(
            title = f"**{info['title']}**",
            url = f"{info['link']}",
            color = Assets.easy if info['difficulty'] == 'Easy' else Assets.medium if info['difficulty'] == 'Medium' else Assets.hard
        )
        embed.add_field(
            name = "Difficulty",
            value = info['difficulty'],
            inline = True
        )
        embed.add_field(
            name = "AC Count", 
            value = f"{info['total_AC']}/{info['total_submissions']}",
            inline = True,
        )
        embed.add_field(
            name = "AC Rate",
            value = str(info['ac_rate'])[0:5] + "%",
            inline = True,
        )
        tag_list = ""
        for name, link in info['topics'].items():
            tag_list += f"[``{name}``]({link}), "
        
        tag_list = tag_list[:-2]
        tag_list = "||" + tag_list + "||"
        embed.add_field(
            name = "Topics",
            value = tag_list,
            inline = False
        )
        embed.set_footer(
            text = f"{info['likes']} 👍 • {info['dislikes']} 👎"
        )

        await interaction.followup.send(f"Daily Challenge - {daily_info['date']}", embed = embed)

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
                name = "🏡 In-server (beta)",
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
    async def _verify(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(thinking = True)

        lc_db = self.client.DBClient['LC_db']
        lc_col = lc_db['LC_tracking']
        lc_query = {'server_id': interaction.guild_id}
        lc_result = lc_col.find_one(lc_query)
        if lc_result:
            lc_update = {'$set': {'verified_role_id': role.id}}
            lc_col.update_one(lc_query, lc_update)
        else:
            lc_col.insert_one({'server_id': interaction.guild_id, 'verified_role_id': role.id})
        await interaction.followup.send(f"{Assets.green_tick} **Verified role has been set to {role.mention}**")

    @app_commands.command(name = 'test')
    async def _test(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        await interaction.followup.send("owo", view = TestView())

    ranklist = app_commands.Group(name = 'ranklist', description = 'Ranking of all kinds')
    @ranklist.command(name = 'streak', description = "Views the daily streak ranking")
    async def _ranklist_streak(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        lc_col = self.client.DBClient['LC_db']['LC_users']
        users = list(lc_col.find())
        users.sort(key = lambda x: -x['current_month']['max_daily_streak'])
        response = ""
        idx = 1
        for user in users:
            if user['current_month']['max_daily_streak'] > 0:
                response += f"`#{idx}` {user['lc_username']}/<@{user['discord_id']}> - Max: {user['current_month']['max_daily_streak']} - Current: {user['current_month']['current_daily_streak']}\n"
                idx += 1
        embed = discord.Embed(
            title = "Daily streak ranking",
            description = response
        )
        await interaction.followup.send(embed = embed)

    @ranklist.command(name = 'score', description = "Views the score ranking of this month")
    async def _ranklist_score(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        lc_col = self.client.DBClient['LC_db']['LC_users']
        users = list(lc_col.find())
        users.sort(key = lambda x: -x['current_month']['score'])
        response = ""
        idx = 1
        for user in users:
            if user['current_month']['score'] > 0:
                response += f"`#{idx}` {user['lc_username']}/<@{user['discord_id']}> - Score: {user['current_month']['score']}\n"
                idx += 1
        embed = discord.Embed(
            title = "Current month's score ranking",
            description = response
        )
        await interaction.followup.send(embed = embed)
    
    @ranklist.command(name = 'prev_month_score', description = "Views the score ranking of previous month")
    async def _ranklist_prevscore(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        lc_col = self.client.DBClient['LC_db']['LC_users']
        users = list(lc_col.find())
        users.sort(key = lambda x: -x['previous_month']['score'])
        response = ""
        idx = 1
        for user in users:
            if user['previous_month']['score'] > 0:
                response += f"`#{idx}` {user['lc_username']}/<@{user['discord_id']}> - Score: {user['previous_month']['score']}\n"
                idx += 1
        embed = discord.Embed(
            title = "Previous month's score ranking",
            description = response
        )
        await interaction.followup.send(embed = embed)

async def setup(client):
    await client.add_cog(lc(client), guilds=[discord.Object(id=1085444549125611530)])
    #await client.add_cog(lc(client))
