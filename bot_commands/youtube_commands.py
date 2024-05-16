# bot_commands/youtube_commands.py
import discord
import yt_dlp
import asyncio
from utils.youtube_dl_utils import get_youtube_url

class YouTubeManager:
    def __init__(self):
        self.track_queue = []

    async def play(self, ctx, *, video_name):
        youtube_url = await get_youtube_url(video_name)
        self.track_queue.append((youtube_url, video_name))  # Save the URL and video name to the queue
        await ctx.send(f"Added to queue: {video_name}")
        
        if not ctx.guild.voice_client.is_playing():
            await self.play_next_track(ctx)

    async def play_next_track(self, ctx):
        if self.track_queue:
            youtube_url, video_name = self.track_queue.pop(0)  # Get the next track from the queue
        else:
            await ctx.send("The queue is empty.")
            return

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        vc = ctx.guild.voice_client

        def after_play(error):
            coro = self.play_next_track(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f'Failed to play next track: {e}')

        with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            url2 = info['formats'][0]['url']
            source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)  # Correct method to use FFmpegPCMAudio

            vc.play(source, after=after_play)

        await ctx.send(f"Now playing: {video_name}")

    async def skip_track(self, ctx):
        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_playing():
            await ctx.send("No song is currently playing.")
            return

        ctx.guild.voice_client.stop()  # Stop the current track
        await ctx.send("Skipping current track.")
  
        await self.play_next_track(ctx)

    async def clear_queue(self, ctx):
        self.track_queue = []
        await ctx.send("The queue has been cleared.")

    async def show_queue(self, ctx):
        if self.track_queue:
            response = "Track queue:\n"
            for _, video_name in self.track_queue:
                response += f"{video_name}\n"
            await ctx.send(response)
        else:
            await ctx.send("The queue is empty.")

    async def stop(self, ctx):
        if ctx.guild.voice_client:
            self.track_queue = []  # Clear the queue
            ctx.guild.voice_client.stop()  # Stop the current track
            await ctx.send("Stopped playback and cleared the queue.")