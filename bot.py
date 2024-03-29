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
    help_message = None # Initialize help_message 

    # Common Inputs --> message_responses
    if message_content.startswith('!join'):
        await join_voice_channel(message)
    
    elif any(message_content.startswith(cmd) for cmd in ['!dc', '!disconnect', '!leave', '!quit']):
        await leave_voice_channel(message, client)
    
    # Spotify Commands --> spotify_commands
    
    elif message_content.startswith('!toptracks'):
        await spotify_manager.get_artist_top_tracks(message)
    
    elif message_content.startswith('!show q'):
        await spotify_manager.show_queue(message)

    elif message_content.startswith('!q'):
        await spotify_manager.add_to_queue(message)
        
    elif message_content.startswith('!play'):
        await spotify_manager.play(message)

    elif message_content.startswith('!clear'):
        await spotify_manager.clear_queue(message)

    elif message_content.startswith('!autoplay'):
        await spotify_manager.toggle_autoplay(message)

    elif message_content.startswith('!skip'):
        await spotify_manager.skip_track(message)


    elif message_content.startswith('!help'):
        help_message = (
            "**Voice Channel Commands:**\n"
            "`!join` - Join the voice channel.\n"
            "`!dc`, `!disconnect`, `!leave`, `!quit` - Leave the voice channel.\n\n"
            
            "**Music Playback Commands:**\n"
            "`!play` - Play music from the queue or add a track to the queue if something is already playing.\n" #TODO: Does not add to q and autoplay
            "`!skip` - Skip the current track.\n"
            "`!clear` - Clear the queue.\n\n"
            # "!autoplay - Toggle autoplay of similar tracks" #TODO : Doesn't work

            "**Queue Management Commands:**\n"
            "`!q <track name>` - Add a track to the queue.\n"
            "`!show q` - Show the current queue.\n\n"
            
            "**Miscellaneous Commands:**\n"
            "`!toptracks <artist>` - Show top tracks of the artist.\n"
        )
    if help_message: # Need to add this to keep ```data = await state.http.send_message(channel.id, params=params)``` error from calling help_message
        await message.channel.send(help_message)


client.run(discord_token)
