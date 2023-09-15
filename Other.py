from __future__ import annotations
import asyncio
import discord


#The prompt lsit
class PromptList:
    __TIMEOUT_DELAY = 60

    def __init__(self):
        self.list = []
    
    async def __timeout(self,prompt:MessagePrompt):
        await asyncio.sleep(self.__TIMEOUT_DELAY)
        await self.remove(prompt)
    
    #Find by prompt
    def __find_by_prompt(self,prompt:MessagePrompt)-> dict:
        for item in self.list:
            if item['prompt'] == prompt:
                return item
        return None
    
    #Deletes all previous prompts from the user
    async def __delete_all_from_user(self,user : discord.User):
        for item in self.list:
            if item['prompt'].original_author == user:
                await self.remove(item['prompt'])
                   

    async def add(self, prompt : MessagePrompt):
        await self.__delete_all_from_user(prompt.original_author)#Removes previous user prompts
        #Creates a timer to try to remove the prompt on timeout
        timer = asyncio.ensure_future(self.__timeout(prompt))
        data = {
            "timer":timer,
            "prompt" : prompt
        }
        self.list.append(data)

    async def remove(self,prompt : MessagePrompt)-> bool:
        data = self.__find_by_prompt(prompt)
        if data == None:
            return False
        self.list.remove(data)
        data['timer'].cancel()
        print(data['prompt'].message.content)
        await data['prompt'].message.delete()
        return True
    #Finds a prompt by a message
    def find_by_message(self,message : discord.Message) -> MessagePrompt:
        for item in self.list:
            if item['prompt'].message == message:
                return item['prompt']
        return None
    
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