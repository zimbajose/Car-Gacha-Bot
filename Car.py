from __future__ import annotations
import mysql.connector
import ddbconnector
import DiscordUser

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
    
