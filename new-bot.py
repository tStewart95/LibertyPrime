import os
import glob
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

################
#### CONFIG ####
################
bot = commands.Bot(command_prefix='!')
sfx_dir = "sfx/"

################
##### INIT #####
################
@bot.event
async def on_ready():
    print('Liberty Prime is online.')
    #TODO : Announce
    # Voice a friendly hello if someone is online
    # Check for any users online, if so, pick the room with the most members
    # Announce yourself

################
### COMMANDS ###
################

## Help

## SFX
@bot.command(name='sfx')
async def sfx(ctx, sound : str):

    # Grab the user who sent the command
    user = ctx.message.author
    #Only play if the user is in a voice channel
    if user.voice.channel != None:
        voice_channel = user.voice.channel
        #Find a sound effect that closely matches
        found_sfx = search_sfx(sound)

        if found_sfx != "":
            #Have the bot join the channel
            try:
                vc = await voice_channel.connect()
            except:
                await ctx.send("SFX already playing")
                return
            response = 'Playing `' + found_sfx.split('/')[1] +'`'
            await ctx.send(response)
            vc.play(discord.FFmpegPCMAudio(found_sfx), after=lambda e: bot.loop.create_task(vc.disconnect()))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 2.0

        else:
            await ctx.send('`' + sound +'` not found')

    else:
        await ctx.send(f'{ctx.message.author} is not in a channel.')

def search_sfx(sound_str : str):
    """
        Returns a valid sound, reports when a sound does not work
    """

    f = glob.glob(os.path.join(sfx_dir, sound_str + "*"))
    print(f)
    filepath = ""
    if len(f) >= 1:
        try:
            filepath = random.choice(f)
            print(filepath)
            soundname = filepath.split('/')[-1]
            filepath = os.path.join(sfx_dir, soundname)
        except:
            return ""
        return filepath

    if len(f) < 1:
        return ""

# Add SFX
@bot.command(name='addsfx')
async def addsfx(ctx):
    """
        Uploads media file to sfx/
    """
    #NOTE: This is kind of incredibly insecure, there needs to be better file verification
    #Check that file has a valid .mp3 or .wav extension
    files = ctx.message.attachments
    if len(files) > 0:

        file_type = files[0].filename.split('.')[1]

        if file_type == 'mp3' or file_type == '.wav' or file_type == '.m4a':
            await files[0].save('sfx/' + files[0].filename)
            await ctx.send("Added `" + files[0].filename + "` to avaialble SFX.")

        else:
            await ctx.send("Invalid file type detected.")
    else:
        await ctx.send("No file detected.") 

# List SFX
@bot.command(name='getsfx')
async def getsfx(ctx):
    
    #Loop through and DM pages
    for message in get_sfx_list():
        await ctx.author.send(message)

def get_sfx_list():
    """
        Returns string of sound effects
    """
    messages = []
    messages.append("")
    message_index = 0

    #Searches file system for things under sfx/
    fx = glob.glob("sfx/*")
    messages[0]+="List of Available Sound Effects:\n\n"

    #Sorts by alpahabetical order
    fx = sorted(fx, key=str.lower)

    for sound in fx:

        #DM Length is limited to 2000 characters
        if(len(messages[message_index]) >= 1900):
            message_index+=1
            messages.append("==========\n")
            messages[message_index]+= ("Page " + str(message_index+1) + '\n')
            messages[message_index]+= ("==========\n\n")

        #Print out sound name on correct page
        #The 4: here takes off the 'sfx/' from the sound name
        messages[message_index]+=('`'+ sound[4:] +'`\n')

    return messages

#TODO: Add silly chat bot
## Ask Prime
@bot.command(name='ask')
async def ask(ctx):
    await ctx.send("Functionality not yet added, citizen.")

bot.run(TOKEN)