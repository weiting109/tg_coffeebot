from telegram.ext import (Updater,
                            CommandHandler, MessageHandler, ConversationHandler,
                            Filters)
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from os import environ
import logging

# Load TG bot token (please enter your own token in the .env file)
load_dotenv('.env')
BOT_TOKEN = environ.get('BOT_TOKEN')


# Basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)



# Start callback function returns a greeting
def start(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,text="""
        Welcome to Better To(gather)'s party-matching bot! We'll match you with other attendees with similar hobbies or interests. Exciting hor?
    """)

# Cue rules
def rules(update,context):
    """
    We want to keep our Telegram page an open chat, but we are also a “family-friendly” page, so please keep comments and wall posts clean.

    We want you to tell us what’s on your mind or provide a platform for likeminded individuals to connect through their interests, but if it falls into any of the categories below, we want to let you know beforehand that we will have to remove it:

    1. We do not allow graphic, obscene, explicit or racial comments or submissions nor do we allow comments that are abusive, hateful or intended to defame anyone or any organization.

    2. We do not allow third-party solicitations or advertisements. This includes promotion or endorsement of any financial, commercial or non-governmental agency. Similarly, we do not allow attempts to defame or defraud any financial, commercial or non-governmental agency.

    3. We do not allow comments that support or encourage illegal activity.

    Let’s make this a safe space for everyone! :D
    """
    pass

def main():
    # Updater continuously fetches new updates from TG to be passed to Dispatcher
    updater = Updater(token=BOT_TOKEN,use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start',start)
    dispatcher.add_handler(start_handler)

    # Start bot
    updater.start_polling()

    # Run the bot until Ctr-C or process receives SIGINT/SIGTERM/SIGABRT
    # start_polling() is non-blocking, and will stop the bot gracefully
    updater.idle()

if __name__ == '__main__':
    main()
