import discord
from discord.ext import commands

class AutoDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Nasłuchuje każdej pomyślnie wykonanej komendy na serwerze
    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            # Usuwa wiadomość użytkownika, który wywołał komendę
            await ctx.message.delete()
        except discord.Forbidden:
            # Bot nie ma uprawnień do usuwania wiadomości
            pass
        except discord.NotFound:
            # Wiadomość została już wcześniej usunięta
            pass

async def setup(bot):
    await bot.add_cog(AutoDelete(bot))