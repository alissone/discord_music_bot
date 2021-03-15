import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord_config import CMD_PREFIX, DESCRIPTION, TOKEN

# You need to have a discord_config.py
# TOKEN = "" # The token you got when you created a new bot
# CMD_PREFIX = "$"   # The command prefix (e.g. so you can call $command_name)
# DESCRIPTION = ""  # The description (optional)

# Updated to work with the latest version of discord.py (march 2021)
# Use $join to join the voice channel a user is currently in and $exit to leave

# TODO: Create a Dockerfile and requirements.txt to run it via Docker
# TODO: Allow exiting and rejoining silently in case the user joins twice
# TODO: Gracefully stop when leaving

bot = commands.Bot(command_prefix=CMD_PREFIX, description=DESCRIPTION)
playing = False

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("a voice channel test."),
        afk=False,
    )


@bot.command(aliases=["join_voice", "voice"])
async def join(ctx):
    try:
        destination = ctx.author.voice.channel
        print(f"{ctx.author} called me to {destination} channel!")
        # await ctx.send(f"{ctx.author} called me to {destination} channel!", delete_after = 5.0)

        ctx.voice_state.voice = await destination.connect()
        print(f"Joined {ctx.author.voice.channel} Voice Channel")
        # await ctx.send(f"Joined {ctx.author.voice.channel} Voice Channel", delete_after = 5.0)

    except Exception:
        pass


@bot.command(name="leave", pass_context=True)
async def leave(message):
    ctx = await bot.get_context(message)

    voice_client = ctx.voice_client
    if voice_client:
        print("Bot left the voice channel")
        await voice_client.disconnect()
    else:
        print("Bot was not in channel")



from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
import asyncio

async def test(url, message):
    ydl_opts = {
        'verbose': True,
        'format': 'bestaudio/best',
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        is_link = url.startswith("http") # else is considered a search term

        if is_link:
            song_info = ydl.extract_info(url, download=False)
        else:
            song_info = ydl.extract_info("ytsearch: " + url, download=False)

        voice = bot.voice_clients[0]

        playing = True

        # TODO: Select the right format dinamically instead of [-1]
        # TODO: Allow user to select the video instead of picking first
        if is_link:
            voice.play(discord.FFmpegPCMAudio(song_info["formats"][-1]["url"]))
        else:
            voice.play(discord.FFmpegPCMAudio(song_info["entries"][0]["formats"][-1]["url"]))

        voice.source = discord.PCMVolumeTransformer(message.guild.voice_client.source)
        voice.source.volume = 1

@bot.command(name="stop", pass_context=True)
async def stop(message):
    ctx = await bot.get_context(message)
    playing = False

    voice = get(bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel

    # TODO: Use messages like this to any commands
    if voice and voice.is_playing():
        await ctx.send("Stop!", delete_after = 5.0)
        voice.stop()

    print("Stopping player...")


@bot.event
async def on_message(msg):
    if msg.content.startswith(f"{CMD_PREFIX}join"):
        playing = False
        await join(msg)

    if msg.content.startswith(f"{CMD_PREFIX}exit"):
        await leave(msg)

    if msg.content.startswith(f"{CMD_PREFIX}stop"):
        await stop(msg)


    if msg.content.startswith(f"{CMD_PREFIX}play"):
        link_or_search = msg.content.split(f"{CMD_PREFIX}play")[-1].strip()
        await test(link_or_search, msg)


bot.run(TOKEN)
