import asyncio
import os
import random
import glob
from typing import List

import discord
from discord.ext import commands
import sfx
import ytdl_bot
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
sfx_dir = "/home/tstewart/LibertyPrime/sfx/"
log_dir = "/home/tstewart/LibertyPrime/logs/"

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Relatively simple music bot example",
    intents=intents,
)


@bot.event
async def on_ready():
    if bot.user:
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    else:
        print("Bot user not available yet.")
    print("------")


@bot.event
async def on_voice_state_update(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
):
    if not bot.user or member.id == bot.user.id:
        return
    if not before.channel and after.channel:
        if "tstew" in member.name:
            voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
            if isinstance(voice_client, discord.VoiceClient):
                await voice_client.move_to(after.channel)
            else:
                voice_client = await after.channel.connect()
            if isinstance(voice_client, discord.VoiceClient):
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(f"{sfx_dir}/travischatback.mp3")
                )
                voice_client.play(source)


@bot.command(name="getsfx")
async def getsfx(ctx: commands.Context):
    """DMs a list of available sound effects to the user."""
    # Loop through and DM pages
    for message in get_sfx_list():
        await ctx.author.send(message)
        await asyncio.sleep(0.1)


def get_sfx_list() -> List[str]:
    """
    Returns string of sound effects
    """
    messages = ["List of Available Sound Effects:\n\n"]
    message_index = 0

    # Searches file system for things under sfx/
    fx = sorted(glob.glob(os.path.join(sfx_dir, "*")), key=str.lower)
    messages[0] += "List of Available Sound Effects:\n\n"

    for sound in fx:

        # DM Length is limited to 2000 characters
        if len(messages[message_index]) >= 1900:
            message_index += 1
            messages.append(f"==========\nPage {message_index+1}\n==========\n\n")

        # Print out sound name on correct page
        # The 4: here takes off the 'sfx/' from the sound name
        messages[message_index] += f"`{os.path.basename(sound)}`\n"

    return messages


async def main():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set in the environment.")
    async with bot:
        await bot.add_cog(sfx.sfx(bot))
        await bot.add_cog(ytdl_bot.Music(bot))
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
