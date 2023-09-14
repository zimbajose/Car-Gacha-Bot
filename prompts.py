import discord

#A message prompt to be reacted to
class Message_Prompt:

    def __init__(self,message : discord.Message,original_author : discord.User,response_func : function,data : any = None):
        self.message = message
        self.response_func = response_func
        self.original_author = original_author #Author of the message that resulted in this prompt
        self.data = data