import discord
from discord.ext import commands
from music_updated import music_updated
#from server import keep_alive

cogs  = [music_updated]

client = commands.Bot(command_prefix = "//", intents = discord.Intents.all())
client.remove_command('help')

@client.event
async def on_ready():
  print(f"{client.user.name} is ready")

async def setup(): # wait the bot is ready only we add the cog , otherwise self.guild.id will return none
  await client.wait_until_ready()
  client.add_cog(music_updated(client))

client.loop.create_task(setup())
#keep_alive()
client.run("ODk0MDkxMTQ5MDc2MjA1NTg4.YVk9RQ.jB2mmKt3S4E8H7AMNMxlWEHvGD0")