from __future__ import annotations
import discord
import traceback
import asyncio
from CarGacha import CarGacha

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

car_gacha = CarGacha(client)



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    #Starts the auction timer
    await car_gacha.wait_for_auctions()
@client.event
async def on_message(message):
    
    if message.author == client.user:
        return
    
    try:
        if message.content.startswith("$car"):
            await car_gacha.message(message)

    except:
        await message.channel.send("An error occured")
        print(traceback.format_exc())

@client.event
async def on_reaction_add(reaction,user):
    #Verifies if the message is from the bot
    if reaction.message.author ==client.user:
        await car_gacha.react(reaction,user)



token = open("token.txt",'r').read()
client.run(token)
