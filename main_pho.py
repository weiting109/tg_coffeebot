
"""
test version of conversation bot for NDP party virtual 2020
to enter venv: source env/bin/activate
to begin: python3 ndpBot_v1.py
send /start to initiate the conversation
to leave venv: deactivate
to terminate: CTRL-C (not command!)

"""

import logging
from uuid import uuid4

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

from database import DBHelper
from handlers import add_rules, add_intro, add_name, add_gender, add_age, add_bio, start, cancel, add_catch_random


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


#database-related functions
db = DBHelper()

#initialize dict keys
RULES, INTRO, NAME, GENDER, BIO, AGE = range(6)

#import token
TOKEN = None

with open("token.txt") as f:
    TOKEN = f.read().strip()


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    #add conversation handler with states defined earlier
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            RULES: [add_rules],
            INTRO: [add_intro],
            NAME: [add_name],
            GENDER: [add_gender],
            AGE: [add_age],
            BIO: [add_bio]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    #probably add some handlers for random text a user might send
    dp.add_handler(conv_handler)
    dp.add_handler(add_catch_random)

    logger.info('Up and running')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
