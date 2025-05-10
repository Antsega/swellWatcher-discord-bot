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
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiesfrombrowser': ('chrome',),  # Use cookies from Chrome for better access
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_client': ['android', 'web'],
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First, search for the video
            search_result = ydl.extract_info(f"ytsearch:{track_name}", download=False)
            if not search_result or not search_result.get('entries'):
                return None
            
            # Get the first result's video ID
            video_id = search_result['entries'][0]['id']
            
            # Now get the actual video info with the ID
            video_info = ydl.extract_info(video_id, download=False)
            if not video_info:
                return None
                
            # Get the best audio format URL
            formats = video_info.get('formats', [])
            
            # Try to get audio-only format first
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                # Sort by audio quality
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