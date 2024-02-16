import discord
from discord import app_commands
from discord.ext import commands
from utils.asset import Assets
from utils.lc_utils import LC_utils
from typing import Optional
import random

TOPIC_TAG_LIST = ['Array', 'Backtracking', 'Biconnected Component', 'Binary Indexed Tree', 'Binary Search', 'Binary Search Tree', 'Binary Tree', 'Bit Manipulation', 'Bitmask', 'Brainteaser', 'Breadth-First Search', 'Bucket Sort', 'Combinatorics', 'Concurrency', 'Counting', 'Counting Sort', 'Data Stream', 'Database', 'Depth-First Search', 'Design', 'Divide and Conquer', 'Doubly-Linked List', 'Dynamic Programming', 'Enumeration', 'Eulerian Circuit', 'Game Theory', 'Geometry', 'Graph', 'Greedy', 'Hash Function', 'Hash Table', 'Heap (Priority Queue)', 'Interactive', 'Iterator', 'Line Sweep', 'Linked List', 'Math', 'Matrix', 'Memoization', 'Merge Sort', 'Minimum Spanning Tree', 'Monotonic Queue', 'Monotonic Stack', 'Number Theory', 'Ordered Set', 'Prefix Sum', 'Probability and Statistics', 'Queue', 'Quickselect', 'Radix Sort', 'Randomized', 'Recursion', 'Rejection Sampling', 'Reservoir Sampling', 'Rolling Hash', 'Segment Tree', 'Shell', 'Shortest Path', 'Simulation', 'Sliding Window', 'Sorting', 'Stack', 'String', 'String Matching', 'Strongly Connected Component', 'Suffix Array', 'Topological Sort', 'Tree', 'Trie', 'Two Pointers', 'Union Find']
        
class Gimme(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'gimme', description = "Provides a problem to your likings")
    @app_commands.choices(
        difficulty = [
            app_commands.Choice(name = "Easy", value = "easy"),
            app_commands.Choice(name = "Medium", value = "medium"),
            app_commands.Choice(name = "Hard", value = "hard"),
        ],
        premium = [
            app_commands.Choice(name = 'True', value = 'true'),
            app_commands.Choice(name = 'False', value = 'false'),
            app_commands.Choice(name = 'Any', value = 'any')
        ]
    )
    @app_commands.describe(
        difficulty = 'Choose a diffculty (default: Any)',
        included_tag_1 = 'Choose a topic tag to include',
        included_tag_2 = 'Choose a topic tag to include',
        excluded_tag_1 = 'Choose a topic tag to exclude',
        excluded_tag_2 = 'Choose a topic tag to exclude',
        premium = 'Choose if the problem requires paying (default: False)'
    )
    async def _gimme(
        self, 
        interaction: discord.Interaction, 
        difficulty: app_commands.Choice[str] = None,
        included_tag_1: Optional[str] = None,
        included_tag_2: Optional[str] = None,
        excluded_tag_1: Optional[str] = None,
        excluded_tag_2: Optional[str] = None,
        premium: app_commands.Choice[str] = None
    ):
        await interaction.response.defer(thinking = True)
        lc_query = {}

        # Difficulty
        if difficulty: lc_query['difficulty'] = difficulty.name

        # Tags
        included_tag_list = []
        if included_tag_1: included_tag_list.append(included_tag_1)
        if included_tag_2: included_tag_list.append(included_tag_2)

        excluded_tag_list = []
        if excluded_tag_1: excluded_tag_list.append(excluded_tag_1)
        if excluded_tag_2: excluded_tag_list.append(excluded_tag_2)

        if len(excluded_tag_list) != 0 and len(included_tag_list) != 0:
            lc_query['topics'] = {
                '$all': included_tag_list,
                '$not': {'$all': excluded_tag_list}
            }
        elif len(excluded_tag_list) == 0 and len(included_tag_list) != 0:
            lc_query['topics'] = {
                '$all': included_tag_list,
            }
        elif len(excluded_tag_list) != 0 and len(included_tag_list) == 0:
            lc_query['topics'] = {
                '$not': {'$all': excluded_tag_list}
            }

        # Premium
        if premium and premium.name == "True": lc_query['premium'] = True
        elif premium and premium.name == "False": lc_query['premium'] = False

        # Finds and returns the problem
        lc_result = self.client.db_api.read_gimme(lc_query)
        if len(lc_result) == 0:
            await interaction.followup.send(f"{Assets.red_tick} **No problem matched your query.**")
            return
        gacha_result = random.choice(lc_result)
        info = LC_utils.get_problem_info(gacha_result['titleSlug'])

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
            value = str(info['ac_rate'])[0:2] + "%",
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

        await interaction.followup.send(f"**Problem for {interaction.user.mention}:**", embed = embed)

    @_gimme.autocomplete('included_tag_1')
    @_gimme.autocomplete('included_tag_2')
    @_gimme.autocomplete('excluded_tag_1')
    @_gimme.autocomplete('excluded_tag_2')
    async def _gimme_autocomplete(self, interaction: discord.Interaction, current: str):
        tags = TOPIC_TAG_LIST
        return [
            app_commands.Choice(name = tag, value = tag)
            for tag in tags if current.lower() in tag.lower()
        ][:25]
    
async def setup(client):
    await client.add_cog(Gimme(client), guilds=[discord.Object(id=client.config['serverId'])])
