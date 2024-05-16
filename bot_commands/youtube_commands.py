import discord
import yt_dlp
from utils.youtube_dl_utils import get_youtube_url

class YouTubeManager:
    async def play_youtube(self, ctx, *, video_name):
        if not ctx.guild.voice_client:
            await ctx.send("I am not connected to a voice channel.")
            return

        youtube_url = await get_youtube_url(video_name)

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        vc = ctx.guild.voice_client

        def after_play(error):
            if error:
                print(f'Player error: {error}')

        with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            url2 = info['formats'][0]['url']
            source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)

            vc.play(source, after=after_play)

        await ctx.send(f"Now playing: {video_name}")