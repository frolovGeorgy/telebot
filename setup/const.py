from decouple import config
import telebot

BOT_TOKEN = config('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
