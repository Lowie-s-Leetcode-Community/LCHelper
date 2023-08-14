import discord
import os
from discord.ext import commands
import datetime
import typing
import urllib
import requests
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy
from utils.asset import Assets

class cf(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name = "plot")
    async def _plot(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("hi")

    @_plot.command(name = "performance")
    async def _performance(self, ctx, *, msg):
        handles = msg.split();
        if len(handles) > 5:
            await ctx.send(f"{Assets.red_tick} **Numbers of handles must be 5 or below**")
        plt.figure(figsize=(7, 4))
        minPerformanceDelta = 10000
        maxPerformanceDelta = 0
        color = ["#442288", "#5D4DFF", "#B5D33D", "#FED23F", "#EB7D5B"]
        colorCnt = 0

        for handle in handles:
            link = f"https://codeforces.com/api/user.rating?handle={handle}"
            r = requests.get(link)
            f = json.loads(r.content)
            performanceDelta = []
            ratingUpdateTime = []
            try:
                if f['result'][0]['newRating'] <= 1000:
                    trueRatingDelta = [500, 350, 250, 150, 100, 50, 0]
                    cnt = 0
                    s = 0
                else:
                    cnt = 5
                    s = 0
                    trueRatingDelta = [0, 0, 0, 0, 0, 1400, 0]
            except:
                await ctx.send(f"{Assets.red_tick} **User `{handle}` hasn't participated in a contest.**")
                break
            for i in f['result']:
                tmp = -3*(i['oldRating'] - s + 1400)
                s += trueRatingDelta[cnt]
                tmp += 4*(i['newRating'] - s + 1400)
                performanceDelta.append(tmp)
                ratingUpdateTime.append(datetime.datetime.fromtimestamp(i['ratingUpdateTimeSeconds']))
                if cnt < 6: cnt += 1

            plt.plot(
                ratingUpdateTime,
                performanceDelta,
                marker = "o",
                color  = color[colorCnt],
                label  = f"{handle} ({f['result'][-1]['newRating']})",
                mew    = 1,
                ms     = 3,
                mfc    = "w",
            )

            maxPerformanceDelta = max(maxPerformanceDelta, max(performanceDelta))
            minPerformanceDelta = min(minPerformanceDelta, min(performanceDelta))
            colorCnt += 1

        if (maxPerformanceDelta == 0):
            return
        if (maxPerformanceDelta >= 0): plt.axhspan(min(900, minPerformanceDelta), 1195, facecolor = '#cccccc', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 1200): plt.axhspan(1200, 1395, facecolor = '#77ff77', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 1400): plt.axhspan(1400, 1595, facecolor = '#77ddbb', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 1600): plt.axhspan(1600, 1895, facecolor = '#aaaaff', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 1900): plt.axhspan(1900, 2095, facecolor = '#ff88ff', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 2100): plt.axhspan(2100, 2295, facecolor = '#ffcc88', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 2300): plt.axhspan(2300, 2395, facecolor = '#ffbb55', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 2400): plt.axhspan(2400, 2595, facecolor = '#ff7777', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 2600): plt.axhspan(2600, 2995, facecolor = '#ff3333', alpha = 1, zorder = -100)
        if (maxPerformanceDelta >= 3000): plt.axhspan(3000, 4505, facecolor = '#aa0000', alpha = 1, zorder = -100)


        plt.legend(loc='upper left')
        plt.margins(y=0)
        plt.xticks(rotation = "30")
        plt.yticks(numpy.arange((minPerformanceDelta // 100 * 100), (maxPerformanceDelta + 100) // 100 * 100, 200))
        plt.title('Performance Graph')
        plt.gcf().autofmt_xdate()
        plt.grid(axis = 'x')
        plt.savefig('potato.png')
        plt.clf()
        embed = discord.Embed(
            title = "Performance graph on Codeforces",
            timestamp = ctx.message.created_at,
            author = ctx.message.author
        )
        embed.set_footer(
            text = ctx.author,
            icon_url = ctx.message.author.avatar.url
        )
        file = discord.File("./potato.png", filename = "potato.png")
        embed.set_image(url = "attachment://potato.png")

        await ctx.send(file = file, embed = embed)
        os.remove(r'./potato.png')



async def setup(client):
    await client.add_cog(cf(client))
