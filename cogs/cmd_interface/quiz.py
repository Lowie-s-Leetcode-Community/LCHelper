import sys
import typing

import discord
from discord import app_commands
from discord.ext import commands

import random

keyAns = ['A. ', 'B. ', 'C. ', 'D. ']
correctAnswer = -1;
iconKey = ['🇦', '🇧', '🇨', '🇩']
QA = None


def createEmbed(QandA: list, choice: int = -1):

    question = QandA[0]
    answer = QandA[1]

    global correctAnswer
    correctAnswer = (question.correctAnswerId - 1)%4

    embed = discord.Embed(
        color=0xff822e,
    )
    embed.set_author(
        name="Quiz: ",
        icon_url="https://assets.leetcode.com/users/leetcode/avatar_1568224780.png"
    )
    embed.add_field(
        name="Quiz for difficulty " + question.difficulty + " and category " + question.category,
        value= question.question,
        inline=False
    )
    if (choice == -1):
        answer_view = ""
        for i in range(4):
            answer_view += "```\n" + keyAns[i] + answer[i].answer + '\n```'
        embed.add_field(
            name="Answer",
            value=answer_view,
            inline=False
        )
    else:
        answer_view = ""
        print(correctAnswer)
        for i in range(4):
            if (i == correctAnswer):
                answer_view += "```diff\n+" + keyAns[i] + answer[i].answer + "\n```"
                continue
            if (i == choice):
                answer_view += "```diff\n-" + keyAns[i] + answer[i].answer + "\n```"
                continue
            answer_view += "```\n" + keyAns[i] + answer[i].answer + '\n```'
        embed.add_field(
            name="Answer",
            value=answer_view,
            inline=False
        )
    embed.add_field(
        name="Hint",
        value="||" + "This is a hint" + "||",
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
        global_embed = createEmbed(QA, self.button_type)
        if self.isCorrect:
            global_embed.add_field(
                name="You corect !!! ",
                value='',
                inline=False
            )
        else:
            global_embed.add_field(
                name= "You wrong!!! You choose " + keyAns[self.button_type] +" But the correct answer is " + keyAns[self.view.correct_answer],
                value='',
                inline=False
            )
        self.view.disable_answer()
        await interaction.edit_original_response(embed=global_embed, view = self.view)

class ChooseQuestion(discord.ui.View):
    children: typing.List[typing.Union[NavButton]]

    def __init__(self, correctAnswer: int):
        super().__init__()
        self.response = None
        self.answer = None
        for i in range(4):
            self.add_item(NavButton(button_type=i, isCorrect=i == correctAnswer, style=discord.ButtonStyle.gray,
                                    is_disabled= False,
                                    emoji=iconKey[i]))
        self.correct_answer = correctAnswer

    def disable_answer(self):
        for i in range(4):
            self.children[i].disabled = True

class Quiz(commands.Cog):
    def __init__(self, client):
        self.DB_Quiz = None
        self.client = client

    @app_commands.command(name='quiz', description="Các câu lệnh của LCHelper")
    @app_commands.choices(
        difficulty=[
            app_commands.Choice(name="Easy", value="easy"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Hard", value="hard"),
        ],
        category=[
            app_commands.Choice(name="Algorithms", value="algorithms"),
            app_commands.Choice(name="Concurrency", value="concurrency"),
            app_commands.Choice(name="Distributed Systems", value="distributed systems"),
            app_commands.Choice(name="Software Architecture", value="software architecture"),
            app_commands.Choice(name="Complexity Theory", value="complexity theory")
        ]
    )
    @app_commands.describe(
        difficulty='Choose a diffculty (default: Any)',
        category='Choose a (default: Any)'
    )
    async def _quiz(self,
                    interaction: discord.Interaction,
                    difficulty: app_commands.Choice[str] = None,
                    category: app_commands.Choice[str] = None):
        await interaction.response.defer(thinking=True)

        quiz_detail = {}
        if difficulty:
            quiz_detail['difficulty'] = difficulty.name
        if category:
            quiz_detail['category'] = category.name

        global QA
        quiz_result = []
        # The optimization when the user calls Quiz many times
        if (len(quiz_detail) == 0):
            if (self.DB_Quiz == None):
                self.DB_Quiz = self.client.db_api.read_all_quiz()
                print("Empty")
            quiz = self.DB_Quiz[random.randint(0, len(self.DB_Quiz) - 1)]
            answer = self.client.db_api.read_answer_for_quiz(quiz.id)
            quiz_result.append(quiz)
            quiz_result.append(answer)
        else : quiz_result = self.client.db_api.read_quiz(quiz_detail)
        # quiz_result = self.client.db_api.read_quiz(quiz_detail)
        QA = quiz_result
        if len(quiz_result) == 0:
            await interaction.followup.send(embed=discord.Embed(
                description="Sorry, data for the question is being updated, please come back later"))
            return;

        global ans
        ans = quiz_result[0].correctAnswerId - 1

        view = ChooseQuestion(ans % 4)
        await interaction.followup.send(embed=createEmbed(QA), view=view)
        view.response = await interaction.original_response()


async def setup(client):
    await client.add_cog(Quiz(client), guilds=[discord.Object(id=client.config['serverId'])])
