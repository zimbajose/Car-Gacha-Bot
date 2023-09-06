import mysql.connector
import ddbconnector
class User:

    def __init__(self,tag,last_gacha = None):
        self.discord_tag = tag
        self.last_gacha = last_gacha

    #Searches for the user's tag in the database, if it does not find it it will then insert it, in both cases returns the a user object
    @staticmethod
    def search_user(tag):
        connector = ddbconnector.get_connection()
        cursor = connector.cursor()

        query = "SELECT discordtag, last_gacha FROM user WHERE discordtag = %s"
        cursor.execute(query,tag)
        
        data = cursor.fetchone()

        if data == None:
            insert = "INSERT INTO user(discordtag) VALUES(%s)"
            cursor.execute(insert,tag)
            cursor.close()
            connector.close()
            return User(tag)

        last_gacha = data[1]
        cursor.close()
        connector.close()
        return User(tag,last_gacha)