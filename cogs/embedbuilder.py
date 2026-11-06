import discord
from discord.ext import commands
from discord.ui import View, Modal, TextInput, Select

# --- 1. FORMULARZ DO WPISANIA TREŚCI (Z EMOTKAMI) ---
class EmbedContentModal(Modal):
    def __init__(self, target_channel: discord.TextChannel, text_style: str, formatting_type: str, emoji_choice: str):
        super().__init__(title="Kreator Embedu - Treść i Tytuł")
        self.target_channel = target_channel
        self.text_style = text_style
        self.formatting_type = formatting_type
        self.emoji_choice = emoji_choice

        self.embed_title = TextInput(
            label="Tytuł Ogłoszenia",
            placeholder="Wpisz tytuł...",
            required=True,
            max_length=100
        )
        
        self.embed_desc = TextInput(
            label="Główny Tekst / Opis Ogłoszenia",
            style=discord.TextStyle.paragraph,
            placeholder="Wpisz treść... Użyj | do zrobienia nowych sekcji.",
            required=True,
            max_length=1000
        )

        self.footer_text = TextInput(
            label="Stopka (Footer)",
            placeholder="Podpis pod ogłoszeniem (opcjonalnie)",
            required=False,
            max_length=100
        )

        self.add_item(self.embed_title)
        self.add_item(self.embed_desc)
        self.add_item(self.footer_text)

    async def on_submit(self, interaction: discord.Interaction):
        # Używamy wybranej z GUI emotki wokół tytułu
        title = f"{self.emoji_choice} {self.embed_title.value.strip()} {self.emoji_choice}"
        
        raw_desc = self.embed_desc.value.strip()
        formatted_content = raw_desc.replace(" | ", "\n> 🔹 ")

        if self.text_style == "italic":
            description = f"*{formatted_content}*"
        elif self.text_style == "code":
            description = f"```\n{formatted_content}\n```"
        elif self.text_style == "underline":
            description = f"__{formatted_content}__"
        else:  # Domyślnie bold (pogrubienie **)
            description = f"**{formatted_content}**"

        if self.formatting_type == "uppercase":
            description = description.upper()
        elif self.formatting_type == "quote":
            description = f"> {description}"

        footer = self.footer_text.value.strip() if self.footer_text.value else "System Ogłoszeń | Minecraft Server"

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.from_rgb(88, 101, 242)
        )
        
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
            
        embed.set_footer(text=footer)

        try:
            await self.target_channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Pomyślnie wysłano embed na kanał {self.target_channel.mention}!", ephemeral=True)
        except Exception:
            await interaction.response.send_message("❌ Błąd: Bot nie ma uprawnień do wysyłania wiadomości na ten kanał.", ephemeral=True)

# --- 2. MENU WYBORU STYLU TEKSTU ---
class StyleSelect(Select):
    def __init__(self, target_channel):
        options = [
            discord.SelectOption(label="Pogrubienie (Bold)", description="Pogrubia cały tekst (**tekst**)", emoji="🅱️", value="bold"),
            discord.SelectOption(label="Kursywa (Italic)", description="Pochyla tekst (*tekst*)", emoji="🇮", value="italic"),
            discord.SelectOption(label="Kod (Code block)", description="Umieszcza w ramce kodu (```tekst```)", emoji="💻", value="code"),
            discord.SelectOption(label="Podkreślenie (Underline)", description="Podkreśla tekst (__tekst__)", emoji="🇺", value="underline"),
        ]
        super().__init__(placeholder="Krok 2: Wybierz styl tekstu...", min_values=1, max_values=1, options=options)
        self.target_channel = target_channel

    async def callback(self, interaction: discord.Interaction):
        chosen_style = self.values[0]
        await interaction.response.edit_message(
            content=f"Wybrany styl: **{chosen_style}**. Teraz wybierz dodatkowy efekt tekstowy:",
            view=ExtraFormatView(self.target_channel, chosen_style)
        )

