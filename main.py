import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import io
import os
import sys

# --- Get token from environment variable ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    print("❌ Error: DISCORD_TOKEN not found in environment variables.")
    sys.exit(1)

# --- Discord setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

@tree.command(name="song", description="Send full audio from YouTube")
@app_commands.describe(query="The name of the song to search")
@discord.app_commands.allowed_contexts(dms=True, private_channels=True, guilds=True)
async def song(interaction: discord.Interaction, query: str):
    await interaction.response.defer()  # in case it takes a while

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    audio_file = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['webpage_url']
            data = ydl.extract_info(url, download=True)
            audio_file = data['requested_downloads'][0]['filepath']

        with open(audio_file, 'rb') as f:
            await interaction.followup.send(
                content=f"🎧 {info['title']}",
                file=discord.File(f, filename=os.path.basename(audio_file))
            )
    finally:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)

bot.run(DISCORD_TOKEN)
