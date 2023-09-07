import mysql.connector
import sched

url = "127.0.0.1"
user = "root"
password = ''
database = "car_gacha"

#Failsafe to ensure the connection is eventually closed
scheduler = sched.scheduler()

def __close_connection(connection):
    connection.close()

def get_connection()-> mysql.connector:
    cnx = mysql.connector.connect(user='root',host = '127.0.0.1',database = 'car_gacha')
    scheduler.enter(10,2,__close_connection,argument = cnx)
    return cnx 