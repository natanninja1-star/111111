import json
import os
import discord
from discord.ext import commands

WARNINGS_FILE = "warnings.json"

def load_warnings():
    if not os.path.exists(WARNINGS_FILE):
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_warnings(data):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. CZYSZCZENIE WIADOMOŚCI (PURGE) ---
    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        try:
            await ctx.message.delete()
        except:
            pass

        if amount <= 0:
            await ctx.send("❌ Podaj liczbę większą od zera!", delete_after=5)
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 Pomyślnie usunięto **{len(deleted)}** wiadomości.", delete_after=5)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Nie masz uprawnień do zarządzania wiadomościami!", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Użycie: `!clear [liczba]`", delete_after=5)

    # --- 2. SYSTEM OSTRZEŻEŃ (WARN) ---
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Brak powodu"):
        try:
            await ctx.message.delete()
        except:
            pass

        if member == ctx.author:
            await ctx.send("❌ Nie możesz ostrzec samego siebie!", delete_after=5)
            return

        data = load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in data:
            data[guild_id] = {}
        if user_id not in data[guild_id]:
            data[guild_id][user_id] = []

        data[guild_id][user_id].append({
            "moderator": str(ctx.author),
            "reason": reason
        })
        save_warnings(data)

        embed = discord.Embed(
            title="⚠️ OTRZYMAŁEŚ OSTRZEŻENIE",
            description=f"Otrzymałeś warna na serwerze **{ctx.guild.name}**.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Powód", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)

        try:
            await member.send(embed=embed)
        except:
            pass

        await ctx.send(f"✅ Użytkownik {member.mention} został pomyślnie ostrzeżony. Powód: *{reason}*", delete_after=7)

    # --- 3. SPRAWDZANIE WARNÓW ---
    @commands.command(name="warns", aliases=["ostrzeżenia"])
    @commands.has_permissions(kick_members=True)
    async def warns(self, ctx, member: discord.Member):
        try:
            await ctx.message.delete()
        except:
            pass

        data = load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        user_warns = data.get(guild_id, {}).get(user_id, [])

        embed = discord.Embed(
            title=f"📋 Ostrzeżenia użytkownika: {member.name}",
            color=discord.Color.gold()
        )

        if not user_warns:
            embed.description = "Ten użytkownik nie ma żadnych ostrzeżeń."
        else:
            for idx, w in enumerate(user_warns, 1):
                embed.add_field(
                    name=f"Warn #{idx}",
                    value=f"**Powód:** {w['reason']}\n**Przez:** {w['moderator']}",
                    inline=False
                )

        await ctx.send(embed=embed, delete_after=15)

    # --- 4. USUWANIE WARNA (DELWARN) ---
    @commands.command(name="delwarn", aliases=["usuńwarna"])
    @commands.has_permissions(kick_members=True)
    async def delwarn(self, ctx, member: discord.Member, warn_index: int):
        try:
            await ctx.message.delete()
        except:
            pass

        data = load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        user_warns = data.get(guild_id, {}).get(user_id, [])

        if not user_warns or warn_index < 1 or warn_index > len(user_warns):
            await ctx.send("❌ Nie znaleziono warna o takim numerze dla tego użytkownika!", delete_after=5)
            return

        removed = user_warns.pop(warn_index - 1)
        save_warnings(data)

        await ctx.send(f"✅ Usunięto warn nr **{warn_index}** użytkownikowi {member.mention}.", delete_after=7)

    # --- 5. WYCISZENIE (MUTE) ---
    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int, *, reason: str = "Brak powodu"):
        try:
            await ctx.message.delete()
        except:
            pass

        import datetime
        duration = datetime.timedelta(minutes=minutes)
        
        try:
            await member.timeout(duration, reason=reason)
            await ctx.send(f"🔇 Wyciszono użytkownika **{member.name}** na {minutes} minut. Powód: *{reason}*", delete_after=7)
        except Exception:
            await ctx.send("❌ Nie udało się wyciszyć użytkownika.", delete_after=5)

    # --- 6. ODCISZENIE (UNMUTE) ---
    @commands.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        try:
            await ctx.message.delete()
        except:
            pass

        try:
            await member.timeout(None)
            await ctx.send(f"🔊 Odciszono użytkownika **{member.name}**.", delete_after=7)
        except Exception:
            await ctx.send("❌ Nie udało się odciszyć użytkownika.", delete_after=5)

    # --- 7. KICK ---
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Brak powodu"):
        try:
            await ctx.message.delete()
        except:
            pass

        try:
            await member.kick(reason=reason)
            await ctx.send(f"👢 Wyrzucono użytkownika **{member.name}**. Powód: *{reason}*", delete_after=7)
        except Exception:
            await ctx.send("❌ Nie udało się wyrzucić użytkownika.", delete_after=5)

    # --- 8. BAN ---
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Brak powodu"):
        try:
            await ctx.message.delete()
        except:
            pass

        try:
            await member.ban(reason=reason)
            await ctx.send(f"🔨 Zbanowano użytkownika **{member.name}**. Powód: *{reason}*", delete_after=7)
        except Exception:
            await ctx.send("❌ Nie udało się zbanować użytkownika.", delete_after=5)

    # --- 9. UNBAN ---
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name: str):
        try:
            await ctx.message.delete()
        except:
            pass

        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name.lower() == member_name.lower() or str(user.id) == member_name:
                await ctx.guild.unban(user)
                await ctx.send(f"🔓 Odbanowano użytkownika **{user.name}**.", delete_after=7)
                return

        await ctx.send(f"❌ Nie znaleziono zbanowanego użytkownika: `{member_name}`", delete_after=5)

    # --- 10. SLOWMODE (TRYB WOLNY) ---
    @commands.command(name="slowmode", aliases=["powolnyczat"])
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        try:
            await ctx.message.delete()
        except:
            pass

        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Podaj czas w sekundach od 0 do 21600 (6 godzin).", delete_after=5)
            return

        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send("⏱️ Wyłączono tryb powolnego pisania na tym kanale.", delete_after=5)
        else:
            await ctx.send(f"⏱️ Ustawiono tryb powolnego pisania na **{seconds} sekund**.", delete_after=5)

    # --- 11. LOCK (ZABLOKUJ KANAŁ) ---
    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Ten kanał został **zablokowany** przez administrację.", delete_after=7)

    # --- 12. UNLOCK (ODBLOKUJ KANAŁ) ---
    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Ten kanał został **odblokowany**.", delete_after=7)

async def setup(bot):
    await bot.add_cog(Moderation(bot))