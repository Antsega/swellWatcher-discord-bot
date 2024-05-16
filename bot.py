import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from bot_commands.message_responses import join_voice_channel, leave_voice_channel
from bot_commands.spotify_commands import SpotifyManager
from bot_commands.youtube_commands import YouTubeManager

# Load .env file
load_dotenv()
discord_token = os.getenv('DISCORD_DEV_BOT_TOKEN')

# Instances
intents = discord.Intents.default()
intents.message_content = True

# Set up bot with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Managers
spotify_manager = SpotifyManager()
youtube_manager = YouTubeManager()

# Start log
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Common Inputs --> message_responses
@bot.command()
async def join(ctx):
    await join_voice_channel(ctx.message)

@bot.command(aliases=['dc', 'disconnect', 'quit'])
async def leave_voice(ctx):  # original `leave` renamed to `leave_voice`
    await leave_voice_channel(ctx.message, bot)

# Spotify Commands --> spotify_commands
@bot.command(name="spot_toptracks")
async def toptracks(ctx, *, artist: str):
    ctx.message.content = f"!spot_toptracks {artist}"
    await spotify_manager.get_artist_top_tracks(ctx.message)

@bot.command(name="spot_showq")
async def show_queue(ctx):
    await spotify_manager.show_queue(ctx.message)

@bot.command(name="spot_q")
async def add_to_queue(ctx, *, track_name: str):
    await spotify_manager.add_to_queue(ctx.message, track_name)

@bot.command(name="spot_play")
async def play(ctx):
    await spotify_manager.play(ctx.message)

@bot.command(name="spot_clear")
async def clear(ctx):
    await spotify_manager.clear_queue(ctx.message)

@bot.command(name="spot_autoplay")
async def autoplay(ctx):
    await spotify_manager.toggle_autoplay(ctx.message)

@bot.command(name="spot_skip")
async def skip(ctx):
    await spotify_manager.skip_track(ctx.message)

# YouTube Commands --> youtube_commands
@bot.command(name="yt_play")
async def play_youtube(ctx, *, video_name: str):
    await youtube_manager.play_youtube(ctx, video_name=video_name)

# Custom help
@bot.command(name="bothelp") 
async def show_help(ctx):
    help_message = (
        "**Voice Channel Commands:**\n"
        "`!join` - Join the voice channel.\n"
        "`!dc`, `!disconnect`, `!leave_voice`, `quit` - Leave the voice channel.\n\n" 
        
        "**Spotify Commands (Prefixed with `spot_`):**\n"
        "`!spot_play` - Play music from the queue or add a track to the queue if something is already playing.\n"
        "`!spot_skip` - Skip the current track.\n"
        "`!spot_clear` - Clear the queue.\n"
        "`!spot_q <track name>` - Add a track to the queue.\n"
        "`!spot_showq` - Show the current queue.\n"
        "`!spot_toptracks <artist>` - Show top tracks of the artist.\n"
        "`!spot_autoplay` - Toggle autoplay of similar tracks.\n"
        
        "**YouTube Commands (Prefixed with `yt_`):**\n"
        "`!yt_play <video name>` - Play a YouTube video by search term.\n"
        
        "`!bothelp` - Show this help message.\n"
    )
    await ctx.send(help_message)

bot.run(discord_token)