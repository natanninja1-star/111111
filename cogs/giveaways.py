import discord
from discord.ext import commands
import asyncio
import time
import random

# --- 1. FORMULARZ KONFIGURACYJNY GIVEAWAYA ---
class GiveawaySetupModal(discord.ui.Modal, title="Stwórz Giveaway"):
    def __init__(self):
        super().__init__()

        self.nagroda = discord.ui.TextInput(
            label="Nagroda",
            placeholder="Np. Ranga VIP / Nagroda specjalna",
            required=True,
            max_length=100
        )
        self.czas = discord.ui.TextInput(
            label="Czas trwania (w minutach)",
            placeholder="Np. 1 (dla 1 minuty)",
            required=True,
            max_length=5
        )
        self.rola_id = discord.ui.TextInput(
            label="ID Rangi z bonusem losów (opcjonalnie)",
            placeholder="Wpisz ID roli lub zostaw puste",
            required=False,
            max_length=30
        )
        self.waga_mnoznik = discord.ui.TextInput(
            label="Ile dodatkowych losów daje ta ranga?",
            placeholder="Wpisz cyfrę (np. 3, 5...)",
            required=False,
            max_length=5
        )

        self.add_item(self.nagroda)
        self.add_item(self.czas)
        self.add_item(self.rola_id)
        self.add_item(self.waga_mnoznik)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            czas_min = int(self.czas.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Czas musi być liczbą całkowitą (w minutach)!", ephemeral=True)
            return

        waga = 1
        if self.waga_mnoznik.value.strip().isdigit():
            waga = int(self.waga_mnoznik.value.strip())

        nagroda_tekst = self.nagroda.value.strip()
        rola_id = int(self.rola_id.value.strip()) if self.rola_id.value.strip().isdigit() else None

        await interaction.response.send_message(f"✅ Uruchomiono giveaway o nagrodę: **{nagroda_tekst}** na **{czas_min} min**!", ephemeral=True)

        end_timestamp = int(time.time() + (czas_min * 60))
        view = GiveawayView(czas_min, nagroda_tekst, rola_id, waga, interaction.user, end_timestamp)

        embed = discord.Embed(
            title="🎉 **GIVEAWAY** 🎉",
            description=(
                f"Do wygrania: **{nagroda_tekst}**\n\n"
                f"Kliknij przycisk **🎉 Weź udział!**, aby dołączyć.\n"
                f"📊 Sprawdź swoje szanse przyciskiem **Moje Statystyki**!\n\n"
                f"👥 **Liczba uczestników:** 0\n"
                f"⏱️ **Koniec za:** <t:{end_timestamp}:R>\n"
                f"👑 **Organizator:** {interaction.user.mention}"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="System Giveaways | Szansa: 0.0%")

        message = await interaction.channel.send(embed=embed, view=view)
        view.message = message

        elapsed = 0
        while elapsed < (czas_min * 60):
            if view.is_ended:
                return
            await asyncio.sleep(1)
            elapsed += 1

        await view.end_giveaway()


# --- 2. WIDOK Z PRZYCISKAMI ---
class GiveawayView(discord.ui.View):
    def __init__(self, duration_mins: int, prize: str, role_id: int, role_weight: int, host: discord.Member, end_timestamp: int):
        super().__init__(timeout=None)
        self.duration_mins = duration_mins
        self.prize = prize
        self.role_id = role_id
        self.role_weight = role_weight
        self.host = host
        self.end_timestamp = end_timestamp
        
        self.participants = {}
        self.message = None
        self.is_ended = False

    async def update_embed_stats(self, user_id_checking=None):
        if self.is_ended or not self.message:
            return

        total_participants = len(self.participants)
        total_tickets = sum(self.participants.values())
        
        if user_id_checking and user_id_checking in self.participants and total_tickets > 0:
            user_tickets = self.participants[user_id_checking]
            user_chance = (user_tickets / total_tickets) * 100
            footer_text = f"System Giveaways | Twoja szansa: {user_chance:.1f}%"
        else:
            footer_text = f"System Giveaways | Uczestników: {total_participants}"

        embed = discord.Embed(
            title="🎉 **GIVEAWAY** 🎉",
            description=(
                f"Do wygrania: **{self.prize}**\n\n"
                f"Kliknij przycisk **🎉 Weź udział!**, aby dołączyć.\n"
                f"📊 Sprawdź swoje szanse przyciskiem **Moje Statystyki**!\n\n"
                f"👥 **Liczba uczestników:** {total_participants}\n"
                f"⏱️ **Koniec za:** <t:{self.end_timestamp}:R>\n"
                f"👑 **Organizator:** {self.host.mention}"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text=footer_text)

        try:
            await self.message.edit(embed=embed, view=self)
        except:
            pass

    @discord.ui.button(label="Weź udział!", style=discord.ButtonStyle.success, emoji="🎉", custom_id="join_giveaway_btn")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_ended:
            await interaction.response.send_message("❌ Ten giveaway już się zakończył!", ephemeral=True)
            return

        user = interaction.user
        user_id = user.id

        if user_id in self.participants:
            await interaction.response.send_message("❌ Już bierzesz udział w tym giveawayu!", ephemeral=True)
            return

        weight = 1
        info_tekst = "Zwykły los (1x)"

        if self.role_id and any(r.id == self.role_id for r in user.roles):
            weight = self.role_weight
            info_tekst = f"Ranga bonusowa ({weight}x losów!)"

        self.participants[user_id] = weight
        await self.update_embed_stats(user_id)

        total_tickets = sum(self.participants.values())
        user_chance = (weight / total_tickets) * 100 if total_tickets > 0 else 0

        await interaction.response.send_message(
            f"✅ Dołączyłeś do giveawayu!\n🎟️ Przyznano Ci losów: **{weight}** ({info_tekst})\n📊 Twoja aktualna szansa na wygraną: **{user_chance:.1f}%**",
            ephemeral=True
        )

    @discord.ui.button(label="Moje Statystyki", style=discord.ButtonStyle.secondary, emoji="📊", custom_id="stats_giveaway_btn")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id not in self.participants:
            await interaction.response.send_message("❌ Nie bierzesz jeszcze udziału. Kliknij najpierw 'Weź udział!'", ephemeral=True)
            return

        await self.update_embed_stats(user_id)

        total_participants = len(self.participants)
        total_tickets = sum(self.participants.values())
        user_tickets = self.participants[user_id]
        user_chance = (user_tickets / total_tickets) * 100

        await interaction.response.send_message(
            f"📊 **Twoje statystyki w giveawayu:**\n"
            f"👥 Unikalnych uczestników: **{total_participants}**\n"
            f"🎟️ Twoje losy: **{user_tickets}** z **{total_tickets}** wszystkich\n"
            f"🎯 Szansa na wygraną: **{user_chance:.1f}%**",
            ephemeral=True
        )

    @discord.ui.button(label="Usuń Giveaway", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="delete_giveaway_btn")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_host = interaction.user.id == self.host.id
        is_admin = interaction.user.guild_permissions.manage_messages

        if not (is_host or is_admin):
            await interaction.response.send_message("❌ Tylko organizator tego givawaya lub moderator może go usunąć!", ephemeral=True)
            return

        self.is_ended = True
        try:
            if self.message:
                await self.message.delete()
        except:
            pass

        await interaction.response.send_message(f"🗑️ Giveaway nagrody **{self.prize}** został usunięty przez {interaction.user.mention}.", ephemeral=True)

    async def end_giveaway(self):
        if self.is_ended:
            return
        self.is_ended = True

        channel = self.message.channel if self.message else None

        # Automatyczne usuwanie starej wiadomości z giveawayem z kanału
        try:
            if self.message:
                await self.message.delete()
        except:
            pass

        if not channel:
            return

        if not self.participants:
            await channel.send(f"❌ Giveaway nagrody **{self.prize}** został zakończony, ale nikt nie wziął w nim udziału!", delete_after=10)
            return

        ticket_pool = []
        for user_id, weight in self.participants.items():
            for _ in range(weight):
                ticket_pool.append(user_id)

        winner_id = random.choice(ticket_pool)
        
        # Pobieramy użytkownika bezpiecznie przez fetch_member (żeby nie pisało bzdur o wyjściu z serwera)
        winner = None
        try:
            winner = await channel.guild.fetch_member(winner_id)
        except:
            winner = channel.guild.get_member(winner_id)

        total_participants = len(self.participants)
        total_tickets = len(ticket_pool)
        winner_tickets = self.participants[winner_id]
        winner_chance = (winner_tickets / total_tickets) * 100

        if winner:
            win_embed = discord.Embed(
                title="🏆 **WYNIKI GIVEAWAYA** 🏆",
                description=(
                    f"Nagroda: **{self.prize}**\n"
                    f"Zwycięzca: {winner.mention}! 🎉\n\n"
                    f"📈 **Statystyki:**\n"
                    f"• Uczestników: **{total_participants}**\n"
                    f"• Posiadane losy: **{winner_tickets}/{total_tickets}**\n"
                    f"• Szansa na wygraną wynosiła: **{winner_chance:.1f}%**"
                ),
                color=discord.Color.green()
            )
            await channel.send(embed=win_embed)
        else:
            await channel.send(f"🎉 Giveaway zakończony! Zwycięzca o ID `{winner_id}` wygrał nagrodę, ale nie udało się pobrać jego profilu.")


# --- 3. COG / KOMENDA ---
class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup-giveaway", aliases=["giveaway-setup"])
    @commands.has_permissions(administrator=True)
    async def setup_giveaway(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        view = discord.ui.View()
        button = discord.ui.Button(label="Stwórz Giveaway (GUI)", style=discord.ButtonStyle.primary, emoji="🎁", custom_id="open_giveaway_modal")
        
        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(GiveawaySetupModal())

        button.callback = button_callback
        view.add_item(button)

        embed = discord.Embed(
            title="🎁 PANEL GIVEAWAYS",
            description="Kliknij przycisk poniżej, aby otworzyć okienko i skonfigurować nowy **Giveaway**!\n\n*Wiadomość z konkursem usuwa się automatycznie po zakończeniu, a zwycięzca jest poprawnie weryfikowany.*",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        embed.set_footer(text="Panel Administratora")

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Giveaways(bot))