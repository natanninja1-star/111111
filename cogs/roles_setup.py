import discord
from discord.ext import commands

class RolesSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup-roles", aliases=["role-setup"])
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        """Automatycznie tworzy i układa rangi z odpowiednimi uprawnieniami."""
        guild = ctx.guild

        await ctx.send("⏳ Rozpoczynam tworzenie i układanie rang...", delete_after=10)
        try:
            await ctx.message.delete()
        except:
            pass

        # Definicja uprawnień
        perms_all = discord.Permissions(administrator=True)
        
        perms_mod_chat = discord.Permissions(
            manage_messages=True, 
            kick_members=True, 
            moderate_members=True,
            read_message_history=True,
            view_channel=True
        )
        
        perms_mod_with_tickets = discord.Permissions(
            manage_messages=True, 
            kick_members=True, 
            moderate_members=True,
            manage_channels=True, # Do zarządzania ticketami
            read_message_history=True,
            view_channel=True
        )

        perms_jr_admin = discord.Permissions(
            manage_messages=True, 
            kick_members=True, 
            ban_members=True, 
            moderate_members=True,
            manage_roles=True, # Częściowe zarządzanie rolami
            manage_channels=True,
            read_message_history=True,
            view_channel=True
        )

        perms_empty = discord.Permissions(view_channel=True)

        try:
            # 1. Tworzenie rang od NAJWYŻSZEJ do NAJNIŻSZEJ, 
            # żeby Discord od razu ułożył je w dobrej kolejności hierarchicznej.
            
            # Ranga z gwiazdką (najwyższa)
            role_star = discord.utils.get(guild.roles, name="∗ ∙ ⋆") or await guild.create_role(name="∗ ∙ ⋆", permissions=perms_all, color=discord.Color.gold(), reason="Najwyższa ranga specjalna")
            
            # Właściciel
            role_owner = discord.utils.get(guild.roles, name="ᴛ ∙ wlasciciel") or await guild.create_role(name="ᴛ ∙ wlasciciel", permissions=perms_all, color=discord.Color.red())
            
            # Zarząd
            role_board = discord.utils.get(guild.roles, name="ᴛ ∙ zarzad") or await guild.create_role(name="ᴛ ∙ zarzad", permissions=perms_all, color=discord.Color.from_rgb(255, 100, 100))
            
            # Developer
            role_dev = discord.utils.get(guild.roles, name="ᴛ ∙ developer") or await guild.create_role(name="ᴛ ∙ developer", permissions=perms_all, color=discord.Color.blue())
            
            # Bot
            role_bot = discord.utils.get(guild.roles, name="ᴛ ∙ bot") or await guild.create_role(name="ᴛ ∙ bot", permissions=perms_all, color=discord.Color.lighter_grey())
            
            # HeadAdmin
            role_headadmin = discord.utils.get(guild.roles, name="ᴛ ∙ headadmin") or await guild.create_role(name="ᴛ ∙ headadmin", permissions=perms_all, color=discord.Color.purple())
            
            # Admin
            role_admin = discord.utils.get(guild.roles, name="ᴛ ∙ admin") or await guild.create_role(name="ᴛ ∙ admin", permissions=perms_all, color=discord.Color.magenta())
            
            # Jr Admin
            role_jradmin = discord.utils.get(guild.roles, name="ᴛ ∙ jr admin") or await guild.create_role(name="ᴛ ∙ jr admin", permissions=perms_jr_admin, color=discord.Color.orange())
            
            # Mod
            role_mod = discord.utils.get(guild.roles, name="ᴛ ∙ mod") or await guild.create_role(name="ᴛ ∙ mod", permissions=perms_mod_with_tickets, color=discord.Color.gold())
            
            # Jr Mod
            role_jrmod = discord.utils.get(guild.roles, name="ᴛ ∙ jr mod") or await guild.create_role(name="ᴛ ∙ jr mod", permissions=perms_mod_with_tickets, color=discord.Color.yellow())
            
            # Helper (z ticketami, bez t-helpera)
            role_helper = discord.utils.get(guild.roles, name="ᴛ ∙ helper") or await guild.create_role(name="ᴛ ∙ helper", permissions=perms_mod_with_tickets, color=discord.Color.green())
            
            # T-Helper (mniejsze możliwości, bez ticketów)
            role_thelper = discord.utils.get(guild.roles, name="ᴛ ∙ t-helper") or await guild.create_role(name="ᴛ ∙ t-helper", permissions=perms_mod_chat, color=discord.Color.teal())

            # Role techniczne i dodatkowe
            role_perm_ticket = discord.utils.get(guild.roles, name="perm.ticket.see") or await guild.create_role(name="perm.ticket.see", permissions=perms_empty, color=discord.Color.dark_grey())
            role_perm_antylink = discord.utils.get(guild.roles, name="perm.antylink") or await guild.create_role(name="perm.antylink", permissions=perms_empty, color=discord.Color.dark_grey())
            
            # Etap 2
            role_etap2 = discord.utils.get(guild.roles, name="ᴛ ∙ etap 2") or await guild.create_role(name="ᴛ ∙ etap 2", permissions=perms_empty, color=discord.Color.blurple())
            
            # Gracz (na samym dole)
            role_gracz = discord.utils.get(guild.roles, name="ᴛ ∙ gracz") or await guild.create_role(name="ᴛ ∙ gracz", permissions=perms_empty, color=discord.Color.default())

            await ctx.send("✅ **Pomyślnie utworzono wszystkie rangi w formacie Small Caps z odpowiednimi uprawnieniami!**", delete_after=15)

        except Exception as e:
            await ctx.send(f"❌ Wystąpił błąd podczas tworzenia rang: {e}")

async def setup(bot):
    await bot.add_cog(RolesSetup(bot))