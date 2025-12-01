import asyncio
import glob
import os
import random
import re
import discord

from discord.ext import commands, tasks

sfx_dir = "/home/tstewart/LibertyPrime/sfx/"
goodbye_sounds = [
    "goodbyemyn.mp3",
    "latern.mp3",
    "illseeyouinthesequelbitch.m4a",
    "illbegoingnow.mp3",
    "robloxoof.mp3",
]


class sfx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_idle = False
        self._voice_lock = asyncio.Lock()
        self.volume = 1.0  # Default volume (100%)
        self.leave_if_idle.start()

    @commands.command()
    async def search(self, ctx, *, query):
        f = glob.glob(os.path.join(sfx_dir, "*" + query + "*"))
        if len(f) <= 0:
            await ctx.send(f'No sounds found matching "{query}"')
        else:
            await ctx.send(f"Found {len(f)} matching sounds:")
            found_sounds = []
            for file in f:
                found_sounds.append(file.split("/")[-1])
            await ctx.send(f"{"\n".join(found_sounds)}")

    async def search_sfx(self, sound_str: str):
        """
        Returns a valid sound, reports when a sound does not work
        """

        f = glob.glob(os.path.join(sfx_dir, sound_str + "*"))
        filepath = ""
        if len(f) >= 1:
            try:
                filepath = random.choice(f)
                print(filepath)
                soundname = filepath.split("/")[-1]
                filepath = os.path.join(sfx_dir, soundname)
            except:
                return ""
            return filepath

        if len(f) < 1:
            return ""

    @tasks.loop(seconds=6.0)
    async def leave_if_idle(self, ctx):
        if ctx.voice_client is None:
            return
        else:
            goodbye_sound = random.choice(goodbye_sounds)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(f"{sfx_dir}/{goodbye_sound}")
            )
            ctx.voice_client.play(source)
            await ctx.voice_client.disconnect()

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel or moves if already connected."""
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            print("Changing channels...")
            vc = await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a sound from the sfx/ directory.
        query: beginning of the sound file name to play
        """
        self.is_idle = False
        async with self._voice_lock:
            # Move to user's channel if needed
            if ctx.author.voice:
                user_channel = ctx.author.voice.channel
                if ctx.voice_client is None:
                    await user_channel.connect()
                elif ctx.voice_client.channel != user_channel:
                    await ctx.voice_client.move_to(user_channel)
            else:
                await ctx.send("You are not connected to a voice channel.")
                return

            found_sfx = await self.search_sfx(query)
            if found_sfx == "":
                await ctx.send(f"Could not find sound that starts with {query}")
                return
            else:
                print(f"SFX Found: {found_sfx}")
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(found_sfx))
                source.volume = self.volume

                ctx.voice_client.play(source)
                await ctx.send(f"Now playing: {os.path.basename(found_sfx)}")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume permanently until changed again"""
        if not 0 <= volume <= 200:
            return await ctx.send("Volume must be between 0 and 200.")
        self.volume = volume / 100
        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = self.volume
        await ctx.send(f"Changed volume to {volume}% (will persist for future sounds)")

    @commands.command()
    async def stop(self, ctx):
        """Stops the current sound effect"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command()
    async def out(self, ctx):
        """Says goodbye and disconnects the bot from voice"""
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(f"{sfx_dir}/latern.mp3")
        )
        ctx.voice_client.play(source)
        await asyncio.sleep(1.1)
        await ctx.voice_client.disconnect()

    # Add SFX
    @commands.command()
    async def add_sfx(self, ctx):
        """
        Securely uploads media file to sfx/
        Only members with the 'Audio Engineer' role can use this command.
        """

        # Role check
        if not any(
            role.name == "President" or role.name == "Founding Father"
            for role in ctx.author.roles
        ):
            await ctx.send(
                "You need the 'President' or 'Founding Father' role to use this command."
            )
            return

        files = ctx.message.attachments
        if not files:
            await ctx.send("No file detected.")
            return

        file = files[0]
        filename = os.path.basename(file.filename)
        # Only allow safe characters in filenames
        filename = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", filename)
        allowed_exts = (".mp3", ".wav", ".m4a")
        max_size = 5 * 1024 * 1024  # 5 MB

        # Check extension
        if not filename.lower().endswith(allowed_exts):
            await ctx.send("Invalid file type detected. Only mp3, wav, m4a allowed.")
            return

        # Check file size
        if file.size > max_size:
            await ctx.send("File too large. Max size is 5 MB.")
            return

        # Save to sfx_dir
        save_path = os.path.join(sfx_dir, filename)
        if os.path.exists(save_path):
            await ctx.send("A file with that name already exists.")
            return
        try:
            await file.save(save_path)
            await ctx.send(f"Added `{filename}` to available SFX.")
        except Exception as e:
            await ctx.send("Failed to save file.")
            print(f"Error saving file: {e}")

    # Remove SFX
    @commands.command()
    async def remove_sfx(self, ctx, sound_str: str):
        """
        Remove sound from sfx/
        """

        # Role check
        if not any(role.name == "President" for role in ctx.author.roles):
            await ctx.send("You need the 'Audio Engineer' role to use this command.")
            return

        found_files = glob.glob(os.path.join(sfx_dir, sound_str + "*"))
        print(found_files)
        found_sfx = ""
        if len(found_files) == 0:
            await ctx.send(f"Could not find sound that starts with {sound_str}")
        if len(found_files) >= 2:
            await ctx.send(f"Multiple files found, please be more specific:")
            for file in found_files:
                await ctx.send(f"{file.split('/')[-1]}\n")
        elif len(found_files) == 1:
            found_sfx = found_files[0]
            soundname = found_sfx.split("/")[-1]
            found_sfx = os.path.join(sfx_dir, soundname)

            await ctx.send(f"Removing sound: {sound_str}")
            os.remove(found_sfx)

    @play.before_invoke
    @out.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
