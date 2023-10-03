from __future__ import annotations

import random
import discord
import DiscordUser
import asyncio
from Car import Car
from datetime import datetime,timedelta
#Imports the prompts
from Other import MessagePrompt
from Other import Emojis
from Other import format_number
from Other import PromptList
from GuildConfig import GuildConfig 

class CarGacha:
    #Constants
    __DELAY = 30 # in minutes
    __SELL_RATE = 3 #The value that the price will be divided by when you sell the car
    __TIME_BETWEEN_AUCTIONS = 3600 # in seconds
    #Car garage command
    __CARS_LIST_MESSAGE = "These are author's cars\n"
   
    #Car sell command
    __SELL_NO_CARS_FOUND = "No cars found on your list of this model for selling."
    __SELL_CONFIRMATION_TITLE = "Are you sure?"
    __SELL_CONFIRMATION_DESCRIPTION = "Your year model will be sold for price credits, this action cannot be undone."
    __SELL_CONFIRMED_TEXT = "You sold your model for price credits."
    __SELL_DECLINED_TEXT = "You decided to not sell your model."
    #Car gacha command
    __ALREADY_HAS_CAR_MESSAGE = "You already have this car, selling for value credits"
    __GACHA_COOLDOWN_MESSAGE = "author you need to wait time minutes to roll again"
    __GOT_CAR_MESSAGE = "Congratulations author you have obtained a brand year car"

    #Auction
    __AUCTION_DESCRIPTION = "brand model is on a auction! current bid is price credits"
    __AUCTION_TITLE= "A wild model appeared!"
    __AUCTION_NOT_ENOUGH_MONEY_MESSAGE = "user, you do not have enough credits to bid in this car!"
    __NO_BIDS_ON_AUCTION = "No one has bidded on the brand model. "+Emojis.SAD
    __WON_AUCTION_MESSAGE = "Congratulations user, you obtained a brand model!"

    #Auction config
    __AUCTION_SETTED_CHANNEL="The auction channel has been set to auction_channel"
    __NO_AUCTION_CHANNEL = "The bot has no configured auction channel in this server, use the $car auction set command to set a channel."
    __AUCTION_TURNED_ON_MESSAGE = "Auctions have been turned on. Happy bidding!"
    __AUCTION_TURNED_OFF_MESSAGE = "Auctions have been turned off."
    __AUCTION_HELP_MESSAGE = "Use $car auction set to set a channel to host auctions, you can also use the $car auction activate to activate aucitons, and car auction deactivate, to deactivate auctions."
    #User balance
    __USER_BALANCE_MESSAGE = "author you have money CR on your account."

    #Help texts
    __SELL_COMMAND_HELP = "The correct usage of this command is $car sell <car model>"
    __SEARCH_COMMAND_HELP = "The correct usage of this command is $car search <car name>"
    

    #Search command
    __SEARCH_LIST_TITLE = "Select the car you are looking for"
    __SEARCH_LIST_NOT_FOUND = "No cars found with similar names"

    #Car command
    __HELP_COMMAND_HEADER = "This is the car gacha bot, use one of these commands to get started."
    __HELP_COMMANDS = [
        "$car gacha: Rolls for a random car.",
        "$car balance: Gets your current credits balance.",
        "$car garage: Shows a list of all your owned cars.",
        "$car sell: Sells a car that you own.",
        "$car search <carname>: Searches for a car",
        "$car auction set: Sets the current channel to receive auctions embeds.",
        "$car auction activate: Activates auctions for this server.",
        "$car auction deactivate: Deactivates auctions for this server."
    ]

    #Rarity codes
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

    def __init__(self,client : discord.Client):
        self.active_prompts = PromptList()
        self.client = client
        

    #Handles all events that come from a message
    async def message(self,message : discord.Message):
        commands = message.content.split(" ")
        command = commands[1] if len(commands)>1 else "help"
        if command=='gacha':
            await self.__gacha_car(message.author,message.channel)
        elif command=='garage':
            await self.__get_user_cars(message.author,message.channel)
        elif command == 'balance':
            await self.__get_user_balance(message.author,message.channel)
        elif command=='search':
            commands.pop(0)
            commands.pop(0)
            prompt = ""
            if len(commands)==0:
                await message.channel.send(CarGacha.__SEARCH_COMMAND_HELP)
                return
            for text in commands:
                prompt = prompt+ text + " "
            await self.__search_for_car(message.author,message.channel,prompt)
        elif command == 'sell':
            commands.pop(0)
            commands.pop(0)
            prompt = ""
            if len(commands)==0:
                await message.channel.send(CarGacha.__SELL_COMMAND_HELP)
                return
            for text in commands:
                prompt = prompt+ text + " "
            await self.__search_car_to_sell(message.author,message.channel,prompt)
        elif command =='auction':
            commands.pop(0)
            commands.pop(0)
            if len(commands) ==0:
                await message.channel.send(self.__AUCTION_HELP_MESSAGE)
            elif commands[0] == 'activate':
                await self.__set_auction_channel_on(message.channel.guild,message.channel,True)
            elif commands[0] == 'deactivate':
                await self.__set_auction_channel_on(message.channel.guild,message.channel,False)
            elif commands[0] =='set':
                await self.__set_auction_channel(message.channel.guild, message.channel)
        elif command=='help':
            await self.__send_help_embed(message.author,message.channel)
    #Handles all events tha come from reactions
    async def react(self,reaction:discord.Reaction, user: discord.User):
        #Verifies if the message is in the active prompts list
        selected_prompt = self.active_prompts.find_by_message(reaction.message)
        if selected_prompt == None:
            return

        #Calls function associated with prompt
        response = await selected_prompt.callback(selected_prompt,reaction)
        #If response is true, will remove the prompt message and remove the prompt from the active prompts, if not it will reset the timeout timer.
        if response:
            await self.active_prompts.remove(selected_prompt)
        else:
            selected_prompt.continue_run = True


    #Awaits to send auctions
    async def wait_for_auctions(self):
        await asyncio.sleep(self.__TIME_BETWEEN_AUCTIONS)
        await self.__send_auctions()
        await asyncio.ensure_future(self.wait_for_auctions())

    #Gets the guilds that have auctions turned on and then starts them
    async def __send_auctions(self):
        guilds = GuildConfig.get_auction_on_guilds()
        guilds_data = []
        for guild in guilds:
            data = {
                "guild" : guild,
                "car" : Car.get_random_car()
            }
            guilds_data.append(data)
        
        async def send_auction(guild : GuildConfig,car : Car):
            discord_guild = self.client.get_guild(guild.guild_id)
            if discord_guild == None:
                return
            channel =self.client.get_channel(guild.auction_channel_id)
            if channel == None:
                return
            await self.__start__auction(channel,car)
        for guild_data in guilds_data:
            asyncio.ensure_future(send_auction(guild_data['guild'],guild_data['car']))

    #Creates a auction embed
    @staticmethod
    def __get_auction_embed(car : Car,price : str, winning_bidder = None)->discord.Embed:
        auction_embed = discord.Embed()
        auction_embed.set_image(url = car.image_url)
        auction_embed.color = CarGacha.__color_codes[car.rarity]
        auction_embed.description = CarGacha.__AUCTION_DESCRIPTION.replace("brand",car.brand_name).replace("model",car.model).replace("price",price)
        auction_embed.title = CarGacha.__AUCTION_TITLE.replace("model",car.model)
        if not winning_bidder== None:
            auction_embed.set_footer(text = "The winning bidder is "+winning_bidder)
        return auction_embed
    
    #Starts a auction
    async def __start__auction(self,channel : discord.TextChannel,car : Car):
        start_price = float(car.price)/1.5
        auction_embed = CarGacha.__get_auction_embed(car,format_number(start_price))
        sent_message = await channel.send(embed= auction_embed)
        await sent_message.add_reaction(Emojis.UP)
        await sent_message.add_reaction(Emojis.MORE_UP)
        data = {
            "car":car,
            "price":start_price
        }
        new_prompt = MessagePrompt(sent_message,None,self.__bid_on_auction,data,self.__end_auction)
        await self.active_prompts.add(new_prompt)

    #Called when a auction has been bidded on
    async def __bid_on_auction(self,prompt : MessagePrompt, reaction : discord.Reaction):
        if not (reaction.emoji == Emojis.UP or reaction.emoji == Emojis.MORE_UP):
            return
        car = prompt.data['car']
        #Gets the last one that reacted
        users = [user async for user in reaction.users()]
        discord_user = users[len(users)-1]
        bidded_user = DiscordUser.User.search_user(discord_user.global_name)
        if reaction.emoji == Emojis.UP:
            value_to_sum = (float(car.price)*0.2)
        if reaction.emoji == Emojis.MORE_UP:
            value_to_sum = (float(car.price)*0.4)
        #Sends message to the user saying that he does not have enough credits.
        if float(bidded_user.gacha_money)<float(prompt.data['price'])+value_to_sum:
            if discord_user.dm_channel == None:
                user_channel = await discord_user.create_dm()
            else:
                user_channel = discord_user.dm_channel
            await user_channel.send(CarGacha.__AUCTION_NOT_ENOUGH_MONEY_MESSAGE.replace("user",bidded_user.discord_tag))
        else:
            prompt.data['price'] =(float(prompt.data['price'])+value_to_sum)
            prompt.data['winningbidder'] = bidded_user
            #Generates a new embed
            embed = CarGacha.__get_auction_embed(car,format_number(prompt.data['price']),prompt.data['winningbidder'].discord_tag)
            await prompt.message.edit(embed = embed)
        #Removes the reaction that the user sent
        await reaction.remove(discord_user)
        return False
        

    #Called when a auction has ended
    async def __end_auction(self,prompt:MessagePrompt):
        car = prompt.data['car']
        if not "winningbidder" in prompt.data.keys():
            await prompt.message.channel.send(CarGacha.__NO_BIDS_ON_AUCTION.replace("brand",car.brand_name).replace("model",car.model))
            return
        winning_user = prompt.data["winningbidder"]
        #Adds the car to the user and, and subtracts the money for him.
        winning_user.subtract_money(prompt.data['price'])
        car.add_owner(winning_user)
        await prompt.message.channel.send(CarGacha.__WON_AUCTION_MESSAGE.replace("user",winning_user.discord_tag).replace("brand",car.brand_name).replace("model",car.model))

    #Sets a channel for auctions
    async def __set_auction_channel(self,guild : discord.Guild, channel : discord.TextChannel):
        guild_config = GuildConfig.search_guild_config(guild.id)
        guild_config.set_auction_channel(channel.id)
        await channel.send(self.__AUCTION_SETTED_CHANNEL.replace("auction_channel",channel.name))

    #Sets the guild to accept auctions
    async def __set_auction_channel_on(self,guild : discord.Guild, channel : discord.TextChannel,is_on : bool):
        guild_config = GuildConfig.search_guild_config(guild.id)
        if guild_config.auction_channel_id == None:
            await channel.send(self.__NO_AUCTION_CHANNEL)
            return
        guild_channel = guild.get_channel(guild_config.auction_channel_id)
        if channel == None:
            await channel.send(self.__NO_AUCTION_CHANNEL)
            guild_config.set_auction_channel(None)
            return
        guild_config.set_auction_is_on(is_on)
        if is_on:
            await channel.send(self.__AUCTION_TURNED_ON_MESSAGE)
        else:
            await channel.send(self.__AUCTION_TURNED_OFF_MESSAGE)
    

    #Sends a help embed
    async def __send_help_embed(self,author : discord.User, channel : discord.TextChannel):
        embed = discord.Embed()
        embed.title = CarGacha.__HELP_COMMAND_HEADER
        description = ""
        for command in CarGacha.__HELP_COMMANDS:
            description = description+"\n"+ command
        embed.description = description
        await channel.send(embed= embed)

    #Sorts a random car from the list
    async def __gacha_car(self,author : discord.User, channel : discord.TextChannel):
        rarity  = self.__get_random_rarity()
        car = Car.get_random_car(rarity)
        discord_tag = author.global_name
        user = DiscordUser.User.search_user(discord_tag)
        if user.last_gacha!=None:
            time_to_next_roll = user.last_gacha + timedelta(minutes = CarGacha.__DELAY)

            if time_to_next_roll>=datetime.now():
                difference = time_to_next_roll - datetime.now()
                cooldown_message = CarGacha.__GACHA_COOLDOWN_MESSAGE.replace("author",author.display_name).replace("time",str(int(difference.total_seconds()/60)))
                await channel.send(cooldown_message)
                return
        
        has_car = car.check_owner(user)
        #Checks if user already has the car otherwise it will sell it
        if not has_car:
            #Adds the car to the user's list
            car.add_owner(user)
        user.set_time()
        embed_car = discord.Embed()
        embed_car.set_image(url=car.image_url)
        embed_car.set_footer(text = CarGacha.__rarities[rarity])
        embed_car.colour = CarGacha.__color_codes[rarity]
        text = CarGacha.__GOT_CAR_MESSAGE.replace('car',car.model).replace('author',author.name).replace('brand',car.brand_name)
        if car.year!=None:
            text.replace("year",str(car.year))
        else:
            text.replace("year","")
        embed_car.description = text
        await channel.send(embed = embed_car)
        if has_car:
            sell_price = car.price/3
            sell_message = CarGacha.__ALREADY_HAS_CAR_MESSAGE.replace("value",format_number(sell_price))
            user.add_money(sell_price)
            await channel.send(sell_message)

    #Checks the user's balance
    async def __get_user_balance(self,author: discord.User,channel : discord.TextChannel):
        user = DiscordUser.User.search_user(author.global_name)
        message_text = CarGacha.__USER_BALANCE_MESSAGE.replace("money",format_number(user.gacha_money))
        await channel.send(message_text)

    #Sends the list of cars the user has
    async def __get_user_cars(self,author : discord.User, channel : discord.TextChannel):
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
        embed.title = CarGacha.__CARS_LIST_MESSAGE.replace('author',author.display_name)
        embed.description = cars_list
        await channel.send(embed = embed)
    
    #Searches for a car by name, sends a embed when there is only one with similar name, if there are multiple matches it sends a prompt to select one of them with reactions
    async def __search_for_car(self,author : discord.User,channel : discord.TextChannel ,prompt : str):
        cars = Car.search_cars(prompt)
        if cars == None:
            await channel.send(CarGacha.__SEARCH_LIST_NOT_FOUND)
            return
        if len(cars) ==1:
            car_embed = self.__get_car_embed(cars[0])
            await channel.send(embed = car_embed)
            return
        await self.__send_car_select_prompt(channel,author,cars,self.__send_embed)

    #Searches for the car model in the user's cars, then send a prompt for the user to select the car he wants to sell
    async def __search_car_to_sell(self,author : discord.User,channel : discord.TextChannel, prompt : str):
        if prompt == "":
            await channel.send(CarGacha.__SELL_COMMAND_HELP)
            return
        user = DiscordUser.User.search_user(author.global_name)
        cars = Car.get_user_cars(user,prompt)
        #Checks the length, if its 0 will say it found no cars, if 1 it will send the confimartion prompt
        if cars == None:
            await channel.send(CarGacha.__SELL_NO_CARS_FOUND)
            return
        elif len(cars)==1:
            await self.__send_sell_confirmation_prompt(None,cars[0],author,channel)
            return
        #Sends a select prompt with the callback for the sell confirmation prompt function
        await self.__send_car_select_prompt(channel,author,cars,self.__send_sell_confirmation_prompt)

    #Sends a confirmation prompt to see if the user really wants to sell the car
    async def __send_sell_confirmation_prompt(self,message_prompt : MessagePrompt, car : Car, author : discord.User = None, channel : discord.TextChannel = None):
        if not message_prompt == None:
            channel = message_prompt.message.channel
            author = message_prompt.original_author
        sell_price = car.price/CarGacha.__SELL_RATE
        description = CarGacha.__SELL_CONFIRMATION_DESCRIPTION.replace("year",str(car.year)).replace("model",str(car.model)).replace("price",format_number(sell_price))
        message_embed = discord.Embed()
        message_embed.title = CarGacha.__SELL_CONFIRMATION_TITLE
        message_embed.description = description
        sent_message = await channel.send(embed = message_embed)
        await sent_message.add_reaction(Emojis.ACCEPT)
        await sent_message.add_reaction(Emojis.DECLINE)

        new_prompt = MessagePrompt(sent_message,author,self.__sell_car,car)
        await self.active_prompts.add(new_prompt)
        return True

    #Sells or not the car based on the reply
    async def __sell_car(self,message_prompt : MessagePrompt, reaction : discord.Reaction):
        car = message_prompt.data
        sell_price = car.price/CarGacha.__SELL_RATE
        #Checks if the user is the one who reacted
        users = [user async for user in reaction.users()]
        if not message_prompt.original_author in users:
            return
        if reaction.emoji==Emojis.DECLINE:
            decline_message = CarGacha.__SELL_DECLINED_TEXT.replace("model",car.model)
            await message_prompt.message.channel.send(decline_message)
            return True
        if reaction.emoji == Emojis.ACCEPT:
            accept_message = CarGacha.__SELL_CONFIRMED_TEXT.replace("model",car.model).replace("price",format_number(sell_price))
            user = DiscordUser.User.search_user(message_prompt.original_author.global_name)
            car.remove_owner(user)
            user.add_money(sell_price)
            await message_prompt.message.channel.send(accept_message)
            return True
        return False

    #Sends a car embed
    async def __send_embed(self,message_prompt : MessagePrompt,car : Car):
        
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
        car_embed.set_footer(text=car.brand_name)
        car_embed.colour = CarGacha.__color_codes[car.rarity]
        info = car.drive+"\n"+str(car.horsepower)+" hp\n"+str(car.weight)+" kg\n"+ str(car.torque) + " nm\ndefault price "+format_number(car.price)+" CR"
        car_embed.description = info

        return car_embed
    
    #Sends a car selection prompt
    async def __send_car_select_prompt(self,channel : discord.TextChannel,author : discord.User,cars : list,callback : function):
        if len(cars)<2:
            Exception("Not enough cars to make a select prompt")
        i = 1
        list_embed = discord.Embed()
        list_embed.title = CarGacha.__SEARCH_LIST_TITLE
        message_text = ""
        for car in cars:
            if car.year == None:
                message_text = message_text+"\n"+str(i)+". "+car.model
            else:
                message_text = message_text+"\n"+str(i)+". "+str(car.year)+" "+car.model
        list_embed.description = message_text
        
        sent_message = await channel.send(embed= list_embed)
        await sent_message.add_reaction(Emojis.ONE)
        await sent_message.add_reaction(Emojis.TWO)
        if len(cars)>2:
            await sent_message.add_reaction(Emojis.THREE)
        if len(cars)>3:
            await sent_message.add_reaction(Emojis.FOUR)
        if len(cars)>4:
            await sent_message.add_reaction(Emojis.FIVE)
        data = {
            "cars":cars,
            "callback": callback 
        }
        new_message_prompt = MessagePrompt(sent_message,author,self.__select_car_prompt,data)
        await self.active_prompts.add(new_message_prompt)

    #Returns the car from a selected prompt on the callback
    async def __select_car_prompt(self,message_prompt : MessagePrompt,reaction: discord.reaction):
        users = [user async for user in reaction.users()]
        if not message_prompt.original_author in users:
            return
        cars = message_prompt.data['cars']
        #Checks for the reaction sent and sets the car based on the data sent
        if reaction.emoji == Emojis.ONE and len(cars)>0:
            car =cars[0]
        elif reaction.emoji == Emojis.TWO and len(cars)>1:
            car = cars[1]
        elif reaction.emoji == Emojis.THREE and len(cars)>2:
            car = cars[2]
        elif reaction.emoji == Emojis.FOUR and len(cars)>3:
            car = cars[3]
        elif reaction.emoji == Emojis.FIVE and len(cars)>4:
            car = cars[4]
        else:
            return False
        #Obtains the car based on the id
        car = Car.get_car_by_id(car.id)
        await message_prompt.data['callback'](message_prompt,car)
        return True

    #Gets a random rarity
    def __get_random_rarity(self) ->int:
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
        
        

