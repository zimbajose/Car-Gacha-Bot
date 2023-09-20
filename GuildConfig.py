from __future__ import annotations
from ddbconnector import get_connection
class GuildConfig:
    __SELECT_FROM_GUILD_CONFIG = "SELECT guild_id,auction_channel_id,auction_is_on FROM server_config sc "
    __WHERE_GUILD_ID = " sc.guild_id = %(guild_id)s "
    __WHERE_AUCTION_IS_TRUE = " sc.auction_is_on = 1 "
    __INSERT_INTO_GUILD_CONFIG = "INSERT INTO server_config(guild_id) VALUES(%(guild_id)s)"
    __UPDATE_SET_CHANNEL = "UPDATE server_config sc SET auction_channel_id = %(auction_channel_id)s "
    __UPDATE_SET_AUCTION_ON = "UPDATE server_config sc SET auction_is_on = %(auction_is_on)s "
    __REMOVE_SERVER_CONFIG = "DELETE FROM server_config sc "
    __LIMIT = " LIMIT 1"
    def __init__(self,guild_id : int, auction_is_on: int =0,auction_channel_id : int = None):
        self.guild_id = guild_id
        self.auction_is_on = auction_is_on
        self.auction_channel_id = auction_channel_id


    #Removes this guild form the database
    def remove_guild(self):
        connection = get_connection()
        cursor = connection.cursor()
        query = GuildConfig.__REMOVE_SERVER_CONFIG + "WHERE" + GuildConfig.__WHERE_GUILD_ID
        data = {
            "guild_id":self.guild_id
        }
        cursor.execute(query,data)
        connection.commit()
        cursor.close()
        connection.close()

    #Sets the config to start receiving auctions on or off
    def set_auction_is_on(self,is_on : bool):
        connection = get_connection()
        cursor = connection.cursor()
        query = GuildConfig.__UPDATE_SET_AUCTION_ON + "WHERE" + GuildConfig.__WHERE_GUILD_ID
        if is_on:
            data = {
                "guild_id":self.guild_id,
                "auction_is_on":1,
            }
        else:
            data = {
                "guild_id":self.guild_id,
                "auction_is_on":0,
            }
        
        cursor.execute(query,data)
        connection.commit()
        cursor.close()
        connection.close()
    
    #Sets a auction channel for the guild config
    def set_auction_channel(self,channel_id : int):
        connection = get_connection()
        cursor = connection.cursor()
        query = GuildConfig.__UPDATE_SET_CHANNEL + "WHERE" + GuildConfig.__WHERE_GUILD_ID
        data = {
            "guild_id":self.guild_id,
            "auction_channel_id":channel_id
        }
        cursor.execute(query,data)
        connection.commit()
        cursor.close()
        connection.close()

    #Binds select return data to a guild
    @staticmethod
    def __bind_data(data : dict)-> list:
        def create_guild_config(data) -> GuildConfig:
            guild_id = data[0]
            auction_channel_id = data[1]
            auction_is_on = data[2]
            return GuildConfig(guild_id,auction_is_on,auction_channel_id)
        if isinstance(data,list):
            guild_list = []
            for guild_config in data:
                guild_list.append(create_guild_config(guild_config))
            return guild_list
        return create_guild_config(data)

    #Tries to get the guild config, if there is no config it will insert a new one, returning the found or created guild in any case
    @staticmethod
    def search_guild_config(guild_id : int) -> GuildConfig:
        connection = get_connection()
        cursor = connection.cursor()
        query = GuildConfig.__SELECT_FROM_GUILD_CONFIG + "WHERE" + GuildConfig.__WHERE_GUILD_ID + GuildConfig.__LIMIT
        data = {
            "guild_id":guild_id
        }
        cursor.execute(query,data)
        guild_data = cursor.fetchone()
        if guild_data == None:
            GuildConfig.__insert_guild(guild_id)
            guild = GuildConfig(guild_id)
        else:
            guild = GuildConfig.__bind_data(guild_data)
        cursor.close()
        connection.close()
        return guild

    #Gets all the guilds that have the auction function turned on
    @staticmethod
    def get_auction_on_guilds() ->list:
        connection = get_connection()
        cursor = connection.cursor()
        
        query = GuildConfig.__SELECT_FROM_GUILD_CONFIG +"WHERE" + GuildConfig.__WHERE_AUCTION_IS_TRUE
        cursor.execute(query)
        guilds = GuildConfig.__bind_data(cursor.fetchall())
        cursor.close()
        connection.close()
        return guilds

    #Inserts a new guild config
    @staticmethod
    def __insert_guild(guild_id : int):
        connection = get_connection()
        cursor = connection.cursor()
        query = GuildConfig.__INSERT_INTO_GUILD_CONFIG
        print(guild_id)
        data = {
            "guild_id": guild_id
        }
        cursor.execute(query,data)
        connection.commit()
        cursor.close()
        connection.close()