import discord
import Genshin
import traceback

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    try:
       
        #Genshin Functions
        if message.content.startswith("$genshin"):
            await Genshin.message(message)

    
    except:
        await message.channel.send("An error occured")
        print(traceback.format_exc())

token = open("token.txt",'r').read()
client.run(token)
