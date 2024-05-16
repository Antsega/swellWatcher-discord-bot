# bot.py
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from bot_commands.message_responses import join_voice_channel, leave_voice_channel
from bot_commands.youtube_commands import YouTubeManager

# Load .env file
load_dotenv()
discord_token = os.getenv('DISCORD_DEV_BOT_TOKEN')

# Instances
intents = discord.Intents.default()
intents.message_content = True

# Set up bot with command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize YouTubeManager
youtube_manager = YouTubeManager()

# Start log
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Common Inputs -> message_responses
@bot.command()
async def join(ctx):
    await join_voice_channel(ctx.message)

@bot.command(aliases=['dc', 'disconnect', 'quit'])
async def leave_voice(ctx):  # original `leave` renamed to `leave_voice`
    await leave_voice_channel(ctx.message, bot)

# YouTube Commands -> youtube_commands
@bot.command(name="play")
async def play_youtube(ctx, *, video_name: str):
    await youtube_manager.play(ctx, video_name=video_name)

@bot.command(name="skip")
async def skip(ctx):
    await youtube_manager.skip_track(ctx)

@bot.command(name="clear")
async def clear(ctx):
    await youtube_manager.clear_queue(ctx)

@bot.command(name="showq")
async def show_queue(ctx):
    await youtube_manager.show_queue(ctx)

@bot.command(name="stop")
async def stop(ctx):
    await youtube_manager.stop(ctx)

# Custom help
@bot.command(name="bothelp")
async def show_help(ctx):
    help_message = (
        "**Voice Channel Commands:**\n"
        "`!join` - Join the voice channel.\n"
        "`!dc`, `!disconnect`, `!leave_voice`, `quit` - Leave the voice channel.\n\n"  # updated command and aliases
        
        "**YouTube Commands:**\n"
        "`!play <video name>` - Play a YouTube video by search term.\n"
        "`!skip` - Skip the current track.\n"
        "`!clear` - Clear the queue.\n"
        "`!showq` - Show the current queue.\n"
        "`!stop` - Stop playback and clear the queue.\n\n"
        
        "`!bothelp` - Show this help message.\n"
    )
    await ctx.send(help_message)

bot.run(discord_token)