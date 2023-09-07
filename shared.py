from __future__ import annotations
import mysql.connector
import ddbconnector
class User:

    def __init__(self,tag : str,last_gacha = None):
        self.discord_tag = tag
        self.last_gacha = last_gacha

    #Searches for the user's tag in the database, if it does not find it it will then insert it, in both cases returns the a user object
    @staticmethod
    def search_user(tag : str)-> User:
        connector = ddbconnector.get_connection()
        cursor = connector.cursor()

        query = "SELECT discordtag, last_gacha FROM discord_user WHERE discordtag = %(tag)s"
        cursor.execute(query,{'tag':tag})
       
        data = cursor.fetchone()
        print(data)
        if data == None:
            insert = "INSERT INTO discord_user(discordtag) VALUES(%(tag)s)"
            cursor.execute(insert,{"tag":tag})
            connector.commit()
            cursor.close()
            connector.close()
            return User(tag)

        last_gacha = data[1]
       
        cursor.close()
        connector.close()
        return User(tag,last_gacha)