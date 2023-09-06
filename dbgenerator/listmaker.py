import json
import random
import csv

import mysql.connector

#Connects to the database
cnx = mysql.connector.connect(user='root',host = '127.0.0.1',database = 'car_gacha')
cursor = cnx.cursor()

#Price of the most expensive car, this is used to define the rarity of the cars
max_price = 20000000

with open("gran_turismo_gt6.csv",'r', encoding="utf-8") as cars_csv:
    cars = csv.reader(cars_csv,delimiter = ",")
    #Skips the headers
    next(cars,None)
    insert = "INSERT INTO car(model,price,image_url,brand,rarity) VALUES(%s,%s,%s,%s,%s)"
    for car in cars:
        if car[4] == '':
            continue
        car[4] = float(car[4])
        #Defines the rarity by the price
        #0 is commom
        #1 is uncommom
        #2 is rare
        #3 is epic
        #4 is legendary
        #5 is mythical
        if car[4]>=max_price/5:
            rarity = 5
        elif car[4]>=max_price/20:
            rarity = 4
        elif car[4]>=max_price/50:
            rarity = 3
        elif car[4]>=max_price/320:
            rarity =2
        elif car[4]>=max_price/600:
            rarity = 1
        else:
            rarity = 0

        insert_data = (car[1],car[4],car[3],car[0],rarity)
        cursor.execute(insert,insert_data)

cnx.commit()

cursor.close()
cnx.close()