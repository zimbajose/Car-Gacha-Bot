from __future__ import annotations

import random
import discord
import DiscordUser

from Car import Car
from datetime import datetime,timedelta
class CarGacha:
    #Constants
    __delay = 0 # in minutes
    __got_car_message = "Congratulations author you have obtained a brand year car"
    __cars_list_message = "These are author's cars\n"
    __gacha_cooldown_message = "author you need to wait time minutes to roll again"
    __search_command_help = "The correct usage of this command is $car search <car name>"
    __search_list_title = "Select the car you are looking for"
    __search_list_not_found = "No cars found with similar names"
    __sell_rate = 3 #The value that the price will be divided by when you sell the car
    
    #A message prompt to be reacted to
    class Message_Prompt:

        def __init__(self,message : discord.Message,original_author : discord.User,response_func : function,data : any = None):
            self.message = message
            self.response_func = response_func
            self.original_author = original_author #Author of the message that resulted in this prompt
            self.data = data
    #The emojis used by the bot
    class Emojis:
        right_arrow = "➡️"
        left_arrow = "⬅️"
        one = "1️⃣"
        two = "2️⃣"
        three = "3️⃣"
        four = "4️⃣"
        five = "5️⃣"

    __rarities = {
        0:"common",
        1:"uncommon",
        2:"rare",
        3:"epic",
        4:"legendary",
        5:"Mythical"
    }
    

    __color_codes = {
        0: discord.Color.light_grey(),
        1: discord.Color.teal(),
        2: discord.Color.blue(),
        3: discord.Color.dark_purple(),
        4: discord.Color.orange(),
        5: discord.Color.gold()
    }

    def __init__(self):
        self.active_prompts = []
       
    #Handles all events that come from a message
    async def message(self,message : discord.Message):
        commands = message.content.split(" ")
        command = commands[1] if len(commands)>1 else "help"
        if command=='gacha':
            await self.__gacha_car(message.author,message.channel)
        elif command=='garage':
            await self.__get_user_cars(message.author,message.channel)
        elif command=='search':
            commands.pop(0)
            commands.pop(0)
            prompt = ""
            if len(commands)==0:
                await message.channel.send(CarGacha.__search_command_help)
                return
            for text in commands:
                prompt = prompt+ text + " "
            await self.__search_for_car(message.author,message.channel,prompt)
    

    #Handles all events tha come from reactoins
    async def react(self,reaction:discord.Reaction, user: discord.User):
        #Verifies if the message is in the active prompts list
        selected_prompt = None
        for message_prompt in self.active_prompts:
            if reaction.message == message_prompt.message:
                selected_prompt = message_prompt
                break
        if selected_prompt == None:
            return
        #Verifies if the user is author of the original prompt
        if user !=selected_prompt.original_author:
            return
        #Removes prompt and calls function associated
        await selected_prompt.response_func(selected_prompt,reaction)
        self.active_prompts.remove(selected_prompt)

    #Clears all active prompts from the user
    def __clear_prompts(self,user : discord.User):
        self.active_prompts = list(filter(lambda a : a.original_author !=user,self.active_prompts))


    #Sorts a random car from the list
    async def __gacha_car(self,author : discord.User, channel : discord.channel):
        rarity  = self.__get_random_rarity()
        car = Car.get_random_car(rarity)
        discord_tag = author.global_name
        user = DiscordUser.User.search_user(discord_tag)
        if user.last_gacha!=None:
            time_to_next_roll = user.last_gacha + timedelta(minutes = CarGacha.__delay)

            if time_to_next_roll>=datetime.now():
                difference = time_to_next_roll - datetime.now()
                cooldown_message = CarGacha.__gacha_cooldown_message.replace("author",author.display_name).replace("time",str(int(difference.total_seconds()/60)))
                await channel.send(cooldown_message)
                return
        
        #Adds the car to the user's list
        car.add_owner(user)
        user.set_time()
        embed_car = discord.Embed()
        embed_car.set_image(url=car.image_url)
        embed_car.set_footer(text = CarGacha.__rarities[rarity])
        embed_car.colour = CarGacha.__color_codes[rarity]
        text = CarGacha.__got_car_message.replace('car',car.model).replace('author',author.name).replace('brand',car.brand)
        if car.year!=None:
            text.replace("year",str(car.year))
        else:
            text.replace("year","")
        embed_car.description = text
        await channel.send(embed = embed_car)

    #Sends the list of cars the user has
    async def __get_user_cars(self,author : discord.User, channel : discord.channel):
        discord_tag = author.global_name
        user = DiscordUser.User.search_user(discord_tag)
        cars = Car.get_user_cars(user)
        if cars==None:
            await channel.send("It seems you have no cars, use the $car gacha command to roll for a random car")
            return
        cars_list = ""
        for car in cars:
            if car.year!=None:
                cars_list = cars_list+"\n "+str(car.year)+" "+car.model
            else:
                cars_list = cars_list+"\n "+car.model
        embed = discord.Embed()
        embed.title = CarGacha.__cars_list_message.replace('author',author.display_name)
        embed.description = cars_list
        await channel.send(embed = embed)
    
    #Searches for a car by name, sends a embed when there is only one with similar name, if there are multiple matches it sends a prompt to select one of them with reactions
    async def __search_for_car(self,author : discord.User,channel : discord.channel ,prompt : str):
        self.__clear_prompts(author)#Clear previous user prompts
        cars = Car.search_cars(prompt)
        if cars == None:
            await channel.send(CarGacha.__search_list_not_found)
            return
        if len(cars) ==1:
            car_embed = self.__get_car_embed(cars[0])
            await channel.send(embed = car_embed)
            return
        i = 1
        list_embed = discord.Embed()
        list_embed.title = CarGacha.__search_list_title
        message_text = ""
        for car in cars:
            if car.year == None:
                message_text = message_text+"\n"+str(i)+". "+car.model
            else:
                message_text = message_text+"\n"+str(i)+". "+str(car.year)+" "+car.model
        list_embed.description = message_text
        sent_message = await channel.send(embed= list_embed)
        await sent_message.add_reaction(CarGacha.Emojis.one)
        await sent_message.add_reaction(CarGacha.Emojis.two)
        if len(cars)>2:
            await sent_message.add_reaction(CarGacha.Emojis.three)
        if len(cars)>3:
            await sent_message.add_reaction(CarGacha.Emojis.four)
        if len(cars)>4:
            await sent_message.add_reaction(CarGacha.Emojis.five)
        new_message_prompt = CarGacha.Message_Prompt(sent_message,author,self.__searched_car,cars)
        self.active_prompts.append(new_message_prompt)

    #Responds to a search car prompt

    async def __searched_car(self,message_prompt: CarGacha.Message_Prompt,reaction : discord.Reaction):
        data = message_prompt.data
        #Checks for the reaction sent and sets carname based on the reaction
        if reaction.emoji == CarGacha.Emojis.one and len(data)>0:
            car =data[0]
        elif reaction.emoji == CarGacha.Emojis.two and len(data)>1:
            car = data[1]
        elif reaction.emoji == CarGacha.Emojis.three and len(data)>2:
            car = data[2]
        elif reaction.emoji == CarGacha.Emojis.four and len(data)>3:
            car = data[3]
        elif reaction.emoji == CarGacha.Emojis.five and len(data)>4:
            car = data[4]
        else:
            return
        #Obtains the car based on the id
        car = Car.get_car_by_id(car.id)
        car_embed = self.__get_car_embed(car)
        await message_prompt.message.channel.send(embed = car_embed)

    #Generates a embed with all the info of the selected car
    def __get_car_embed(self,car :Car)-> discord.Embed:
        car_embed = discord.Embed()
        if car.year!=None:
            car_embed.title = str(car.year)+" "+car.model
        else:
            car_embed.title = car.model
        car_embed.set_image(url=car.image_url)
        car_embed.set_footer(text=car.brand)
        car_embed.colour = CarGacha.__color_codes[car.rarity]
        info = car.drive+"\n"+str(car.horsepower)+" hp\n"+str(car.weight)+" kg\n"+ str(car.torque) + " nm\ndefault price "+str(car.price)
        car_embed.description = info

        return car_embed
    #Gets a random rarity
    def __get_random_rarity(self):
        rand = random.randint(1,1000)
        if rand>=995:
            return 5
        elif rand>=975:
            return 4
        elif rand>=925:
            return 3
        elif rand>=825:
            return 2
        elif rand >=650:
            return 1
        else:
            return 0
        
        

