import discord
import os
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
from utils.asset import Assets

TOPIC_TAG_LIST = ['Array', 'Backtracking', 'Biconnected Component', 'Binary Indexed Tree', 'Binary Search', 'Binary Search Tree', 'Binary Tree', 'Bit Manipulation', 'Bitmask', 'Brainteaser', 'Breadth-First Search', 'Bucket Sort', 'Combinatorics', 'Concurrency', 'Counting', 'Counting Sort', 'Data Stream', 'Database', 'Depth-First Search', 'Design', 'Divide and Conquer', 'Doubly-Linked List', 'Dynamic Programming', 'Enumeration', 'Eulerian Circuit', 'Game Theory', 'Geometry', 'Graph', 'Greedy', 'Hash Function', 'Hash Table', 'Heap (Priority Queue)', 'Interactive', 'Iterator', 'Line Sweep', 'Linked List', 'Math', 'Matrix', 'Memoization', 'Merge Sort', 'Minimum Spanning Tree', 'Monotonic Queue', 'Monotonic Stack', 'Number Theory', 'Ordered Set', 'Prefix Sum', 'Probability and Statistics', 'Queue', 'Quickselect', 'Radix Sort', 'Randomized', 'Recursion', 'Rejection Sampling', 'Reservoir Sampling', 'Rolling Hash', 'Segment Tree', 'Shell', 'Shortest Path', 'Simulation', 'Sliding Window', 'Sorting', 'Stack', 'String', 'String Matching', 'Strongly Connected Component', 'Suffix Array', 'Topological Sort', 'Tree', 'Trie', 'Two Pointers', 'Union Find']
    
class config(commands.Cog):
    def __init__(self, client):
        self.client = client

    config_group = app_commands.Group(name = "settings", description = "LLC settings system")
    config_set_group = app_commands.Group(parent = config_group, name = "set", description = "Change settings")
    @config_group.command(name = 'view', description = "View the current LLC's settings")
    @app_commands.checks.has_role(1085445066484621362)
    async def _settings(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        lc_config = self.client.DBClient['LC_db']['LC_config'].find_one({})
        
        embed = discord.Embed(
            title = "Current config for LLC",
            color = discord.Colour.red()
        )
        embed.add_field(
            name = "Events",
            value = f"""
            `event_multiplier_topic_bonus`: {lc_config['event_multiplier_topic_bonus']}x
            `event_multiplier_topic_list`: {', '.join(lc_config['event_multiplier_topic_list'])}
            `event_multiplier_topic_start`: <t:{lc_config['event_multiplier_topic_start']}:f> - <t:{lc_config['event_multiplier_topic_start']}:R>
            `event_multiplier_topic_end`: <t:{lc_config['event_multiplier_topic_end']}:f> - <t:{lc_config['event_multiplier_topic_end']}:R>
            """
        )
        await interaction.followup.send(embed = embed)
    
    @config_set_group.command(name = 'event_multiplier_topic_bonus', description = "Change the multiplier of the topic event")
    @app_commands.checks.has_role(1085445066484621362)
    @app_commands.describe(value = "New multiplier bonus")
    async def _set_multiplier_topic_bonus(self, interaction: discord.Interaction, value: float):
        await interaction.response.defer(thinking = True)
        lc_config = self.client.DBClient['LC_db']['LC_config']
        lc_config.update_one({}, {'$set': {
            'event_multiplier_topic_bonus': value,      
        }})
        await interaction.followup.send(f"{Assets.green_tick} **Setting updated.**")
    
    @config_set_group.command(name = 'event_multiplier_topic_list', description = "Change the problem topics to apply multiplier")
    @app_commands.checks.has_role(1085445066484621362)
    @app_commands.describe(topic1 = "New topic #1")
    @app_commands.describe(topic2 = "New topic #2")
    @app_commands.describe(topic3 = "New topic #3")
    async def _set_multiplier_topic_list(
        self, 
        interaction: discord.Interaction, 
        topic1: Optional[str] = None,
        topic2: Optional[str] = None,
        topic3: Optional[str] = None
    ):
        topic_list = []
        if topic1: topic_list.append(topic1)
        if topic2: topic_list.append(topic2)
        if topic3: topic_list.append(topic3)

        await interaction.response.defer(thinking = True)
        lc_config = self.client.DBClient['LC_db']['LC_config']
        lc_config.update_one({}, {'$set': {
            'event_multiplier_topic_list': topic_list,      
        }})
        await interaction.followup.send(f"{Assets.green_tick} **Setting updated.**")
    
    @_set_multiplier_topic_list.autocomplete('topic1')
    @_set_multiplier_topic_list.autocomplete('topic2')
    @_set_multiplier_topic_list.autocomplete('topic3')
    async def _gimme_autocomplete(self, interaction: discord.Interaction, current: str):
        tags = TOPIC_TAG_LIST
        return [
            app_commands.Choice(name = tag, value = tag)
            for tag in tags if current.lower() in tag.lower()
        ][:25]
        
    
    @config_set_group.command(name = 'event_multiplier_topic_start', description = "Change the timestamp when the event should start")
    @app_commands.describe(value = "New timestamp")
    async def _set_multiplier_topic_start(self, interaction: discord.Interaction, value: int):
        await interaction.response.defer(thinking = True)
        lc_config = self.client.DBClient['LC_db']['LC_config']
        lc_config.update_one({}, {'$set': {
            'event_multiplier_topic_start': value,      
        }})
        await interaction.followup.send(f"{Assets.green_tick} **Setting updated.**")
    
    @config_set_group.command(name = 'event_multiplier_topic_end', description = "Change the timestamp when the event should end")
    @app_commands.describe(value = "New timestamp")
    async def _set_multiplier_topic_end(self, interaction: discord.Interaction, value: int):
        await interaction.response.defer(thinking = True)
        lc_config = self.client.DBClient['LC_db']['LC_config']
        lc_config.update_one({}, {'$set': {
            'event_multiplier_topic_end': value,      
        }})
        await interaction.followup.send(f"{Assets.green_tick} **Setting updated.**")
    
async def setup(client):
    await client.add_cog(config(client), guilds=[discord.Object(id=1085444549125611530)])
