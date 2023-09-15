from __future__ import annotations
import discord

#A message prompt to be reacted to
class Message_Prompt:

    def __init__(self,message : discord.Message,original_author : discord.User,callback : function ,data : any = None):
        self.message = message
        self.callback = callback
        self.original_author = original_author #Author of the message that resulted in this prompt
        self.data = data


#The emojis used by the bot
class Emojis:
    right_arrow = "➡️"
    left_arrow = "⬅️"
    one = "1️⃣"
    two = "2️⃣"
    three = "3️⃣"
    four = "4️⃣"
    five = "5️⃣"