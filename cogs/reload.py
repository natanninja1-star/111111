import os
import discord
from discord.ext import commands

class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload-cogs-all")
    async def reload_cogs_all(self, ctx):
        # Sprawdzamy czy osoba wpisująca komendę to administrator/właściciel serwera (dla bezpieczeństwa)
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Nie masz uprawnień do użycia tej komendy!")
            return

        sukcesy = 0
        bledy = 0

        # Pętla przechodząca przez wszystkie pliki w folderze cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = filename[:-3]
                # Pomijamy plik reload.py, żeby nie zepsuć przeładowania w trakcie
                if cog_name == "reload":
                    continue
                
                try:
                    # Najpierw próbujemy wyładować moduł, a potem załadować na nowo
                    await self.bot.reload_extension(f"cogs.{cog_name}")
                    sukcesy += 1
                except Exception as e:
                    # Jeśli moduł jeszcze nie był załadowany, spróbujemy go po prostu wczytać
                    try:
                        await self.bot.load_extension(f"cogs.{cog_name}")
                        sukcesy += 1
                    except Exception as e2:
                        bledy += 1
                        print(f"Błąd przeładowania {cog_name}: {e2}")

        # Wysyłamy podsumowanie na czat
        embed = discord.Embed(
            title="🔄 Przeładowanie modułów",
            description=f"Pomyślnie przeładowano: **{sukcesy}** modułów.\nBłędy: **{bledy}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reload(bot))