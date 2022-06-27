import discord
from discord import voice_client
from discord import colour
from discord.client import Client
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.ui import Button
from discord.ui import view
from discord.ui.view import View

import random
from discord.ext.commands.core import after_invoke
import youtube_dl
from functools import partial
import asyncio

# valeur arbitraire
client = commands.Bot(command_prefix='.')


# A quoi sert channel ?
channel =""
# queues qui contient tous les sons a jouer
queue = []

# Setup "optmial" pour youtube_dl et ffmpeg

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ydl_opts  = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'http-chunk-size': '2000000',
    'default_search': "auto",
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

# Je ne sais pas ce que ca fait
youtube_dl.utils.bug_reports_message = lambda: ''

#creation d'une classe view pour laffichage simplifié des boutons

class ViewPlayPause(View):

    def __init__(self, ctx):
        super().__init__()
        self.ctx=ctx   
    
    @discord.ui.button(label="skip", style=discord.ButtonStyle.gray)
    async def button_skip_callback(self, button, interaction):
        await self.ctx.invoke(client.get_command('skip'))

    @discord.ui.button(label="resume", style=discord.ButtonStyle.green)
    async def button_resume_callback(self, button, interaction):
        await self.ctx.invoke(client.get_command('resume'))

        
    @discord.ui.button(label="pause", style=discord.ButtonStyle.red)
    async def button_pause_callback(self, button, interaction): 
        await self.ctx.invoke(client.get_command('pause'))


# event de démarage du bot
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Rabit est nul !"))
    
    
def checkqueue():
    if queue == []:
        return True
    else: return False

# commande nul qui print un message dans la console      
async def Emptyqueue(ctx):
    await ctx.send("There is no more songs to be played !") 

# méthode qui permet de faire un affichage sympa dans le channel texte du discord
async def embed(ctx, title,thumbnail,view):
    embed = discord.Embed(
        title = title,
        colour = discord.Colour.blue()
    )
    embed.set_author(name='Music BOT', icon_url='https://cdn.discordapp.com/attachments/915975502026649673/917848192270352414/Music.png')
    embed.set_footer(text='This song is currently being played')
    embed.set_thumbnail(url=thumbnail)
    await ctx.send(embed=embed,view=view)
    await view.wait()

    
