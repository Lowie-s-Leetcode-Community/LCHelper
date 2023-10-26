import discord
from discord import app_commands
from discord.ext import tasks, commands
import json
from bson import json_util

class backup(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.backup_loop.start()

    def cog_unload(self):
        self.backup_loop.cancel()

    async def get_json_file(self):
        db = self.client.DBClient['LC_db']
        col_list = db.list_collection_names()
        col_list.sort(reverse = True)
        res = {}
        for col in col_list:
            res[col] = []
            query = db[col].find({})
            for doc in list(query):
                res[col].append(doc)

        data = json.loads(json_util.dumps(res))
        with open("backup.json", "w") as f:
            json.dump(data, f, indent = 2)

    @tasks.loop(hours = 1)
    async def backup_loop(self):
        guild = self.client.get_guild(1085444549125611530)
        lc_query = self.client.DBClient['LC_db']['LC_config'].find_one({})
        backup_channel_id = lc_query['backup_channel_id']
        backup_channel = await guild.fetch_channel(backup_channel_id)

        await self.get_json_file()
        
        await backup_channel.send(file = discord.File("backup.json"))

    @backup_loop.before_loop
    async def wait_for_cache(self):
        await self.client.wait_until_ready()

    @app_commands.command(name = "backup", description = "Get a backup JSON file of the current database")
    @app_commands.checks.has_permissions(administrator = True)
    async def _backup(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        await self.get_json_file()
        await interaction.followup.send("**Backup file:**", file = discord.File("backup.json"))


async def setup(client):
    await client.add_cog(backup(client), guilds=[discord.Object(id=1085444549125611530)])
