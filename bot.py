import asyncio
import os
import discord
from discord.ext import commands

# 1. Konfiguracja uprawnień
intents = discord.Intents.default()
intents.message_content = True

# 2. Tworzenie bota z prefixem !
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. Pojedyncza, automatyczna pętla ładująca moduły z folderu "cogs"
async def load_extensions():
    print("-" * 45)
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"📦 Załadowano moduł: cogs.{cog_name}")
            except Exception as e:
                print(f"⚠️ Nie udało się załadować modułu cogs.{cog_name}: {e}")

# 4. Komunikat po uruchomieniu bota
@bot.event
async def on_ready():
    print("-" * 45)
    print(f"🤖 Bot {bot.user.name} jest AKTYWNY i gotowy do działania!")
    print(f"ID bota: {bot.user.id}")
    print("-" * 45)

# 5. Funkcja startowa
async def main():
    async with bot:
        await load_extensions()
        # Wpisz tutaj swój token bota w cudzysłowie:
        await bot.start("MTU2NzIzMTQ0NzEzNDI0OTA1MA.GUVtMO.Pskx1DB1f5zEIOIqJLJMZt-cYe53jX6gCyKg40")

# Uruchomienie bota
asyncio.run(main())