# fameuse méthode play qui permet de donner l'url d'un son yt et de l'ajouter a la queue puis de la jouer 
@client.command(pass_content=True)
async def play(ctx, *, url):
    guild = ctx.message.guild
    voice = guild.voice_client
        
    # On check si autheur est connecté, si non on lui fait comprendre
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else: 
        await ctx.send("You are not connected to a voice channel")
        return
    # On check si le bot est connecté
    if not voice is None:
        if voice.is_connected():
            await voice.move_to(channel)   
    else:
        voice = await channel.connect()

        
    # je sais pas trop a quoi ca sert mais ca a l'air important.   
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        video = ydl.extract_info(url, download=False)
        if 'entries' in video:
            video_format = video['entries'][0]["formats"][0]
            thumbnail = video['entries'][0].get('thumbnail',None)
            video_title = video['entries'][0].get('title', None)
        elif 'formats' in video:
            video_format = video["formats"][0]
            thumbnail = video.get('thumbnail',None)
            video_title = video.get('title', None)
            
        url = video["webpage_url"]
        URL = video_format['url'] 
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    
    # Il y a 2 options : 
    # 1. On ajoute le son a la queue si le bot joue déjà un son
    # 2. le bot ne joue rien (1ere itération ou voice.stop()) et le bot joue le son (plus affichage sympa)

    if ctx.voice_client.is_playing() and checkqueue:
        queue.append((URL, video_title,thumbnail))
        await ctx.send('Video queued')    
        print("queued\n\n")
    else:
        voice.play(discord.FFmpegPCMAudio(URL),after = lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await embed(ctx, video_title,thumbnail,ViewPlayPause(ctx))
        #await ctx.invoke(client.get_command('play'))
        print("play\n\n")
    
# !play https://www.youtube.com/watch?v=nU21rCWkuJw
# !play https://www.youtube.com/watch?v=3PIyHxsE-gI&ab_channel=LostInLofi
    
async def play_next(ctx):
    guild = ctx.message.guild
    voice = guild.voice_client
    if queue != []:
        song = queue.pop(0)
        voice.play(discord.FFmpegPCMAudio(song[0]), after = lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await embed(ctx, song[1],song[2],ViewPlayPause(ctx))
        
        
# Commande qui permet de skip le son en cours, permet aussi de faire un affichage sympa (to be improved)
# Si Queue vide : juste print dans la console de notre côté
@client.command(pass_content=True)
async def skip(ctx):
    guild = ctx.message.guild
    voice = guild.voice_client
    if queue != []:
        song = queue.pop(0)
        voice.stop()
        voice.play(discord.FFmpegPCMAudio(song[0]), after = lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send("Musique skipped !")
        await embed(ctx, song[1],song[2],ViewPlayPause(ctx))
    else:
        await Emptyqueue(ctx)

# commande de ping basique
@client.command()
async def ping(ctx):
    await ctx.send(f'Ton ping est de {round(client.latency*1000)} ms')
    
# clear les messages du chat textuel (par défaut 2 derniers message, no max amount)
@client.command()
async def clear(ctx, amout=2):
    await ctx.channel.purge(limit=amout)

# ta commande de question pas ouf mais je la laisse parce que je suis sympa
@client.command()
async def question(ctx,*,question):
    responses = ["C'est certain.",
                "C'est décidément le cas.",
                "Sans aucun doute.",
                "Oui - définitivement.",
                "Vous pouvez vous y fier.",
                "Comme je le vois, oui.",
                "Très probablement.",
                "Bonne perspective.",
                "Oui.",
                "Les signes indiquent que oui.",
                "Réponse floue, essayez encore.",
                "Redemandez plus tard.",
                "Mieux vaut ne pas vous le dire maintenant.",
                "On ne peut pas prédire maintenant.",
                "Concentrez-vous et redemandez.",
                "Ne comptez pas là-dessus.",
                "Ma réponse est non.",
                "Mes sources disent non.",
                "Les perspectives ne sont pas très bonnes.",
                "Très douteux."
                ]
    await ctx.send(f'{random.choice(responses)}')

   
# commande test qui permet de savoir si le bot est en train de "parler ou non" (plus du tout utile mais je la laisse on sait jamais)
@client.command()
async def isplaying(ctx):
    if ctx.voice_client.is_playing():
        await ctx.reply("Playing audio :)")
    else:
        await ctx.reply("Nothing is playing")
        
@client.command()
async def disconnect(ctx):
    guild = ctx.message.guild
    voice = guild.voice_client
    await ctx.voice_client.disconnect()
    
# commande stop qui permet de stop le bot
@client.command()
async def stop(ctx):
    guild = ctx.message.guild
    voice = guild.voice_client
    voice.stop()
    
# commande qui permet de pause le bot
@client.command(pass_content=True)
async def pause(ctx):
    guild = ctx.message.guild
    voice = guild.voice_client
    voice.pause()
    #await ctx.send("Video paused !")

# command qui permet de reprendre la lecture en cours
@client.command(pass_content=True)
async def resume(ctx):
    guild = ctx.message.guild
    voice = guild.voice_client
    voice.resume()
    #await ctx.send("Video resumed !")

# comamnde qui retourne un choix rng parmi une string (élements doivent être séparés par un espace)
# works now (paramètre * permet de faire en sorte que le bot regarde toute la fin de la commande, il ne s'arrete pas a l'espace)
@client.command(pass_content=True)
async def rng(ctx, *, options):
    choices = options.split(' ')
    answer =  random.choice(choices)
    await ctx.send("RNG choosed : {}".format(answer))
    
@client.command(pass_content=True)
async def to(ctx, member : discord.Member):
    timer = 0
    voice = member.voice
    while timer<5:
        await asyncio.sleep(1)
        timer+=1
        if not voice is None:
            await member.move_to(None)
    
@client.command(pass_content=True)
async def mute(ctx, member : discord.Member):  
    await member.edit(mute=True)
    
    
client.run('here you put discord bot token (smth like wifi code)')

# REGARDER POUR LES BOUTONS + AMELIORATIONS DES EMBEDS
# COMPRENDRE POURQUOI BCP DE MUSIQUE S'ARRETE VERS 50% (je suppose que c'est parce que download=false) mais y'a peut etre une solution.