async def join_voice_channel(message):
    channel = message.author.voice.channel
    if channel:
        await channel.connect()
    else:
        await message.channel.send("You are not in a voice channel.")

async def leave_voice_channel(message, client):
    if message.guild.voice_client is not None:
        await message.guild.voice_client.disconnect()
    else:
        await message.channel.send("I am not in a voice channel.")