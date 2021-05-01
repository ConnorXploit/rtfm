import telebot
from . import APIS

class Bot:

    def __init__(self):
        self.TOKEN = APIS.TELEGRAM
        self.GRUPO = APIS.TELEGRAM_CHAT_ID
        self.bot = telebot.TeleBot(self.TOKEN)

    def sendMessage(self, message, msgChatID=None, reply_markup=None, is_reply=False, disable_web_page_preview=True, disable_notification=True):
        if len(message) > 4096: 
            for x in range(0, len(message), 4096):
                if is_reply:
                    self.bot.reply_to(msgChatID if msgChatID else self.GRUPO, message[x:x+4096], reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification)
                else:
                    self.bot.send_message(self.GRUPO, message[x:x+4096], reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification)
        else: 
            if is_reply:
                self.bot.reply_to(msgChatID if msgChatID else self.GRUPO, message, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification)
            else:
                self.bot.send_message(self.GRUPO, message, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification)
