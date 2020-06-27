from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from os import environ
import logging

# Load TG bot token (please enter your own token in the .env file)
load_dotenv('.env')
BOT_TOKEN = environ.get('BOT_TOKEN')

# Updater continuously fetches new updates from TG to be passed to Dispatcher
updater = Updater(token=BOT_TOKEN,use_context=True)
dispatcher = updater.dispatcher

# Basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Start callback function returns a greeting
def start(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,text="I'm a bot, talk to me!")

start_handler = CommandHandler('start',start)
dispatcher.add_handler(start_handler)

updater.start_polling()
updater.idle()
