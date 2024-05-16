import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import discord
import asyncio
from utils.youtube_dl_utils import get_youtube_url
import yt_dlp

class SpotifyManager:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = Spotify(client_credentials_manager=client_credentials_manager)
        self.track_queue = []
        self.autoplay = False

    async def get_artist_top_tracks(self, message):
        # Extract artist name and perform search
        artist_name = message.content[len('!toptracks '):].strip()
        result = self.sp.search(q=f'artist:{artist_name}', type='artist')
        
        # Respond with top tracks or not found message
        if not result['artists']['items']:
            await message.channel.send("Artist not found.")
            return
        
        artist = result['artists']['items'][0]
        top_tracks = self.sp.artist_top_tracks(artist['id'])
        response = f"Top tracks for {artist_name}:\n"
        for track in top_tracks['tracks'][:10]:
            self.track_queue.append(track['uri'])  # Add track URI to queue
            response += f"{track['name']} - {track['external_urls']['spotify']}\n"
        await message.channel.send(response)

    async def skip_track(self, message):
        if not message.guild.voice_client or not message.guild.voice_client.is_playing():
            await message.channel.send("No song is currently playing.")
            return

        message.guild.voice_client.stop()  # Stop the current track
        await message.channel.send("Skipping current track.")
  
        await self.play_next_track(message)

    async def play_next_track(self, message):
        if self.track_queue:
            next_track_uri = self.track_queue.pop(0)
            await self.play_track(next_track_uri, message)
        elif self.autoplay:
            # Implement autoplay logic here
            pass
        else:
            await message.channel.send("The queue is empty.")

    async def toggle_autoplay(self, message):
        self.autoplay = not self.autoplay
        status = "on" if self.autoplay else "off"
        await message.channel.send(f"Autoplay is now {status}.")

    async def show_queue(self, message):
        if self.track_queue:
            response = "Track queue:\n"
            for track_uri in self.track_queue:
                track_info = self.sp.track(track_uri)
                response += f"{track_info['name']} - {track_info['artists'][0]['name']}\n"
            await message.channel.send(response)
        else:
            await message.channel.send("The queue is empty.")

    async def add_to_queue(self, message, track_name=None):
        if not track_name:
            track_name = message.content[len('!q '):].strip()
        
        result = self.sp.search(q=f'track:{track_name}', limit=1, type='track')
        if result['tracks']['items']:
            track = result['tracks']['items'][0]
            self.track_queue.append(track['uri'])
            response = f"Added to queue: {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}"
        else:
            response = "Track not found."

        await message.channel.send(response)

    async def clear_queue(self, message):
        self.track_queue = []
        await message.channel.send("The queue has been cleared.")

    async def play(self, message):
        if not message.guild.voice_client:
            await message.channel.send("I am not connected to a voice channel.")
            return

        if message.guild.voice_client.is_playing():
            await self.add_to_queue(message, message.content[len('!play '):].strip())
            return

        if self.track_queue:
            track_uri = self.track_queue.pop(0)
            await self.play_track(track_uri, message)
        else:
            await message.channel.send("The queue is empty.")

    async def play_track(self, track_uri, message):
        track_info = self.sp.track(track_uri)
        track_name = f"{track_info['name']} by {', '.join(artist['name'] for artist in track_info['artists'])}"
        youtube_url = await get_youtube_url(track_name)

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        YDL_OPTIONS = {'format': 'bestaudio'}

        vc = message.guild.voice_client

        def after_play(error):
            coro = self.play_next_track(message)
            fut = asyncio.run_coroutine_threadsafe(coro, message.guild.voice_client.loop)
            try:
                fut.result()
            except Exception as e:
                print(f'Failed to play next track: {e}')

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source, after=after_play)

        await message.channel.send(f"Now playing: {track_name}")