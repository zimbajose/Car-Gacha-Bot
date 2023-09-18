from __future__ import annotations
import mysql.connector
import ddbconnector
import DiscordUser

class Car:


    __INSERT_INTO_CAR_POSSESSION = "INSERT INTO car_possession(car_id,user_discord_tag) VALUES (%(car_id)s,%(discord_tag)s) "
    __DELETE_FROM_CAR_POSSESSION = "DELETE FROM car_possession WHERE car_id = %(car_id)s AND user_discord_tag = %(discord_tag)s"
    __DEFAULT_SELECT_CAR = """
    SELECT c.id,c.model,c.price,c.image_url,c.rarity,c.drive,c.horsepower,c.weight,c.torque,c.car_year,c.brand_id,b.name
    FROM car c JOIN brand b ON c.brand_id = b.id 
    """
    __SELECT_BRAND = "SELECT b.id, b.name FROM brand b "
    __JOIN_USER = """ 
     JOIN car_possession cp ON cp.car_id = c.id 
     JOIN discord_user u ON cp.user_discord_tag = u.discord_tag 
    """

    __WHERE_USER_ID= """
     u.discord_tag = %(discord_tag)s
    """
    __WHERE_MODEL_LIKE = " c.model LIKE %(model)s "
    __WHERE_BRAND_ID = " b.id = %(brand_id)s"
    __WHERE_BRAND_REGEX =" %(exp)s REGEXP b.name"
    __WHERE_RARITY = " c.rarity = %(rarity)s "
    __WHERE_CAR_ID = " c.id = %(car_id)s "

    __ORDER_BY_RAND = " ORDER BY RAND() "
 
    __LIMIT = " LIMIT %(limit)s"

    def __init__(self,id : int,model : str,brand_name : str,price : float,image_url : str,rarity : int,drive :str, horsepower : int, weight : int, torque : int,year:int, brand_id : int):
        self.id = id
        self.model = model
        self.brand_name = brand_name
        self.price = price
        self.image_url = image_url
        self.rarity = rarity
        self.drive = drive
        self.horsepower = horsepower
        self.weight = weight
        self.torque = torque
        self.year = year
        self.brand_id = brand_id
    
    #Searches a search prompt for a brand name, the returns a prompt tripped fo the brand name and the brand_id, brand id will be -1 if there is none found
    @staticmethod
    def __strip_prompt(prompt:str):
        connector = ddbconnector.get_connection()
        cursor = connector.cursor()
        exp = "("+prompt+")"
        select = Car.__SELECT_BRAND+" WHERE "+Car.__WHERE_BRAND_REGEX
        data = {"exp":exp}
        cursor.execute(select,data)
        response = cursor.fetchone()
        if response == None:
            return prompt,-1
        prompt = prompt.casefold()
        prompt =prompt.replace(response[1].casefold(),"")
        prompt = prompt.lstrip()
        return prompt, response[0]

    #Generates the car from sql return data, returns a list if there are multiple rows, or a car if there is only one
    @staticmethod
    def __generate_from_sql_data(data : list)-> Car:
        def bind_data(data : tuple)->Car:
            id = data[0]
            model = data[1]
            price = data[2]
            image_url= data[3]
            rarity = data[4]
            drive = data[5]
            horsepower = data[6],
            weight = data[7]
            torque = data[8]
            car_year = data[9]
            brand_id = data[10]
            brand_name = data[11]
            return Car(id,model,brand_name,price,image_url,rarity,drive,horsepower,weight,torque,car_year,brand_id)
        if len(data)==0:
            return None
        if isinstance(data[0],tuple):
            cars = []
            for car_data in data:
                cars.append(bind_data(car_data))
            return cars
        return bind_data(data)
    
    #Gets a car by id
    @staticmethod
    def get_car_by_id(id : int) ->Car:
       connection = ddbconnector.get_connection()
       cursor = connection.cursor()
       
       select = Car.__DEFAULT_SELECT_CAR +" WHERE "+Car.__WHERE_CAR_ID
       data = {"car_id":id}
       cursor.execute(select,data)
       car = Car.__generate_from_sql_data(cursor.fetchone())
       cursor.close()
       connection.close()
       return car

    #Gets a random car based on rarity
    @staticmethod
    def get_random_car(rarity = None)-> Car:
        connection = ddbconnector.get_connection()
        cursor = connection.cursor()
        if rarity ==None:
            select = Car.__DEFAULT_SELECT_CAR + Car.__ORDER_BY_RAND + Car.__LIMIT
            cursor.execute(select,{"limit":1})
            car = Car.__generate_from_sql_data(cursor.fetchone())
            cursor.close()
            connection.close()
        else : 
            select = Car.__DEFAULT_SELECT_CAR +" WHERE "+Car.__WHERE_RARITY +Car.__ORDER_BY_RAND +Car.__LIMIT
            data = {"rarity":rarity,"limit":1}
            cursor.execute(select,data)
            car = Car.__generate_from_sql_data(cursor.fetchone())
            cursor.close()
            connection.close()
        return car
        

    #Gets all the cars of the user and returns them as a list, if a prompt is sent it will then try to search by name
    @staticmethod
    def get_user_cars(user : DiscordUser.User, prompt :str = None)->list:
        connection = ddbconnector.get_connection()
        cursor = connection.cursor()
        if prompt == None:
            select = Car.__DEFAULT_SELECT_CAR + Car.__JOIN_USER +" WHERE "+ Car.__WHERE_USER_ID
            data = {"discord_tag":user.discord_tag}
            cursor.execute(select,data)
            cars = Car.__generate_from_sql_data(cursor.fetchall())
            cursor.close()
            connection.close()
            return cars
        else:
            prompt,brand_id = Car.__strip_prompt(prompt)
            if brand_id == -1:
                select = Car.__DEFAULT_SELECT_CAR + Car.__JOIN_USER + " WHERE "+ Car.__WHERE_USER_ID +" AND "+ Car.__WHERE_MODEL_LIKE
                data = {"discord_tag":user.discord_tag,"model":"%"+prompt+"%"}
                cursor.execute(select,data)
                cars = Car.__generate_from_sql_data(cursor.fetchall())
            else:
                select = Car.__DEFAULT_SELECT_CAR +  Car.__JOIN_USER + " WHERE "+ Car.__WHERE_USER_ID +" AND "+ Car.__WHERE_MODEL_LIKE +" AND "+Car.__WHERE_BRAND_ID
                data = {
                    "discord_tag":user.discord_tag,
                    "model":"%"+prompt+"%",
                    "brand_id":brand_id
                }
                cursor.execute(select,data)
                cars = Car.__generate_from_sql_data(cursor.fetchall())
            cursor.close()
            connection.close()
            return cars
    #Searches for a x number of cars based on the sent string
    @staticmethod
    def search_cars(prompt : str,amount : int = 5) ->list:
        connection = ddbconnector.get_connection()
        cursor = connection.cursor()
        prompt, brand_id = Car.__strip_prompt(prompt)
        if brand_id ==-1:
            select = Car.__DEFAULT_SELECT_CAR +" WHERE " + Car.__WHERE_MODEL_LIKE+ Car.__LIMIT
            data = {
                "model": "%"+prompt+"%",
                "limit":amount
            }
            cursor.execute(select,data)
            cars = Car.__generate_from_sql_data(cursor.fetchall())
        else:
            select = Car.__DEFAULT_SELECT_CAR +" WHERE " + Car.__WHERE_MODEL_LIKE+" AND "+Car.__WHERE_BRAND_ID+  Car.__LIMIT
            data = {
                "model": "%"+prompt+"%",
                "limit":amount,
                "brand_id":brand_id
            }
            cursor.execute(select,data)
            cars = Car.__generate_from_sql_data(cursor.fetchall())
        cursor.close()
        connection.close()
        return cars

    #Checks if the user has this car in his garage, returns true if yes false if no
    def check_owner(self,user :DiscordUser.User)-> bool:
        connection = ddbconnector.get_connection()
        cursor = connection.cursor()
        select = Car.__DEFAULT_SELECT_CAR + Car.__JOIN_USER +" WHERE "+Car.__WHERE_USER_ID + "AND"+ Car.__WHERE_CAR_ID
        data = {
            "discord_tag":user.discord_tag,
            "car_id" : self.id
            }
        cursor.execute(select,data)
        response = cursor.fetchone()
        cursor.close()
        connection.close()
        return not response == None

    #Adds a ownership of this car to the database
    def add_owner(self,user : DiscordUser.User):
      connection = ddbconnector.get_connection()
      cursor = connection.cursor()
      data = {
          "discord_tag":user.discord_tag,
          "car_id":self.id
      }
      cursor.execute(Car.__INSERT_INTO_CAR_POSSESSION,data)
      connection.commit()
      cursor.close()
      connection.close()

    #Removes ownership of this car from the sent user
    def remove_owner(self,user : DiscordUser.User):
        connection = ddbconnector.get_connection()
        cursor = connection.cursor()
        query = Car.__DELETE_FROM_CAR_POSSESSION
        data = {
            "car_id":self.id,
            "discord_tag":user.discord_tag
        }
        cursor.execute(query,data)
        connection.commit()
        cursor.close()
        connection.close()

    
