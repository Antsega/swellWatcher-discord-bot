# bot_commands/youtube_commands.py
import discord
import asyncio
from utils.youtube_dl_utils import get_youtube_url

class YouTubeManager:
    def __init__(self):
        self.track_queue = []
        self.current_track = None
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -b:a 192k',
        }

    async def _ensure_voice_client(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return False

        if not ctx.guild.voice_client:
            try:
                await ctx.author.voice.channel.connect()
            except Exception as e:
                await ctx.send(f"Failed to join voice channel: {str(e)}")
                return False
        return True

    async def play(self, ctx, *, video_name):
        if not await self._ensure_voice_client(ctx):
            return

        youtube_url = await get_youtube_url(video_name)
        if not youtube_url:
            await ctx.send("Sorry, I couldn't find that video or extract its audio.")
            return

        self.track_queue.append((youtube_url, video_name))
        await ctx.send(f"Added to queue: {video_name}")
        
        if not ctx.guild.voice_client.is_playing():
            await self.play_next_track(ctx)

    async def play_next_track(self, ctx):
        if not self.track_queue:
            self.current_track = None
            await ctx.send("The queue is empty.")
            return

        youtube_url, video_name = self.track_queue.pop(0)
        self.current_track = video_name

        def after_play(error):
            if error:
                print(f'Error during playback: {error}')
            coro = self.play_next_track(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f'Failed to play next track: {e}')

        try:
            source = discord.FFmpegPCMAudio(youtube_url, **self.FFMPEG_OPTIONS)
            ctx.guild.voice_client.play(source, after=after_play)
            await ctx.send(f"Now playing: {video_name}")
        except Exception as e:
            print(f'Error playing audio: {e}')
            await ctx.send("Sorry, there was an error playing the audio. Skipping to next track.")
            await self.play_next_track(ctx)

    async def skip_track(self, ctx):
        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_playing():
            await ctx.send("No song is currently playing.")
            return

        ctx.guild.voice_client.stop()
        await ctx.send("Skipping current track.")
        await self.play_next_track(ctx)

    async def clear_queue(self, ctx):
        self.track_queue = []
        self.current_track = None
        await ctx.send("The queue has been cleared.")

    async def show_queue(self, ctx):
        if not self.track_queue and not self.current_track:
            await ctx.send("The queue is empty.")
            return

        response = []
        if self.current_track:
            response.append(f"Now playing: {self.current_track}")
        
        if self.track_queue:
            if response:
                response.append("")  # Add a blank line if we have a current track
            response.append("Track queue:")
            for i, (_, video_name) in enumerate(self.track_queue, 1):
                response.append(f"{i}. {video_name}")
        
        await ctx.send("\n".join(response))

    async def stop(self, ctx):
        if ctx.guild.voice_client:
            self.track_queue = []
            self.current_track = None
            ctx.guild.voice_client.stop()
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Stopped playback, cleared the queue, and disconnected from voice channel.")