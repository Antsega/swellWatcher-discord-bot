1) ## Generate Spotify Keys
- Create .env and SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET or change variable names in /bot_commands/spotify_commands.py
- Spotify ID and Secret Walkthrough: https://developer.spotify.com/documentation/web-api/concepts/apps

2) ## VENV <br>

```python -m venv venv```

activate venv

```source venv/bin/activate```

install dependencies


```pip install -r requirements.txt```

3) ## Discord Key <br>

Walkthrough : https://www.writebots.com/discord-bot-token/

Create DISCORD_DEV_BOT_TOKEN in .env for ./bot.py discord_token var

Invite your bot to server

## Documentation

Spotipy documentation
https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.search

FFmpeg download
https://ffmpeg.org/download.html


__Common Issues__
if you get an ffmpeg error, likely you need to install ffmpeg on your machine 

```
sudo apt update
sudo apt install ffmpeg
``` 

4) ## Add to server

https://discord.com/developers/applications

OAuth2 tab generate new link to add to server

should be able to run  ```ffmpeg```

