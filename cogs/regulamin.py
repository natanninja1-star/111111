import discord
from discord.ext import commands

class Regulamin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="regulamin")
    async def regulamin(self, ctx):
        # Usuwamy wiadomość z komendą !regulamin, żeby czat był czysty
        try:
            await ctx.message.delete()
        except:
            pass

        # Główny Embed z rozbudowanym regulaminem
        embed = discord.Embed(
            title="📋 KOMPLEKSOWY REGULAMIN SERWERA",
            description="Witaj! Poniższy regulamin określa zasady panujące na naszym serwerze. Dołączenie do społeczności jest jednoznaczne z akceptacją poniższych punktów.",
            color=discord.Color.from_rgb(88, 101, 242)
        )

        # Miniaturka w prawym górnym rogu (awatar bota)
        if ctx.bot.user.avatar:
            embed.set_thumbnail(url=ctx.bot.user.avatar.url)

        embed.add_field(
            name="1. Ogólne zasady kultury osobistej",
            value="• Bezwzględny szacunek do każdego użytkownika.\n• Zakaz używania mowy nienawiści, rasizmu, seksizmu i dyskryminacji.\n• Zakaz prowokowania kłótni, toksycznych zachowań oraz dram.",
            inline=False
        )

        embed.add_field(
            name="2. Czat, wiadomości i spam",
            value="• Zakaz spamu, floodowania oraz nadmiernego używania CAPS LOCK-a.\n• Zakaz wysyłania łańcuszków szczęścia i masowych pingów.\n• Używaj kanałów zgodnie z ich tematyką i przeznaczeniem.",
            inline=False
        )

        embed.add_field(
            name="3. Reklamy i linki",
            value="• Całkowity zakaz reklamowania innych serwerów Discord, stron oraz mediów społecznościowych bez zgody.\n• Zakaz wysyłania zaproszeń w wiadomościach prywatnych (DM) do innych członków serwera.\n• Zakaz udostępniania podejrzanych linków, IP grabberów i plików z wirusami.",
            inline=False
        )

        embed.add_field(
            name="4. Treści NSFW i materiały drastyczne",
            value="• Bezwzględny zakaz publikowania treści erotycznych, pornograficznych (NSFW) oraz 18+.\n• Zakaz wysyłania materiałów drastycznych, przemocy, krwi i gore.\n• Zakaz wrzucania memów lub filmów o skrajnie kontrowersyjnej tematyce.",
            inline=False
        )

        embed.add_field(
            name="5. Profile, nicki i avatary",
            value="• Nazwa użytkownika, nick na serwerze oraz avatar muszą być cenzuralne i odpowiednie dla osób w każdym wieku.\n• Zakaz ustawiania nicków składających się z samych niewidocznych znaków lub utrudniających oznaczenie.",
            inline=False
        )

        embed.add_field(
            name="6. Kanały głosowe i mikrofon",
            value="• Zakaz puszczania muzyki, earrape'ów i dźwięków z soundboardów na kanałach publicznych bez zgody osób siedzących na kanale.\n• Zakaz używania zmieniaczy głosu w celu zagłuszania lub denerwowania innych.\n• Przebywanie na kanałach AFK w przypadku braku aktywności.",
            inline=False
        )

        embed.add_field(
            name="7. Administracja i sankcje",
            value="• Decyzje administracji są ostateczne i należy się do nich bezwzględnie stosować.\n• Nieznajomość regulaminu nie zwalnia z obowiązku jego przestrzegania.\n• Za złamanie zasad grozi: ostrzeżenie (warn), wyciszenie (mute), wyrzucenie (kick) lub ban.\n• Problemy i zgłoszenia kieruj poprzez oficjalny system ticketów.",
            inline=False
        )

        embed.set_footer(text="Dziękujemy za przestrzeganie zasad! Życzymy udanego pobytu | Administracja")
        
        # Opcjonalny baner graficzny na dole (odkomentuj i wklej link, jeśli chcesz):
        # embed.set_image(url="https://cdn.discordapp.com/attachments/1070393673239507075/1564737148685656064/945s91n.png?ex=6aeaec47&is=6ae99ac7&hm=4f90b1d0c51d6b9af8b3f3e408dc1c8561b1671e3689f949e918fa0b4cc57a77&")

        # Wysyłamy embed na kanał
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Regulamin(bot))