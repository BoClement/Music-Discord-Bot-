# Discord bot Music (ytb and twitch) #

## Description ##

This Discord bot.py is a music bot where you can play music/video from youtube (and also stream from twitch). Moreover, you can also ask the bot for rng answers, funny things or also mute or kick someone for a specific time. (do not abuse)

Bot command : "."

## Requirements

1. Python version 3.5 or +
2. install all the libs in the requirements.txt
    ```bash
    sudo pip install -r requirements.txt
    ```
3. You will need to set up a discord bot on the discord developper website (check some ytb tuto)


# Compilation

When you have already create a discord bot on the discord developper website, you will need to put your own token at the end of the bot.py script. 
```py
client.run('here you put discord bot token (smth like wifi code)')
```

You can change the bot call command in line code above ("." by default)
```py
client = commands.Bot(command_prefix='.')
```

Then, simply run the bot.py script to enjoy the rebirth Rythm 2. If you want to host your bot for free you can check for Heroku (Idk if this work because since a update last year, my bot stopped working properly on Heroku).

```bash
python3 bot.py 
```

# Improvements
This is open-source so feel free to help or change.

Here is an non exhaustive list of what to do/correct :
- For some unknow reasons, some youtube music stop at half time.
- For some unknow reasons, discord buttons stop working after a certains time.
- Listen to a ytb playlist 
- Could add a player for spotify music 
- Add others funnctions
