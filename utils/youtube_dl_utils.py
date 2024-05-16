import yt_dlp

async def get_youtube_url(track_name):
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