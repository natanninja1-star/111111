import discord
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test")
    async def test_komenda(self, ctx):
        await ctx.send("Czesc! Modul testowy dziala poprawnie.")

async def setup(bot):
    await bot.add_cog(Test(bot))