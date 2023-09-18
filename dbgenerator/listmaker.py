import json
import random
import csv

import mysql.connector

#Connects to the database
cnx = mysql.connector.connect(password = "123",user='root',host = '127.0.0.1',database = 'car_gacha')
cursor = cnx.cursor()

#Price of the most expensive car, this is used to define the rarity of the cars
#max_price = 20000000

with open("gran_turismo_gt6.csv",'r', encoding="utf-8") as cars_csv:
    cars = csv.reader(cars_csv,delimiter = ",")
    #Skips the headers
    next(cars,None)
    insert = """INSERT INTO car(model,price,image_url,rarity,drive,horsepower,weight,torque,car_year,brand_id) 
    VALUES(%(model)s,%(price)s,%(image_url)s,%(rarity)s,%(drive)s,%(horsepower)s,%(weight)s,%(torque)s,%(car_year)s,%(brand_id)s)"""
    brand_index = 0
    brand_ids = {}
    for car in cars:
        if car[4] == '' or car[6] =='' or car[7]=='' or car[8]== '':
            continue
        try:
            split_model = car[1].split("'")
            model = split_model[0]
            year = int(split_model[1])
            if year<=25:
                year = year+2000
            else:
                year = year+1900
        except:
            model = car[1]
            year = None
        image_url = car[3]
        brand = car[0]
        price = float(car[4])
        drive = car[5]
        horsepower = int(car[6])
        weight = int(car[7])
        torque = int(car[8])
        #Defines the rarity by the price
        #0 is commom
        #1 is uncommom
        #2 is rare
        #3 is epic
        #4 is legendary
        #5 is mythical
        if price>=14000000:
            rarity = 5
        elif price>=5000000:
            rarity = 4
        elif price>=1000000:
            rarity = 3
        elif price>=100000:
            rarity =2
        elif price>=50000:
            rarity = 1
        else:
            rarity = 0

        #checks if the brand exists already
        if brand in brand_ids:
            brand_id = brand_ids[brand]
        else:
            #Inserts the new brand
            brand_insert = "INSERT INTO brand(name) VALUES(%(name)s)"
            brand_data = {"name" : brand}
            cursor.execute(brand_insert,brand_data)
            cnx.commit()
            #Gets id from the inserted brand
            select = "SELECT id FROM brand WHERE name = %(name)s LIMIT 1"
            select_data = {"name":brand}
            cursor.execute(select,select_data)
            data = cursor.fetchone()
            brand_id =data[0]
            brand_ids[brand] = brand_id

        insert_data = {
            "model": model,
            "price": price,
            "image_url" : image_url,
            "rarity": rarity,
            "drive":drive,
            "horsepower":horsepower,
            "weight":weight,
            "torque":torque,
            "car_year":year,
            "brand_id": brand_id
        }
        cursor.execute(insert,insert_data)

cnx.commit()

cursor.close()
cnx.close()