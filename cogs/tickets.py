import io
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput

# --- MODAL DLA ZWYKŁYCH TICKETÓW ---
class StandardTicketModal(Modal):
    def __init__(self, category_name: str):
        super().__init__(title=f"Ticket: {category_name}")
        self.category_name = category_name

        self.nick_mc = TextInput(
            label="Nick z gry (Minecraft)",
            placeholder="Twój nick...",
            required=True,
            max_length=50
        )
        self.problem_desc = TextInput(
            label="Opis sprawy",
            style=discord.TextStyle.paragraph,
            placeholder="Opisz dokładnie, w czym możemy pomóc...",
            required=True,
            max_length=1000
        )
        self.proof_link = TextInput(
            label="Link do dowodu (klip, SS, nagranie)",
            style=discord.TextStyle.short,
            placeholder="Wklej link lub wpisz 'brak'",
            required=False,
            max_length=200
        )

        self.add_item(self.nick_mc)
        self.add_item(self.problem_desc)
        self.add_item(self.proof_link)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, self.category_name, {
            "Nick z gry": self.nick_mc.value,
            "Opis sprawy": self.problem_desc.value,
            "Dowód": self.proof_link.value or "Brak dowodu"
        })

# --- MODAL DLA REKRUTACJI (5 PYTAŃ) ---
class RecruitsModal(Modal):
    def __init__(self):
        super().__init__(title="Formularz Rekrutacyjny")

        self.nick_mc = TextInput(
            label="1. Nick z gry (Minecraft)",
            placeholder="Twój nick...",
            required=True,
            max_length=50
        )
        self.premium = TextInput(
            label="2. Czy posiadasz Minecraft Premium?",
            placeholder="Tak / Nie",
            required=True,
            max_length=10
        )
        self.experience = TextInput(
            label="3. Doświadczenie jako administrator",
            style=discord.TextStyle.paragraph,
            placeholder="Opisz swoje dotychczasowe doświadczenie...",
            required=True,
            max_length=500
        )
        self.cheats = TextInput(
            label="4. Znajomość narzędzi (Process Hacker itp.)",
            style=discord.TextStyle.paragraph,
            placeholder="Process Hacker, System Informator, AnyDesk...",
            required=True,
            max_length=500
        )
        self.activity = TextInput(
            label="5. Ile czasu poświęcisz i dlaczego ty?",
            style=discord.TextStyle.paragraph,
            placeholder="Ile grasz dziennie i dlaczego mamy Cię wybrać?",
            required=True,
            max_length=500
        )

        self.add_item(self.nick_mc)
        self.add_item(self.premium)
        self.add_item(self.experience)
        self.add_item(self.cheats)
        self.add_item(self.activity)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, "Rekrutacja", {
            "Nick z gry": self.nick_mc.value,
            "Minecraft Premium": self.premium.value,
            "Doświadczenie": self.experience.value,
            "Wykrywanie cheatów": self.cheats.value,
            "Aktywność i dlaczego ty": self.activity.value
        })

