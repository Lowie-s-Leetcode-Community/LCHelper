import discord
from discord import app_commands
from discord.ext import tasks, commands

class poll(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name='poll',
                          description="create polls up to 20 options")
    async def polling(self,
                      interaction: discord.Interaction,
                      question: str,
                      args1: str = None,
                      args2: str = None,
                      args3: str = None,
                      args4: str = None,
                      args5: str = None,
                      args6: str = None,
                      args7: str = None,
                      args8: str = None,
                      args9: str = None,
                      args10: str = None,
                      args11: str = None,
                      args12: str = None,
                      args13: str = None,
                      args14: str = None,
                      args15: str = None,
                      args16: str = None,
                      args17: str = None,
                      args18: str = None,
                      args19: str = None,
                      args20: str = None,
                      ):
        await interaction.response.defer(thinking = True)
        # lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        # message = "test poll"
        embed = discord.Embed(
            title = "Poll: " + question,
            description = "Here are the options:",
            color = discord.Colour.blue()
            )
        args = [args1, args2, args3, args4, args5, args6, args7, args8, args9, args10, args11, args12, args13, args14, args15, args16, args17, args18, args19, args20]
        emojis = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹"]
        cnt = 0
        for i in range(20):
            if args[i] != None :
                cnt += 1
                embed.add_field(
                    value = emojis[i] + ": " + args[i]
                    inline = False
                )
        await interaction.followup.send(message)
        original_mes = await interaction.original_response()
        for i in range(20):
            if args[i] != None :
                await original_mes.add_reaction(emojis[i])
        if cnt == 0 :
            await original_mes.add_reaction("👍")
            await original_mes.add_reaction("👎")

async def setup(client):
    await client.add_cog(poll(client), guilds=[discord.Object(id=1085444549125611530)])