class StyleSelectView(View):
    def __init__(self, target_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.add_item(StyleSelect(target_channel))

# --- 3. DODATKOWE OPCJE FORMATOWANIA ---
class ExtraSelect(Select):
    def __init__(self, target_channel, text_style):
        options = [
            discord.SelectOption(label="Brak dodatków", description="Zwykły sformatowany tekst", emoji="✨", value="none"),
            discord.SelectOption(label="Wielkie litery (UPPERCASE)", description="Zamienia cały tekst na wielkie litery", emoji="🔠", value="uppercase"),
            discord.SelectOption(label="Styl cytatu (>)", description="Dodaje znak cytatu na początku", emoji="💬", value="quote"),
        ]
        super().__init__(placeholder="Krok 3: Wybierz efekt dodatkowy...", min_values=1, max_values=1, options=options)
        self.target_channel = target_channel
        self.text_style = text_style

    async def callback(self, interaction: discord.Interaction):
        formatting_type = self.values[0]
        # Po efekcie przechodzimy do wyboru emotek
        await interaction.response.edit_message(
            content=f"Wybrany efekt: **{formatting_type}**. Ostatni krok przed formularzem – wybierz ozdobne emotki:",
            view=EmojiSelectView(self.target_channel, self.text_style, formatting_type)
        )

class ExtraFormatView(View):
    def __init__(self, target_channel: discord.TextChannel, text_style: str):
        super().__init__(timeout=None)
        self.add_item(ExtraSelect(target_channel, text_style))

# --- 4. WYBÓR EMOTIKON (NOWOŚĆ) ---
class EmojiSelect(Select):
    def __init__(self, target_channel, text_style, formatting_type):
        options = [
            discord.SelectOption(label="Gwiazdki i blask", description="👀 Użyj gwiazdek", emoji="👀", value="👀"),
            discord.SelectOption(label="Ogień", description="🔥 Użyj płomieni", emoji="🔥", value="🔥"),
            discord.SelectOption(label="Rakieta", description="🚀 Użyj rakiet", emoji="🚀", value="🚀"),
            discord.SelectOption(label="Ostrzeżenie / Ważne", description="⚠️ Użyj wykrzykników", emoji="⚠️", value="⚠️"),
            discord.SelectOption(label="Diament", description="💎 Użyj diamentów", emoji="💎", value="💎"),
        ]
        super().__init__(placeholder="Krok 4: Wybierz ozdobne emotki...", min_values=1, max_values=1, options=options)
        self.target_channel = target_channel
        self.text_style = text_style
        self.formatting_type = formatting_type

    async def callback(self, interaction: discord.Interaction):
        chosen_emoji = self.values[0]
        # Otwieramy ostateczny formularz tekstowy z przekazaną emotką
        await interaction.response.send_modal(EmbedContentModal(self.target_channel, self.text_style, self.formatting_type, chosen_emoji))

class EmojiSelectView(View):
    def __init__(self, target_channel, text_style, formatting_type):
        super().__init__(timeout=None)
        self.add_item(EmojiSelect(target_channel, text_style, formatting_type))

# --- 5. WYBÓR KANAŁU ---
class ChannelSelect(Select):
    def __init__(self, options):
        super().__init__(placeholder="Krok 1: Wybierz kanał docelowy...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        target_channel = interaction.guild.get_channel(channel_id)
        
        if not target_channel:
            await interaction.response.send_message("❌ Nie znaleziono kanału!", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=f"Kanał docelowy: **#{target_channel.name}**. Teraz wybierz styl tekstu:",
            view=StyleSelectView(target_channel)
        )

class ChannelSelectView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=None)
        options = []
        for channel in guild.text_channels[:25]:
            options.append(discord.SelectOption(label=channel.name, description=f"Wysyłaj na #{channel.name}", emoji="📝", value=str(channel.id)))
        
        if not options:
            options.append(discord.SelectOption(label="Brak kanałów", value="none"))
        self.add_item(ChannelSelect(options))

# --- 6. GŁÓWNY PANEL STARTOWY ---
class EmbedPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Stwórz Customowe Ogłoszenie (GUI)", style=discord.ButtonStyle.primary, emoji="🎨", custom_id="start_embed_builder")
    async def open_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Wybierz kanał, na którym ma pojawić się ogłoszenie:", 
            view=ChannelSelectView(interaction.guild), 
            ephemeral=True
        )

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup-embed")
    @commands.has_permissions(administrator=True)
    async def setup_embed(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        embed = discord.Embed(
            title="📣 INTERAKTYWNY KREATOR EMBEDÓW",
            description="Kliknij przycisk poniżej, aby uruchomić zaawansowane GUI.\n\n**Co zrobisz w tym menu?**\n• Wybierzesz kanał z listy\n• Wybierzesz styl tekstu i dodatkowe efekty\n• **Wybierzesz ozdobne emotki** do oprawy tytułu\n• Wpiszesz tytuł i treść w formularzu",
            color=discord.Color.from_rgb(88, 101, 242)
        )
        if ctx.bot.user.avatar:
            embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        embed.set_footer(text="Panel Administratora")

        await ctx.send(embed=embed, view=EmbedPanelView())

async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))