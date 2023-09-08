from __future__ import annotations
import json
import random
import discord
import DiscordUser
import mysql.connector
import ddbconnector
from datetime import datetime,timedelta
class CarGacha:
    #Constants
    __delay = 0 # in minutes
    __got_car_message = "Congratulations author you have obtained a brand car"
    __cars_list_message = "These are author's cars\n"
    __gacha_cooldown_message = "author you need to wait time minutes to roll again"
    __search_command_help = "The correct usage of this command is $car search <car name>"
    __sell_rate = 3 #The value that the price will be divided by when you sell the car

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
        5: discord.Color.blurple()
    }

    def __init__(self):
        pass
       
    #Handles all events that come from a message
    async def message(self,message : discord.Message):
        commands = message.content.split(" ")
        command = commands[1] if len(commands)>1 else "help"
        if command=='gacha':
            await self.__gacha_car(message.author,message.channel)
        if command=='garage':
            await self.__get_user_cars(message.author,message.channel)

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
        embed_car.description = text
        await channel.send(embed = embed_car)

    #Sends the list of cars the user has
    async def __get_user_cars(self,author : discord.User, channel : discord.channel):
        discord_tag = author.global_name
        user = DiscordUser.User.search_user(discord_tag)
        cars = Car.get_user_cars(user)
        if len(cars)==0:
            await channel.send("It seems you have no cars, use the $car gacha command to roll for a random car")
            return
        cars_list = ""
        for car in cars:
            cars_list = cars_list+"\n "+car.model
        embed = discord.Embed()
        embed.title = CarGacha.__cars_list_message.replace('author',author.display_name)
        embed.description = cars_list
        await channel.send(embed = embed)
    
    #Searches for a car by name, sends a embed when there is only one with similar name, if there are multiple matches it sends a prompt to select one of them with reactions
    async def __search_for_car(self,author : discord.User,channel : discord.channel ,prompt : str):
        discord_tag = author.global_name
        cars = Car.search_cars(prompt)
        if len(cars) == 0:
            await channel.send(CarGacha.__search_command_help)
            return
        if len(cars) ==1:
            car_embed = self.__get_car_embed(cars[0])
            await channel.send(embed = car_embed)
            return
        i = 1
        list_embed = discord.Embed()
        message = " "
        for car in cars:
            message = str(i)+". "+car.model
        

    #Generates a embed with all the info of the selected car
    def __get_car_embed(self,car :Car)-> discord.Embed:
        car_embed = discord.Embed()
        car_embed.title = car.model
        car_embed.set_image(car.image)
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
        
        

class Car:

    def __init__(self,id : int,model : str,brand : str,price : float,image_url : str,rarity : int,drive :str, horsepower : int, weight : int, torque : int):
        self.id = id
        self.model = model
        self.brand = brand
        self.price = price
        self.image_url = image_url
        self.rarity = rarity
        self.drive = drive
        self.horsepower = horsepower
        self.weight = weight
        self.torque = torque

    #Gets a car by id
    @staticmethod
    def get_car_by_id(id : int) ->Car:
        cnx = ddbconnector.get_connection()
        cursor = cnx.cursor()

        query = "SELECT id,model,brand,price,image_url,rarity,drive,horsepower,weight,torque FROM car WHERE id=%s"
        cursor.execute(query,id)
        data = cursor.fetchone()
        if data== None:
            return None
        cursor.close()
        cnx.close()
        return Car.__generate_from_sql_data(data)
    
    #Gets a random car based on rarity
    @staticmethod
    def get_random_car(rarity = None)-> Car:
        cnx = ddbconnector.get_connection()
        cursor = cnx.cursor()

        #If no rarity has been sent simply gets a random from all possible cars
        if rarity==None:
            query = "SELECT id,model,brand,price,image_url,rarity,drive,horsepower,weight,torque FROM CAR ORDER BY RAND() LIMIT 1"
            cursor.execute(query)
            data = cursor.fetchone()
            if data==None:
                cursor.close()
                cnx.close()
                Exception("Database has no cars!")
            return Car.__generate_from_sql_data(data)

        query = "SELECT id,model,brand,price,image_url,rarity,drive,horsepower,weight,torque FROM CAR WHERE rarity= %(rarity)s ORDER BY RAND() LIMIT 1"
        cursor.execute(query,{'rarity':rarity})
        data = cursor.fetchone()
        if data==None:
            Exception("No car found with this rarity value, was an invalid value sent?")

        return Car.__generate_from_sql_data(data)
    
    #Gets all the cars of the user and returns them as a list
    @staticmethod
    def get_user_cars(user : DiscordUser.User)->list:
        cnx =ddbconnector.get_connection()
        cursor = cnx.cursor()
        
        query = "SELECT c.id,c.model,c.brand,c.price,c.image_url,c.rarity,c.drive,c.horsepower,c.weight,c.torque FROM car c JOIN car_possession cp ON c.id=cp.car_id JOIN discord_user u ON u.discord_tag = %(user_tag)s"
        data = {
            "user_tag": user.discord_tag
        }
        cursor.execute(query,data)
        cars_raw = cursor.fetchall()
        cars = Car.__generate_from_sql_data(cars_raw)
        cursor.close()
        cnx.close()
        return cars
    
     #Searches for a x number of cars based on the sent string
    @staticmethod
    def search_cars(prompt : str,amount : int = 5) ->list:
        cnx = ddbconnector.get_connection()
        cursor = cnx.cursor()

        select = "SELECT id,model,price,image_url,brand,rarity,drive,horsepower,weight,torque FROM car WHERE model LIKE %(prompt)s LIMIT %(amount)s"
        data = {
            "prompt": prompt,
            "amount": amount
        }
        cars = Car.__generate_from_sql_data(cursor.fetchall())

        cursor.close()
        cnx.close()
        return cars

    #Generates the car from sql return data, returns a list if there are multiple rows, or a car if there is only one
    @staticmethod
    def __generate_from_sql_data(data : list):
        def __bind_data(data):
            id = data[0]
            model = data[1]
            brand = data[2]
            price = data[3]
            image_url = data[4]
            rarity =data[5]
            drive = data[6]
            horsepower = data[7]
            weight = data[8]
            torque = data[9]
            return Car(id,model,brand,price,image_url,rarity,drive,horsepower,weight,torque)

        if len(data)==0:
            return None
        
        if isinstance(data[0],tuple):
            cars = []
            for dat in data:
                car = __bind_data(dat)
                cars.append(car)
            return cars
        
        return __bind_data(data)

    #Adds a ownership of this car to the database
    def add_owner(self,user : DiscordUser.User):
        cnx = ddbconnector.get_connection()
        cursor = cnx.cursor()

        insert = "INSERT INTO car_possession(car_id,user_discordtag) VALUES(%(car_id)s,%(user_discordtag)s)"
        data = {
            "car_id": self.id,
            "user_discordtag":user.discord_tag
        }
        cursor.execute(insert,data)
        cnx.commit()
        cursor.close()
        cnx.close()

    #Removes ownership of this car from the sent user
    def remove_owner(self,user : DiscordUser.User):
        cnx = ddbconnector.get_connection()
        cursor = cnx.cursor()

        insert = "DELETE FROM car_possession WHERE car_id = %(car_id)s, AND user_discordtag = %(tag)s"
        data = {
            "car_id": self.id,
            "tag":user.discord_tag
        }
        cursor.execute(insert,data)
        cnx.commit()
        cursor.close()
        cnx.close()
    
