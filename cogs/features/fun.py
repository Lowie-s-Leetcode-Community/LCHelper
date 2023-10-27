import discord
from discord import app_commands
from discord.ext import commands
from ..logging.logging import logging
import random


class fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    global bonus

    @app_commands.command(name="gacha", description="Random bonus point")
    async def _gacha(self, interaction: discord.Interaction):
        avatar_url = interaction.user.guild_avatar.url if interaction.user.guild_avatar else interaction.user.display_avatar.url
        await interaction.response.defer(thinking=True)
        lc_user = self.client.DBClient['LC_db']['LC_users'].find_one({'discord_id': interaction.user.id})
        lc_col = self.client.DBClient['LC_db']['LC_users']
        lc_gacha = lc_user['daily_task']['gacha']
        lc_daily_finished = lc_user['daily_task']['finished_today_daily']
        guild = self.client.get_guild(interaction.guild_id)
        member = guild.get_member(lc_user['discord_id'])
        if lc_daily_finished and lc_gacha is False:
            global bonus
            bonus = random.randint(0, 3)
            lc_user['current_month']['score'] += bonus
            lc_user['all_time']['score'] += bonus
            lc_query = {'$set': lc_user}
            lc_col.update_one({'discord_id': member.id}, lc_query)
            embed = discord.Embed(
                title="Gacha",
                description=f"You got {bonus} {'points' if bonus > 1 else 'point'} !",
                color=0x03cffc,
                timestamp=interaction.created_at
            )
        elif lc_daily_finished and lc_gacha is True:
            embed = discord.Embed(
                title="Gacha",
                description=f"You already got your bonus point today!",
                color=0x03cffc,
                timestamp=interaction.created_at
            )
        else:
            embed = discord.Embed(
                title="Gacha",
                description=f"You got to finish daily Leetcode first!",
                color=0x03cffc,
                timestamp=interaction.created_at
            )
        embed.set_author(
            name="Gacha",
            icon_url=self.client.user.display_avatar.url
        )
        embed.set_footer(
            text=interaction.user.display_name,
            icon_url=avatar_url
        )
        await interaction.followup.send(embed=embed)
        if lc_daily_finished:
            await logging.on_score_add(logging(self.client), member=member, score=bonus, reason='Gacha!')

    @app_commands.command(name="trivia", description="Answer a random and awesome question")
    @app_commands.choices(
        difficulty=[
            app_commands.Choice(name="Medium", value="Medium"),
            app_commands.Choice(name="Hard", value="Hard"),
        ]
    )
    async def _trivia(
            self,
            interaction: discord.Interaction,
            difficulty: app_commands.Choice[str] = None,
    ):
        difficulty_value = difficulty.value if difficulty else 'Medium'
        await interaction.response.defer(thinking=True)
        quiz = get_question(difficulty_value, self.client.DBClient)
        print(quiz)
        view = Menu(quiz['correct_answer'])
        embed = make_embed_quiz(quiz)
        await interaction.followup.send(
            embed=embed,
            view=view
        )


class Menu(discord.ui.View):
    def __init__(self, correct: str):
        super().__init__(timeout=None)
        self.correct = correct
        self.add_item(self.AnsButton(style=discord.ButtonStyle.blurple, label='A', custom_id='A', correct=correct))
        self.add_item(self.AnsButton(style=discord.ButtonStyle.blurple, label='B', custom_id='B', correct=correct))
        self.add_item(self.AnsButton(style=discord.ButtonStyle.blurple, label='C', custom_id='C', correct=correct))
        self.add_item(self.AnsButton(style=discord.ButtonStyle.blurple, label='D', custom_id='D', correct=correct))

        # print(self.correct[0])

    async def callback(self, interaction: discord.Interaction):
        if interaction.custom_id == self.correct[0]:
            await interaction.response.send_message('Correct', ephemeral=True)
        else:
            await interaction.response.send_message('Wrong', ephemeral=True)

    # async def interaction_check(self, interaction: discord.Interaction):
    #     if interaction.user != self.view.message.author:
    #         await interaction.response.send_message("You cannot interact with this trivia.", ephemeral=True)
    #         return False
    #     return True

    class AnsButton(discord.ui.Button):
        def __init__(self, style: discord.ButtonStyle, label: str, custom_id: str, correct: str):
            super().__init__(style=style, label=label, custom_id=custom_id)
            self.correct = correct

        # async def process_answer(self, button: discord.ui.Button, interaction: discord.Interaction):
        #     print(123)
        #     await interaction.response.defer(thinking=True)
        #     if button.custom_id == self.correct:
        #         content = "Correct!"
        #     else:
        #         content = "Wrong!"
        #     await interaction.followup.send(content)


def get_question(difficulty: str, db):
    lc_quizzes = db['LC_db']['LC_quiz'].find({'difficulty': difficulty})
    lc_quizzes = list(lc_quizzes)
    index = random.randint(0, len(lc_quizzes) - 1)
    return lc_quizzes[index]


def make_embed_quiz(quiz):
    question = quiz['title']
    embed = discord.Embed(
        title="Trivia Question",
        description=question,
        color=0xffc01e if quiz['difficulty'] == 'Medium' else 0xef4743
    )
    options = quiz['options']
    embed.add_field(name="Ans", value=options[0], inline=False)
    embed.add_field(name="Ans", value=options[1], inline=False)
    embed.add_field(name="Ans", value=options[2], inline=False)
    embed.add_field(name="Ans", value=options[3], inline=False)
    embed.add_field(name="Category", value=quiz.get('category'), inline=True)
    embed.add_field(name="Difficulty", value=quiz.get('difficulty'), inline=True)
    return embed


async def setup(client):
    await client.add_cog(fun(client), guilds=[discord.Object(id=1085444549125611530)])
