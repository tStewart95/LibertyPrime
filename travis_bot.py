import asyncio
import os
import random
import glob

import discord

from discord.ext import commands
import sfx
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
sfx_dir = "/home/tstewart/LibertyPrime/sfx/"

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="Relatively simple music bot example",
    intents=intents,
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_voice_state_update(member, before, after):
    # Ignore events triggered by the bot itself
    if member.id == bot.user.id:
        return
    if not before.channel and after.channel:
        if ("reeland" in member.name) and (random.random() <= 0.1):
            if len(bot.voice_clients) > 0:
                voice_client = bot.voice_clients[0]
                await voice_client.move_to(after.channel)
            else:
                voice_client = await after.channel.connect()
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(f"{sfx_dir}/ralert.mp3")
            )
            voice_client.play(source)


# List SFX
@bot.command(name="getsfx")
async def getsfx(ctx):

    # Loop through and DM pages
    for message in get_sfx_list():
        await ctx.author.send(message)


def get_sfx_list():
    """
    Returns string of sound effects
    """
    messages = []
    messages.append("")
    message_index = 0

    # Searches file system for things under sfx/
    fx = glob.glob("sfx/*")
    messages[0] += "List of Available Sound Effects:\n\n"

    # Sorts by alpahabetical order
    fx = sorted(fx, key=str.lower)

    for sound in fx:

        # DM Length is limited to 2000 characters
        if len(messages[message_index]) >= 1900:
            message_index += 1
            messages.append("==========\n")
            messages[message_index] += "Page " + str(message_index + 1) + "\n"
            messages[message_index] += "==========\n\n"

        # Print out sound name on correct page
        # The 4: here takes off the 'sfx/' from the sound name
        messages[message_index] += "`" + sound[4:] + "`\n"

    return messages


async def main():
    async with bot:
        await bot.add_cog(sfx.sfx(bot))
        await bot.start(TOKEN)


asyncio.run(main())
