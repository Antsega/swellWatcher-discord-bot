import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import discord

class SpotifyManager:
    def __init__(self):
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = Spotify(client_credentials_manager=client_credentials_manager)
        self.track_queue = []

    async def get_artist_top_tracks(self, message):
        try:
            artist_name = message.content[len('!toptracks '):].strip()
            result = self.sp.search(q=f'artist:{artist_name}', type='artist')
            if result['artists']['items']:
                artist = result['artists']['items'][0]
                top_tracks = self.sp.artist_top_tracks(artist['id'])
                response = f"Top tracks for {artist_name}:\n"
                for track in top_tracks['tracks'][:10]:
                    self.track_queue.append(track['uri'])  # Add track URI to queue
                    response += f"{track['name']} - {track['external_urls']['spotify']}\n"
            else:
                response = "Artist not found."
        except Exception as e:
            response = f"An error occurred while processing your request: {str(e)}"
        
        await message.channel.send(response)

    async def get_youtube_url(self, track_name):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'auto',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{track_name}", download=False)
            video_url = info_dict['entries'][0]['url']  # Get the first result's URL
            return video_url

    async def play_next_track(self, message):
        if self.track_queue:
            next_track_uri = self.track_queue.pop(0)  # Get the next track URI
            # You'll need to convert this URI to a playable URL or use a method to play from Spotify (which is generally not supported due to DRM)
            await message.channel.send(f"Playing next track: {next_track_uri}")
        else:
            await message.channel.send("The queue is empty.")

    async def show_queue(self, message):
        if self.track_queue:
            response = "Track queue:\n"
            for track_uri in self.track_queue:
                track_info = self.sp.track(track_uri)
                response += f"{track_info['name']} - {track_info['artists'][0]['name']}\n"
            await message.channel.send(response)
        else:
            await message.channel.send("The queue is empty.")

    async def add_to_queue(self, message):
        try:
            track_name = message.content[len('!queue '):].strip()
            result = self.sp.search(q=f'track:{track_name}', limit=1, type='track')
            if result['tracks']['items']:
                track = result['tracks']['items'][0]
                self.track_queue.append(track['uri'])
                response = f"Added to queue: {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}"
            else:
                response = "Track not found."
        except Exception as e:
            response = f"An error occurred while processing your request: {str(e)}"
        await message.channel.send(response)

    async def play(self, message):
        if not message.guild.voice_client:
            await message.channel.send("I am not connected to a voice channel.")
            return

        if self.track_queue:
            current_track_uri = self.track_queue.pop(0)
            track_info = self.sp.track(current_track_uri)
            track_name = f"{track_info['name']} by {', '.join(artist['name'] for artist in track_info['artists'])}"
            youtube_url = await self.get_youtube_url(track_name)

            # Play the audio from YouTube URL
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }
            YDL_OPTIONS = {'format': 'bestaudio'}

            vc = message.guild.voice_client
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                vc.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

            await message.channel.send(f"Now playing: {track_name}")
        else:
            await message.channel.send("The queue is empty.")
