
"""
Handlers for NDP Better To(gather) chatbot
"""
import logging
import datetime
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
import sqlite3

"""
the functions defined below are callback functions passed to Handlers. Arguments for
different classes of Handler can be found in docs.

some_fun(update, context) is the standard callback signature for the context based API
"""

logger = logging.getLogger(__name__)

#initialize dict keys
RULES, INTRO, NAME, GENDER, BIO, AGE = range(6)


def start(update, context):

    #sends starting message and request password
    update.message.reply_text(
    "Welcome to Better To(gather)'s party-matching bot! "
    "We'll match you with other attendees with similar hobbies or interests. Exciting hor? \n"

    "\nYou shall not pass...without a password! Please enter:"
    )

    #changes state of conv_handler. should make this function a bit more flexible
    return RULES


def get_user_details(user):
    """Gets user details from User object"""
    user_id = user.id
    username = user.full_name
    logger.info(f"Got user details: {user_id} {username}")

    if not get_user_document(user_id):
        create_user_document(user_id, username)


def rules(update, context):
    user = update.message.from_user
    logger.info("User %s 's password: %s", user.first_name, update.message.text)

    #set reply_keyboard
    reply_keyboard = [["OK, can"]]

    update.message.reply_text(
    "OK very nice. Hello! "
    "This is an open chat, but we are also a “family-friendly” page, so please keep comments and wall posts clean.\n"

    "\nWe want you to tell us what’s on your mind and provide a platform for likeminded individuals to connect through their interests, "
    "but please note that content falling into any of the categories below will be removed: \n"

    "\n1. We do not allow graphic, obscene, explicit or racial comments or submissions "
    "nor do we allow comments that are abusive, hateful or intended to defame anyone or any organization. \n"

    "\n2. We do not allow third-party solicitations or advertisements. "
    "This includes promotion or endorsement of any financial, commercial or non-governmental agency. "
    "Similarly, we do not allow attempts to defame or defraud any financial, commercial or non-governmental agency. \n"

    "\n3. We do not allow comments that support or encourage illegal activity. \n"

    "\nLet’s make this a safe space for everyone! :-D",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

    return INTRO


def intro(update, context):
    user = update.message.from_user
    logger.info("User %s says: %s", user.first_name, update.message.text)

    update.message.reply_text('Great! Your name please:')

    return NAME


def name(update, context):
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)

    #store user's name in dict (accessed through context.user_data)
    context.user_data['name'] = update.message.text

    #define next state for conversation
    reply_keyboard = [['He/him', 'She/her', 'They/them']]

    update.message.reply_text(
        'Ah boy, ah girl, others?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return GENDER



def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)

    #store user's gender in dict (accessed through context.user_data)
    context.user_data['gender'] = update.message.text

    #define keyboard for age range
    reply_keyboard = [['<20', '20s', '30s','40s','Other']]
    update.message.reply_text('You how old?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))


    return AGE


def age(update, context):
    user = update.message.from_user
    logger.info("Age of %s: %s", user.first_name, update.message.text)

    #store user's age in dict (accessed through context.user_data)
    context.user_data['age'] = update.message.text

    update.message.reply_text('Almost done soompah! Tell us something interesting about yourself?')

    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    #store user's age in dict (accessed through context.user_data)
    context.user_data['bio'] = update.message.text
    update.message.reply_text('Okay, finding a match for you...')

    conn = sqlite3.connect('coffeebot.db')
    c = conn.cursor()
    user_info = (update.effective_user.id,
                update.effective_chat.id,
                datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))),
                update.effective_user.username,
                context.user_data['name'],
                context.user_data['gender'],
                context.user_data['age'],
                context.user_data['bio'],
                0)
    c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)',user_info)
    conn.commit()

    #check for match
    #if match unavailable, proceed to end conversation; if available, notify both parties
    if len(c.execute("SELECT username FROM users WHERE matched=0").fetchall()) == 0:
        update.message.reply_text('Waiting for match...')

    else:
        #retrieve user_id of match
        c = c.execute("SELECT TOP username FROM users WHERE matched=0").fetchone()
        matched_username = c[0]
        c = c.execute("SELECT TOP bio FROM users WHERE matched=0").fetchone()
        matched_bio = c[0]

        #update db records of matched parties

        #send message to both parties
        update.message.reply_text("We've found a match! Meet @%s, who says: %s", matched_username, matched_bio)



    return ConversationHandler.END



def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def catch_random(update, context):
    user = update.message.from_user
    logger.info("User %s sent an unrecognized command %s", user.first_name, update.message.text)
    update.message.reply_text("I don't understand leh, try another reply")


add_start_cmd = CommandHandler('start', start)
add_rules = MessageHandler(Filters.regex('^password$'), rules)
add_intro = MessageHandler(Filters.text, intro)
add_name = MessageHandler(Filters.text, name)
add_gender = MessageHandler(Filters.regex('^(He/him|She/her|They/them)$'), gender)
add_age = MessageHandler(Filters.text, age)
add_bio = MessageHandler(Filters.text, bio)
add_catch_random = MessageHandler(Filters.all, catch_random)
