import discord
from discord.ext import commands
import music_updated
#from server import keep_alive

cogs  = [music_updated]

client = commands.Bot(command_prefix = "//", intents = discord.Intents.all())
client.remove_command('help')

for i in range(len(cogs)):
  cogs[i].setup(client)

#keep_alive()
client.run("ODk0MDkxMTQ5MDc2MjA1NTg4.YVk9RQ.jB2mmKt3S4E8H7AMNMxlWEHvGD0")