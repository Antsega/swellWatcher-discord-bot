# utils/youtube_dl_utils.py
import yt_dlp

async def get_youtube_url(track_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'default_search': 'ytsearch',
        'extractor_args': {
            'youtube': {
                'player_client': ['web'],
                'player_skip': ['js', 'configs', 'webpage'],
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search and extract in one step
            info = ydl.extract_info(f"ytsearch:{track_name}", download=False)
            if not info or not info.get('entries'):
                return None
            
            # Get the first result
            video = info['entries'][0]
            
            # Get the best audio format URL
            formats = video.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if audio_formats:
                # Sort by audio quality and get the best one
                audio_formats.sort(key=lambda x: x.get('abr', 0) or 0, reverse=True)
                return audio_formats[0]['url']
            
            # Fallback to any format with audio
            for f in formats:
                if f.get('acodec') != 'none':
                    return f['url']
            
            return None
    except Exception as e:
        print(f"Error extracting YouTube URL: {e}")
        return None