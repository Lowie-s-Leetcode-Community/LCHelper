from typing import Optional
import typing

import discord
from discord import app_commands
from discord.ext import commands

import random

keyAns = ['A. ', 'B. ', 'C. ', 'D. ', 'E.', 'F.']
iconKey = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫']
TOPIC_TAGS = ['Algorithms', 'Concurrency', 'Distributed Systems','Software Architecture', 'Complexity Theory']


def createEmbed(QandA: list, choice: int = -1):
    question = QandA[0]
    answer = QandA[1]

    correctAnswer = question.correctAnswerId - answer[0].id

    embed = discord.Embed(
        color=0xff822e,
    )
    embed.set_author(
        name="Quiz: ",
        icon_url="https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
    )
    embed.add_field(
        name=question.question,
        value="",
        inline=False
    )

    embed.add_field(
        name="Difficulty",
        value=question.difficulty,
        inline=True
    )

    embed.add_field(
        name="Topic",
        value=f"||{question.category}||",
        inline=True
    )

    if choice == -1:
        answer_view = ""
        for i in range(len(answer)):
            answer_view += f"```\n{keyAns[i] + answer[i].answer}\n```"
        embed.add_field(
            name="Answer",
            value=answer_view,
            inline=False
        )
    else:
        answer_view = ""
        for i in range(len(answer)):
            if i == correctAnswer:
                answer_view += f"```diff\n+{keyAns[i] + answer[i].answer}\n```"
                continue
            if i == choice:
                answer_view += f"```diff\n-{keyAns[i] + answer[i].answer}\n```"
                continue
            answer_view += f"```\n{keyAns[i] + answer[i].answer}\n```"
        embed.add_field(
            name="Answer",
            value=answer_view,
            inline=False
        )
    embed.add_field(
        name="Hint",
        value="|| This is a hint ||",
        inline=False
    )
    return embed


class NavButton(discord.ui.Button['ChooseQuestion']):
    def __init__(self, button_type: int, isCorrect: bool, style: discord.ButtonStyle, is_disabled: bool = False,
                 emoji: typing.Union[str, discord.Emoji, discord.PartialEmoji, None] = None, label: str = None):
        super().__init__(style=style, label=label, disabled=is_disabled, emoji=emoji)
        self.button_type = button_type
        self.isCorrect = isCorrect

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        embed = createEmbed(self.view.question, self.button_type)
        if interaction.user != self.view.user: return
        if self.isCorrect:
            embed.add_field(
                name="You're correct !!! ",
                value='',
                inline=False
            )
        else:
            embed.add_field(
                name="Wrong!!! You chose " + keyAns[self.button_type] + " But the correct answer is " + keyAns[
                    self.view.correct_answer],
                value='',
                inline=False
            )
        self.view.disable_answer()
        await interaction.edit_original_response(embed=embed, view=self.view)


class ChooseQuestion(discord.ui.View):
    children: typing.List[typing.Union[NavButton]]

    def __init__(self, question: None, correctAnswer: int, user):
        super().__init__()
        self.response = None
        self.question = question
        self.user = user
        for i in range(len(question[1])):
            self.add_item(NavButton(button_type=i, isCorrect=(i == correctAnswer), style=discord.ButtonStyle.gray,
                                    is_disabled=False,
                                    emoji=iconKey[i]))
        self.correct_answer = correctAnswer

    def disable_answer(self):
        for i in range(4):
            self.children[i].disabled = True


class Quiz(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name='quiz', description="Get some easy quiz questions")
    @app_commands.choices(
        difficulty=[
            app_commands.Choice(name="Easy", value="easy"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Hard", value="hard"),
        ]
    )
    @app_commands.describe(
        difficulty='Choose a difficulty (default: Any)',
        category='Choose a topic (default: Any)'
    )
    async def _quiz(self,
                    interaction: discord.Interaction,
                    difficulty: app_commands.Choice[str] = None,
                    category: Optional[str] = None):
        await interaction.response.defer(thinking=True)
        quiz_detail = {}
        if difficulty:
            quiz_detail['difficulty'] = difficulty.name
        if category:
            quiz_detail['category'] = category

        quiz_result = self.client.db_api.read_quiz(quiz_detail)

        if len(quiz_result) == 0:
            await interaction.followup.send(embed=discord.Embed(
                description="Sorry, data for the question is being updated, please come back later"))
            return

        view = ChooseQuestion(quiz_result, quiz_result[0].correctAnswerId - quiz_result[1][0].id, interaction.user)
        await interaction.followup.send(embed=createEmbed(quiz_result), view=view)
        view.response = await interaction.original_response()

    @_quiz.autocomplete('category')
    async def _quiz_autocomplete(self, interaction: discord.Interaction, current: str):
        tags = TOPIC_TAGS
        return [app_commands.Choice(name=tag, value=tag) for tag in tags][:len(TOPIC_TAGS)]


async def setup(client):
    await client.add_cog(Quiz(client), guilds=[discord.Object(id=client.config['serverId'])])
