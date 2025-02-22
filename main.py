from keep_alive import keep_alive

keep_alive()  # Startet den Webserver

import discord
from discord.ext import commands
import os

# Erforderliche Intents aktivieren
intents = discord.Intents.default()
intents.message_content = True   
intents.voice_states = True      
intents.members = True           

# Bot-Objekt erstellen
bot = commands.Bot(command_prefix="!", intents=intents)

# Liste der Sprachkanäle (Funk1 - Funk10)
ALLOWED_CHANNELS = [f"Funk{i}" for i in range(1, 11)]

# Debugging: Startmeldung
@bot.event
async def on_ready():
    print(f"✅ Bot ist eingeloggt als {bot.user}")
    print("🔍 Move-Panel für Kanäle:", ", ".join(ALLOWED_CHANNELS))

# Button-Klasse für das Move-Panel
class MoveButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  
        for channel_name in ALLOWED_CHANNELS:
            self.add_item(MoveButton(channel_name))  

# Button-Klasse für einzelne Buttons
class MoveButton(discord.ui.Button):
    def __init__(self, channel_name: str):
        super().__init__(label=channel_name, style=discord.ButtonStyle.primary)
        self.channel_name = channel_name

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user

        # Prüfen, ob der Nutzer in einem Sprachkanal ist
        if not member.voice:
            await interaction.response.send_message("❌ Du bist in keinem Sprachkanal!", ephemeral=True, delete_after=5)
            return

        # Ziel-Sprachkanal suchen
        target_channel = discord.utils.get(interaction.guild.voice_channels, name=self.channel_name)
        if not target_channel:
            await interaction.response.send_message(f"❌ Kanal `{self.channel_name}` nicht gefunden.", ephemeral=True, delete_after=5)
            return

        # **Hier wird der Move erzwungen, auch wenn der Nutzer keine Rechte für den Kanal hat**
        if not interaction.guild.me.guild_permissions.move_members:
            await interaction.response.send_message("❌ Ich habe nicht die Berechtigung, Mitglieder zu verschieben!", ephemeral=True, delete_after=5)
            return

        try:
            # Nutzer in den Zielkanal moven
            await member.move_to(target_channel)
            await interaction.response.send_message(f"✅ Du wurdest in `{target_channel.name}` verschoben!", ephemeral=True, delete_after=5)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Ich habe nicht die Berechtigung, dich zu moven.", ephemeral=True, delete_after=5)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Fehler: `{e}`", ephemeral=True, delete_after=5)

# Befehl, um das Move-Panel zu senden
@bot.command()
async def move_panel(ctx):
    await ctx.send("🔊 **Gehe in den Warteraum und klicke auf einen Button um in den Funkkanal verschoben zu werden!**", view=MoveButtons())




# Starte den Bot (Token hier einfügen)
bot.run(os.environ["DC_Token"])