# --- FUNKCJA TWORZĄCA KANAŁ TICKETU ---
async def create_ticket_channel(interaction: discord.Interaction, category_name: str, answers: dict):
    await interaction.response.defer(thinking=True, ephemeral=True)
    
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="🎟️ TICKETY")
    if not category:
        category = await guild.create_category("🎟️ TICKETY")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
    }

    ticket_see_role = discord.utils.get(guild.roles, name="perm.ticket.see")
    if ticket_see_role:
        overwrites[ticket_see_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    channel_name = f"ticket-{interaction.user.name}".lower()
    ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)

    embed = discord.Embed(
        title=f"🎟️ Ticket: {category_name}",
        description=f"Witaj {interaction.user.mention}!\nOto szczegóły Twojego zgłoszenia:",
        color=discord.Color.from_rgb(88, 101, 242)
    )

    for field_name, field_value in answers.items():
        embed.add_field(name=field_name, value=field_value, inline=False)

    embed.set_footer(text="Aby zamknąć ticket, kliknij przycisk poniżej.")

    close_view = View(timeout=None)
    close_btn = discord.ui.Button(label="🔒 Zamknij ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    
    async def close_callback(i: discord.Interaction):
        ticket_see_role = discord.utils.get(i.guild.roles, name="perm.ticket.see")
        has_permission = i.user.guild_permissions.administrator or (ticket_see_role and ticket_see_role in i.user.roles)
        if not has_permission:
            await i.response.send_message("❌ Nie masz uprawnień do zamknięcia tego ticketa!", ephemeral=True)
            return

        await i.response.send_message("⚠️ Generowanie transkrypcji i zamykanie ticketa...", ephemeral=True)

        transcript_content = f"--- TRANSKRYPT TICKETA: {ticket_channel.name} ---\n\n"
        async for message in ticket_channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            transcript_content += f"[{timestamp}] {message.author}: {message.content}\n"
            for att in message.attachments:
                transcript_content += f"[Załącznik: {att.url}]\n"

        file = discord.File(
            fp=io.BytesIO(transcript_content.encode("utf-8")),
            filename=f"transkrypt-{ticket_channel.name}.txt"
        )

        try:
            await interaction.user.send(
                f"Oto transkrypt z Twojego zamkniętego ticketa na serwerze **{guild.name}**:",
                file=discord.File(
                    fp=io.BytesIO(transcript_content.encode("utf-8")),
                    filename=f"transkrypt-{ticket_channel.name}.txt"
                )
            )
        except Exception:
            pass

        log_channel = discord.utils.get(guild.text_channels, name="transkrypcje")
        if not log_channel:
            log_category = discord.utils.get(guild.categories, name="📁 LOGI TICKETÓW")
            if not log_category:
                log_category = await guild.create_category("📁 LOGI TICKETÓW")
            
            log_overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            log_channel = await guild.create_text_channel(name="transkrypcje", category=log_category, overwrites=log_overwrites)

        try:
            await log_channel.send(
                f"📁 Zamknięto ticket **{ticket_channel.name}**. Założyciel: {interaction.user.mention}. Transkrypt:",
                file=file
            )
        except Exception:
            pass

        import asyncio
        await asyncio.sleep(3)
        await ticket_channel.delete()

    close_btn.callback = close_callback
    close_view.add_item(close_btn)

    await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=close_view)
    await interaction.followup.send(f"✅ Utworzono ticket: {ticket_channel.mention}", ephemeral=True)

# --- MENU WYBORU ---
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Błąd", description="Zgłoś błąd występujący na serwerze", emoji="🛠️", value="Błąd"),
            discord.SelectOption(label="Zgłoś gracza", description="Zgłoś gracza łamiącego regulamin", emoji="🚨", value="Zgłoś gracza"),
            discord.SelectOption(label="Sprawa do administracji", description="Prywatna sprawa lub kontakt", emoji="🛡️", value="Sprawa do administracji"),
            discord.SelectOption(label="Problem z płatnością / sklepem", description="Problemy z zakupionymi rangami", emoji="🛒", value="Problem z płatnością / sklepem"),
            discord.SelectOption(label="Rekrutacja", description="Złóż podanie na członka administracji", emoji="📋", value="Rekrutacja"),
            discord.SelectOption(label="Inne", description="Każda inna sprawa", emoji="❓", value="Inne"),
        ]
        super().__init__(placeholder="Wybierz kategorię zgłoszenia...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        if selected == "Rekrutacja":
            await interaction.response.send_modal(RecruitsModal())
        else:
            await interaction.response.send_modal(StandardTicketModal(selected))

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup-tickets")
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        embed = discord.Embed(
            title="🎟️ CENTRUM POMOCY - TICKETY",
            description="Potrzebujesz pomocy, chcesz zgłosić gracza lub złożyć podanie?\n\n**Wybierz odpowiednią kategorię z menu poniżej**, aby utworzyć prywatny kanał z administracją.",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        if ctx.bot.user.avatar:
            embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        embed.set_footer(text="System Zgłoszeń | Administracja Serwera")

        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))