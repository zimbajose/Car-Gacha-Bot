import discord
import json

__genshin_data = ''
#Load the json
with open("data.json") as json_file:
    __genshin_data = json.load(json_file)

if __genshin_data =='':
    Exception("Could not load genshin builds data.")

#Checks if the sent character exists
def __check_character(character):
    try:
        __genshin_data[character]
        return True
    except:
        return False


#Treats all the functions that come from a message event
async def message(message):
    commands = message.content.split(" ")
    
    if(len(commands)==1):
        await __send_help_message(message.channel)
        return
    
    character = commands[2] if len(commands)>2 else commands[1]
    command = commands[1] if len(commands)>2 else "info"
    
    if not __check_character(character):
        await message.channel.send("Could not find this character.")
        return 
    
    if command =="info":
        await __send_info(character,message.channel)

    elif command=="stats":
        await __send_stats(character,message.channel)

    elif command=="artifacts":
        await __send_artifacts(character,message.channel)

    elif command=="weapons":
        await __send_weapons(character,message.channel)
    else:
        await __send_help_message(message.channel)


#Get stats function
async def __send_stats(character,channel):
    embed_stats = discord.Embed()
    embed_stats.title = "Best stats"
    embed_stats.description = "Sands: "+__genshin_data[character]['best_stats']['sands']+"\nGoblet: "+__genshin_data[character]['best_stats']['goblet'] +"\nCirclet: "+__genshin_data[character]['best_stats']['circlet']+"\nSubstats: "+__genshin_data[character]['best_stats']['substats']
    await channel.send(embed = embed_stats)
    

async def __send_info(character,channel):
    embed_info = discord.Embed()
    embed_info.description=(__genshin_data[character]['info']['weapon']+" user")
    embed_info.set_footer(text = "Element",icon_url=__genshin_data[character]['info']['element'])
    embed_info.set_image(url=__genshin_data[character]['info']['portrait'])
    await channel.send(embed=embed_info)


async def __send_weapons(character,channel):
    for weapon in __genshin_data[character]['best_weapons']:
        embed_weapon = discord.Embed()
        embed_weapon.set_image(url=weapon['img'])
        embed_weapon.title = weapon['name']
        await channel.send(embed=embed_weapon)

async def __send_artifacts(character,channel):
    i =1
    for artifacts_sets in __genshin_data[character]['best_artifacts']:
        await channel.send("Top "+str(i))
        i = i+1
        for artifact in artifacts_sets:
            embed_artifact = discord.Embed()
            embed_artifact.title=artifact["name"]
            embed_artifact.set_image(url=artifact["img"])
            await channel.send(embed=embed_artifact)




#Help message

async def __send_help_message(channel):
    await channel.send("Use $genshin <character name> to get basic info for the character \n Use $genshin weapons <character name> to get the character's best weapons \n Use $genshin artifacts <character name> to get the character's best artifact sets \n Use $genshin stats <character name> to get the character's recommended stats")
