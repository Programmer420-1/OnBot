import discord
import os
from discord.ext import commands
from music_updated import music_updated
from configparser import ConfigParser

cogs  = [music_updated]

client = commands.Bot(command_prefix = "//", intents = discord.Intents.all())
client.remove_command('help')

@client.event
async def on_ready():
  print(f"{client.user.name} is ready")

async def setup(): # wait the bot is ready only we add the cog , otherwise self.guild.id will return none
  await client.wait_until_ready()
  client.add_cog(music_updated(client))

#Read config.ini file
config_object = ConfigParser()
config_object.read(r"..\config.ini")

#Get the password
TOKEN = config_object["TOKEN"]

client.loop.create_task(setup())
client.run(TOKEN["TOKEN"])
