
"""
test version of conversation bot for NDP party virtual 2020
to begin: python3 ndpBot_v1.py
send /start to initiate the conversation
to leave venv: deactivate
to terminate: CTRL-C (not command!)

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

"""
the functions defined below are callback functions passed to Handlers. Arguments for
different classes of Handler can be found in docs.

some_fun(update, context) is the standard callback signature for the context based API
"""

def start(update, context):
    #sends starting message
    update.message.reply_text('Hello! Your name please')

    #changes state of conv_handler
    return NAME



def name(update, context):
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)

    #store user's name in dict (accessed through context.user_data)
    context.user_data['name'] = update.message.text

    #define next state for conversation
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Ah boy, ah girl, others?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return GENDER



def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)

    #store user's gender in dict (accessed through context.user_data)
    context.user_data['gender'] = update.message.text

    update.message.reply_text('You how old?')

    return AGE



def age(update, context):
    user = update.message.from_user
    logger.info("Age of %s: %s", user.first_name, update.message.text)

    #store user's age in dict (accessed through context.user_data)
    context.user_data['age'] = update.message.text

    update.message.reply_text('OK ready')

    return ConversationHandler.END


def getmyinfo(update, context):
    """Usage: /getmyinfo uuid"""
    # Seperate ID from command
    key = update.message.text.partition(' ')[2]

    # Load value
    try:
        value = context.user_data[key]
        update.message.reply_text(value)

    except KeyError:
        update.message.reply_text('Not found')



def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def main():
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher

    #add conversation handler with states defined earlier
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NAME: [MessageHandler(Filters.text, name)],
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            AGE: [MessageHandler(Filters.text, age)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('getmyinfo', getmyinfo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
