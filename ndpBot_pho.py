
"""
test version of conversation bot for NDP party virtual 2020
send /start to initiate the conversation
"""

import logging
from uuid import uuid4

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NAME, GENDER, AGE = range(3)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


#database-related functions
db = DBHelper()

#initialize dict keys
RULES, INTRO, NAME, GENDER, AGE = range(5)


def main():
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher

    #add conversation handler with states defined earlier
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            RULES: [add_rules],
            INTRO: [add_intro],
            NAME: [add_name],
            GENDER: [add_gender],
            AGE: [add_age]
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
