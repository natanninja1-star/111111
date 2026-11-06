import discord
from discord.ext import commands
import re

class AntiLinkAndSwear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Lista polskich przekleństw (oraz ich najpopularniejszych odmian/wariantów)
        self.bad_words = [
            "kurwa", "chuj", "jebać", "pierdol", "pizda", "skurwysyn", 
            "cipa", "huj", "peda", "ciul", "frajer", "pierdoli", "chujowy",
            "zjeb", "zajeb", "wyjeb", "podjeb", "chujo", "kurw", "kutas"
        ]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignorujemy wiadomości od bota oraz wiadomości prywatne (DM)
        if message.author.bot or not message.guild:
            return

        # Administratorzy i moderatorzy są zwolnieni z filtrów
        if message.author.guild_permissions.manage_messages:
            return

        # Sprawdzanie czy użytkownik posiada rangę zwolnienia z antylinka (perm.antylink)
        antylink_role = discord.utils.get(message.guild.roles, name="perm.antylink")
        if antylink_role and antylink_role in message.author.roles:
            return # Jeśli ma tę rolę, bot ignoruje jego wiadomości (nie filtruje linków ani słów)

        content_lower = message.content.lower()

        # --- 1. SPRAWDZANIE LINKÓW (Antylink) ---
        # Szukamy linków http://, https:// lub discord.gg/ zaproszeń
        url_pattern = re.compile(r'https?://|discord\.gg/|www\.', re.IGNORECASE)
        if url_pattern.search(message.content):
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"❌ {message.author.mention}, wysyłanie linków na tym serwerze jest zabronione!", 
                    delete_after=6
                )
                return
            except Exception:
                pass

        # --- 2. SPRAWDZANIE PRZEKLEŃSTW (Anty-wulgaryzmy) ---
        # Dzielimy wiadomość na słowa lub sprawdzamy podciągi
        words = re.findall(r'\b\w+\b', content_lower)
        
        is_bad = False
        for word in words:
            for bad in self.bad_words:
                if bad in word:
                    is_bad = True
                    break
            if is_bad:
                break

        if is_bad:
            try:
                await message.delete()
                await message.channel.send(
                    f"❌ {message.author.mention}, proszę nie używać wulgaryzmów na tym serwerze!", 
                    delete_after=6
                )
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(AntiLinkAndSwear(bot))