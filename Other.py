from __future__ import annotations
from threading import Timer
import discord


#The prompt lsit
class PromptList:
    __TIMEOUT_DELAY = 0

    def __init__(self):
        self.list = []
    def __timeout(self,prompt:MessagePrompt):
        pass
    
    def add(self, prompt : MessagePrompt):
        #Creates a timer to try to remove the prompt on timeout
        t = Timer(self.__timeout,prompt)


    def remove(self,prompt : MessagePrompt)-> bool:
        return True
    
#A message prompt to be reacted to
class MessagePrompt:

    def __init__(self,message : discord.Message,original_author : discord.User,callback : function ,data : any = None):
        self.message = message
        self.callback = callback
        self.original_author = original_author #Author of the message that resulted in this prompt
        self.data = data


#The emojis used by the bot
class Emojis:
    RIGHT_ARROW = "➡️"
    LEFT_ARROW = "⬅️"
    ONE = "1️⃣"
    TWO = "2️⃣"
    THREE = "3️⃣"
    FOUR = "4️⃣"
    FIVE = "5️⃣"
    ACCEPT = "✅"
    DECLINE = "❌"


#Formats a number for better viewing, returns it as string
def format_number(number : float)-> str:
    #First off rounds the number
    number = round(number)
    
    if number>=1000000:
        number = round(number/1000000,2)
        return str(number) + "M"
    if number >=100000:
        number = round(number/1000,2)
        return str(number) + "K"
    return str(number)