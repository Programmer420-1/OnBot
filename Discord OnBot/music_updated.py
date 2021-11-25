import discord
from discord.ext import commands
import youtube_dl
import pafy
import threading
import time

command_list = [
  '//help => Get help on the list of commands and its functionality',
  '//join => Invite On Bot into current voice channel',
  '//play [song_name] => Start playing songs in queue',
  '//pause => Pause the player',
  '//resume => Resume the player',
  '//skip => Skip to the next song in queue',
  '//remove [index] => Remove specific songs from queue',
  '//queue => Display a list of songs which are currenly in queue',
  '//disconnect => Disconnect On Bot from the voice channel'
]

queue = {}
nowPlaying = {}

class music_updated(commands.Cog):
  nextSong = False
  FFMPEG_OPTIONS = {
      'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options' : '-vn'
      }
  YDL_OPTIONS = {
    'format' : 'bestaudio',
    'quiet': True,
    'forcetitle' : True,
  }

  ## constructor
  def __init__(self,client):
    print("Setting up bot")
    self.client = client
    self.Setup()

    # start new thread for checking new servers added [Always running until program terminated]
    t = threading.Thread(target=self.checkNewServer, daemon=True)
    t.start()

  ## bot set up
  def Setup(self):
    global queue
    global nowPlaying
    print("running set up method")
    for guild in self.client.guilds:
      # print(str(guild.id)+" << guild id")
      queue[guild.id] = []
      nowPlaying[guild.id] = None

  # check server which bot is in every 0.5s
  def checkNewServer(self):
    global queue
    global nowPlaying
    new_guild_list = []
    while True:
      for guild in self.client.guilds:
        new_guild_list.append(guild.id)
      current_guild_list = list(queue.keys())

      if new_guild_list[-1] not in current_guild_list and len(current_guild_list) < len(new_guild_list):
        queue[new_guild_list[-1]] = []
        nowPlaying[new_guild_list[-1]] = None
        print(queue.keys())
      time.sleep(0.5)

  ## check songs in queue
  async def check_queue(self,ctx):
      global queue
      global nowPlaying
      ## if there is songs in queue
      if len(queue[ctx.guild.id]) > 0:
        ## stop the player first
        ctx.voice_client.stop()
        ## play next songs in queue
        url,nowPlaying[ctx.guild.id] =  queue[ctx.guild.id][0].split("#+-+#")[1],queue[ctx.guild.id][0].split("#+-+#")[0]
        del queue[ctx.guild.id][0]
        await self.play_song(ctx,url,nowPlaying[ctx.guild.id])
      ## update nowplaying info after playing last song
      else:
        nowPlaying[ctx.guild.id] = None

  async def search(self, ctx, song=None):
    ## retrieve info of songs by song title
    info = await self.client.loop.run_in_executor(None,lambda : youtube_dl.YoutubeDL(self.YDL_OPTIONS).extract_info(f"ytsearch:{song}",download = False,ie_key = "YoutubeSearch"))
    if len(info["entries"]) == 0:
      return None
    else:
      return [entry["webpage_url"] for entry in info["entries"]]
  
  async def play_song(self,ctx,song,song_name = None):
    ## takes in url as argument
    if song_name == None:
      await ctx.send("Now Playing: [Error]")
    else:
      await ctx.send(f"Now Playing: {song_name}")
      url = pafy.new(song).getbestaudio().url
      ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after = lambda error: self.client.loop.create_task(self.check_queue(ctx)))
      ctx.voice_client.source.volume = 0.75

  ## join voice channel
  @commands.command()
  async def join(self,ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    #if bot is not in voice channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    #not a voice channel -> move over to a voice channel
    else:
      await ctx.voice_client.move_to(voice_channel)
    
  
  ## disconnect bot from voice channel
  @commands.command()
  async def disconnect(self,ctx):
    global queue
    global nowPlaying
    try:
      queue[ctx.guild.id] = []
      nowPlaying[ctx.guild.id] = None
      ctx.voice_client.stop()
      await ctx.voice_client.disconnect()
    except:
      await ctx.send("Something went wrong! Please try again")
  
  ## pause the song
  @commands.command()
  async def pause(self,ctx):
    if ctx.voice_client.is_paused():
      await ctx.send("Player is already paused!!")
    else:
      await ctx.send("Paused ⏸️")
      ctx.voice_client.pause()
  
  ## resume the song
  @commands.command()
  async def resume(self,ctx):
    if ctx.voice_client.is_playing():
        await ctx.send("Player is already playing!!")
    else:
      await ctx.send("Resumed ▶️")
      ctx.voice_client.resume()

  ## display queue
  @commands.command()
  async def queue(self,ctx):
    global queue
    global nowPlaying
    message = []
    i = 1
    for item in queue[ctx.guild.id]:
      message.append(str(i)+". "+item.split("#+-+#")[0])
      i+=1
    
    message_string = "\n".join(message)
    if nowPlaying[ctx.guild.id] == None:
      now_playing = "-"
    else:
      now_playing = nowPlaying[ctx.guild.id]
    await ctx.send("Now Playing: "+now_playing+"\nCurrent Queue:\n"+message_string)
    
  ## remove song from queue
  @commands.command()
  async def remove(self,ctx,ind = "-1"):
    global queue
    if len(queue[ctx.guild.id]) == 0:
      await ctx.send("The playlist is empty and there is nothing to remove ❗")
      return

    if ind == "-1":
      await ctx.send("Please select a song to remove")
      return

    elif ind == "first":
      try:
        removedVid = queue[ctx.guild.id][0].split("#+-+#")[0]
        del queue[ctx.guild.id][0]
        await ctx.send(removedVid + " has been removed from queue ❌")
      except Exception as e:
        print(e)
    
    elif ind == "last":
      try:
        removedVid = queue[ctx.guild.id][-1].split("#+-+#")[0]
        del queue[ctx.guild.id][-1]
        await ctx.send(removedVid + " has been removed from queue ❌")
      except Exception as e:
        print(e)
    
    elif ind == "all":
      queue[ctx.guild.id]  = []
      await ctx.send("The playlist has been cleared ❌")
    
    else:
      try:
        ind = int(ind)
        removedVid = queue[ctx.guild.id][(ind-1)].split("#+-+#")[0]
        del queue[ctx.guild.id][(ind-1)]
        await ctx.send(removedVid + " has been removed from queue ❌")
      except Exception as e:
        print(e)
        await ctx.send("Invalid index selected ❗")
  
  @commands.command()
  async def play(self, ctx, *,song = None):
    global queue
    #print(song)
    target = song
    ## if song argument is None
    if target == None:
      await ctx.send("Please send the song name or url to play ❌")
      return
    if ctx.voice_client is None:
      await ctx.send("On bot is sad because On Bot isn't invited to a voice channel 😔")
      return

    ## a playlist url 
    if "list" in target:
      await ctx.send("This part of me is still under development 🚧")
      return
      
    ## not url input
    if "youtube.com/watch?" not in target:
      url = await self.search(ctx,target)
      if url == None:
        await ctx.send("Requested song isn't found ¯\_(ツ)_/¯ Try different keyword or input the url instead!")
        return
      target = url[0] ## get first result
    
    #print(target)
    ## first song
    if nowPlaying[ctx.guild.id] is None:
      nowPlaying[ctx.guild.id] = pafy.new(target).title
      await self.play_song(ctx,target,nowPlaying[ctx.guild.id])
      
    else:
      try:
        vidTitle = pafy.new(target).title
        queue[ctx.guild.id].append(vidTitle+"#+-+#"+target)
        await ctx.send(vidTitle + " is added into queue")
      except Exception as e:
        print(queue.keys())
        print(e)
        await ctx.send("This url has some issues 🚧 Please use the song name instead")
        
      #print(queue)

  @commands.command()
  async def skip(self,ctx):
    global queue
    print("skip fx")
    if len(queue[ctx.guild.id]) > 0:
      await ctx.send("Skipping to next song ⏭: "+queue[ctx.guild.id][0].split("#+-+#")[0])
      ctx.voice_client.stop()
    elif len(queue[ctx.guild.id]) == 0:
      ctx.voice_client.stop()
      await ctx.send("Player has reached the end of playlist 🔚")
    else:
      await ctx.send("The playlist is empty!! ❌")
  
  @commands.command()
  async def help(self,ctx):
    message_string = '\n'.join(command_list)
    await ctx.send("Help: \n"+message_string)




