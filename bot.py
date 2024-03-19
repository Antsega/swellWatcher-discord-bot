import discord
import os
from dotenv import load_dotenv
from bot_commands.message_responses import *
from bot_commands.spotify_commands import SpotifyManager

# load .env file
load_dotenv()
discord_token = os.getenv('DISCORD_DEV_BOT_TOKEN')

# instances
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize the SpotifyManager
spotify_manager = None

# Start log
@client.event
async def on_ready():
    global spotify_manager
    print(f'We have logged in as {client.user}')
    spotify_manager = SpotifyManager()  # Instantiate the SpotifyManager

# Check Messages
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    message_content = message.content.lower()  # lower all input

    if message_content.startswith('!join'):
        await join_voice_channel(message)
    
    elif any(message_content.startswith(cmd) for cmd in ['!dc', '!disconnect', '!leave', '!quit']):
        await leave_voice_channel(message, client)
    
    elif message_content.startswith('!toptracks'):
        await spotify_manager.get_artist_top_tracks(message)

    elif message_content.startswith('!playnext'):
        await spotify_manager.play_next_track(message)
    
    elif message_content.startswith('!showqueue'):
        await spotify_manager.show_queue(message)

    elif message_content.startswith('!queue'):
        await spotify_manager.add_to_queue(message)
        
    elif message_content.startswith('!play'):
        await spotify_manager.play(message)

client.run(discord_token)
