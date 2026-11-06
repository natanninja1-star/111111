import random
import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput

# --- OKIENKO (MODAL / GUI) WERYFIKACJI ---
class VerifyModal(Modal):
    def __init__(self, num1: int, num2: int, correct_answer: int, verified_role_name: str):
        super().__init__(title="Formularz Weryfikacyjny")
        self.correct_answer = correct_answer
        self.verified_role_name = verified_role_name

        self.answer_input = TextInput(
            label=f"Rozwiąż Działanie: {num1} + {num2}",
            placeholder="Wpisz wynik cyframi (np. 15)...",
            required=True,
            max_length=5
        )
        self.add_item(self.answer_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_text = self.answer_input.value.strip()

        try:
            user_answer = int(user_text)
        except ValueError:
            await interaction.response.send_message("❌ To nie jest poprawna liczba! Spróbuj ponownie kliknąć przycisk.", ephemeral=True)
            return

        if user_answer == self.correct_answer:
            guild = interaction.guild
            # Szukamy lub tworzymy rangę dla zweryfikowanych
            role = discord.utils.get(guild.roles, name=self.verified_role_name)
            if not role:
                role = await guild.create_role(name=self.verified_role_name, color=discord.Color.green())

            # Przypisujemy rangę użytkownikowi
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ Pomyślnie przeszto weryfikację! Witaj na serwerze.", ephemeral=True)
            except Exception:
                await interaction.response.send_message("⚠️ Bot nie ma uprawnień do nadania rangi! Przesuń rangę bota wyżej w ustawieniach serwera.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Błędny wynik! Spróbuj ponownie kliknąć przycisk i policzyć jeszcze raz.", ephemeral=True)

# --- WIDOK Z PRZYCISKIEM OTWIERAJĄCYM GUI ---
class VerifyView(View):
    def __init__(self, role_name: str):
        super().__init__(timeout=None)
        self.role_name = role_name

    @discord.ui.button(label="Zweryfikuj się", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_modal_button")
    async def verify_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Losujemy dwie liczby do działania matematycznego
        num1 = random.randint(1, 15)
        num2 = random.randint(1, 15)
        correct_answer = num1 + num2

        # Otwieramy okienko GUI (Modal) dla użytkownika
        await interaction.response.send_modal(VerifyModal(num1, num2, correct_answer, self.role_name))

# --- COG / KOMENDA SETUPOWA ---
class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup-verify")
    @commands.has_permissions(administrator=True)
    async def setup_verify(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        guild = ctx.guild
        role_name = "Zweryfikowany"

        # Tworzymy rangę, jeśli jeszcze nie istnieje
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await guild.create_role(name=role_name, color=discord.Color.green())

        # Estetyczny Embed w stylu systemu ticketów
        embed = discord.Embed(
            title="✅kom WERYFIKACJA SERWERA",
            description="Aby uzyskać dostęp do kanałów, musisz potwierdzić, że jesteś człowiekiem.\n\n**Kliknij przycisk poniżej**, aby otworzyć okienko weryfikacyjne i rozwiązać proste zadanie matematyczne.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        if ctx.bot.user.avatar:
            embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        embed.set_footer(text="System Bezpieczeństwa | Ochrona przed botami")

        await ctx.send(embed=embed, view=VerifyView(role_name))

async def setup(bot):
    await bot.add_cog(Verify(bot))