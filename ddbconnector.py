import mysql.connector

import sched

url = "127.0.0.1"
user = "root"
password = '123'
database = "car_gacha"


def get_connection():
    cnx = mysql.connector.connect(password = password,user='root',host = '127.0.0.1',database = 'car_gacha')
    return cnx 