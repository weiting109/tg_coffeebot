
"""
Handlers for NDP Better To(gather) chatbot
"""
import logging
import datetime
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from config import db
from database import CoffeeDB

"""
the functions defined below are callback functions passed to Handlers. Arguments for
different classes of Handler can be found in docs.

some_fun(update, context) is the standard callback signature for the context based API
"""

logger = logging.getLogger(__name__)

#initialize dict keys
RULES, INTRO, NAME, GENDER, BIO, AGE = range(6)

def isUsernameAvailable(update):
    """
    Check if user has set a username
    """
    return update.effective_user.username != None

def matchedPreviously(update, context):
    """
    Check if user has obtained a match previously
    """
    match = db.c.execute(f'SELECT * FROM users WHERE chat_id={update.effective_chat.id}').fetchone()
    return match!=None

def start(update, context):

    if matchedPreviously(update, context):

        #check if user has obtained a match before trying again
        match = db.c.execute(f'SELECT * FROM users WHERE chat_id={update.effective_chat.id}').fetchone()
        matched = match[CoffeeDB.col['matched']]
        context.user_data['name'] = match[CoffeeDB.col['firstname']]
        context.user_data['gender'] = match[CoffeeDB.col['gender']]
        context.user_data['age'] = match[CoffeeDB.col['agegroup']]
        context.user_data['bio'] = match[CoffeeDB.col['bio']]

        if matched==1:
        #if user has gotten a match before, jump straight to bio section
            update.message.reply_text(
            "Welcome back to Better To(gather)'s party-matching bot! "
            "Tell us another interesting thing about yourself?")

            return BIO

        else:
            update.message.reply_text('Still waiting for match...')
            return ConversationHandler.END

    else:
    #if user is new, sends starting message and request password
    #prompts user to set a username and ends conversation if username is unavailable
        if isUsernameAvailable(update):
            update.message.reply_text(
            "Welcome to Better To(gather)'s party-matching bot! "
            "We'll match you with a random cool attendee. Exciting hor? \n"

            "\nYou shall not pass...without a password! Please enter:"
            )

            #changes state of conv_handler. should make this function a bit more flexible
            return RULES

        else:
            update.message.reply_text('Oops! Must have username then can continue. Set username first then try again!')
            return ConversationHandler.END


def rules(update, context):
    user = update.message.from_user
    logger.info("User %s 's password: %s", user.first_name, update.message.text)

    #set reply_keyboard
    reply_keyboard = [["OK, can"]]

    update.message.reply_text(
    "OK very nice. Hello! "
    "This is an open chat, and  a platform for like-minded individuals to connect and forge friendships. ""
    Please help us to build a safe space, by not posting:\n"

    "\n1. Graphic, obscene, explicit or racially/religiously offensive content. \n"

    "\n2. Anything abusive, hateful or intended to defame or defraud anyone or any organization. \n"

    "\n3. Third-party solicitations or advertisements. This includes promotion or endorsement of any financial, "
    "commercial or non-governmental agency. Comments that support or encourage illegal activity. \n"

    "\nThank you for your support! \n"
    "If you encounter an abusive individual, drop us a FB message at https://www.facebook.com/Grounduppartysg/. \n",
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

def insertNewReq(update, context, matched):
    """
    Create new row in users table when a new request is made.
    """
    user_info = (update.effective_user.id,
                update.effective_chat.id,
                datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))),
                update.effective_user.username,
                context.user_data['name'],
                context.user_data['gender'],
                context.user_data['age'],
                context.user_data['bio'],
                matched)
    db.c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)',user_info)
    db.conn.commit()

def isMatchAvailable():
    """
    Check if a match is available
    """
    res = db.c.execute("SELECT username FROM users WHERE matched=0").fetchall()
    return len(res) > 0

def retrieveMatchRow():
    """
    Retrieves first available user to be matched
    """
    #retrieve user_id of match
    match = db.c.execute("SELECT * FROM users WHERE matched=0").fetchone()
    matched_userID = match[CoffeeDB.col['user_id']]

    #update db records of matched party
    db.c.execute(f'''
                UPDATE users
                SET matched = 1
                WHERE user_id = {matched_userID}
                ''')
    db.conn.commit()
    return match

def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    #store user's age in dict (accessed through context.user_data)
    context.user_data['bio'] = update.message.text
    update.message.reply_text('Okay, finding a match for you...')

    #check for match
    #if match unavailable, proceed to end conversation; if available, notify both parties
    if isMatchAvailable():
        match = retrieveMatchRow()
        match_chatid = match[CoffeeDB.col['chat_id']]
        match_username =  match[CoffeeDB.col['username']]
        match_name = match[CoffeeDB.col['firstname']]
        match_gender = match[CoffeeDB.col['gender']]
        match_agegroup = match[CoffeeDB.col['agegroup']]
        match_bio = match[CoffeeDB.col['bio']]

        #send message to curr user
        update.message.reply_text(f'''
                                We've found a match - meet @{match_username}!
                                \n\n Name: {match_name}
                                \n Preferred pronouns: {match_gender}
                                \n Age group: {match_agegroup}
                                \n Bio: {match_bio}
                                \n\n Go ahead and drop {match_name} a text to say hello :-) Happy chatting and enjoy the party!
                                \n Feeling a bit paiseh to talk to strangers? Come come we tell you some jokes. ''')

        #send message to match
        message = (f'''
                    We've found a match - meet @{user.username}!
                    \n\n Name: {context.user_data['name']}
                    \n Preferred pronouns: {context.user_data['gender']}
                    \n Age group: {context.user_data['age']}
                    \n Bio: {context.user_data['bio']}
                    \n\n Go ahead and drop {context.user_data['name']} a text to say hello :-) Happy chatting and enjoy the party!
                    \n Feeling a bit paiseh to talk to strangers? Come come we tell you some jokes. ''')

        context.bot.send_message(match_chatid, message)
        matched = 1 #current User has been matched
        logger.info(f"User @{match_username} has been matched with user @{user.username}")

    else:
        update.message.reply_text('Waiting for match...')
        matched = 0

    if db.c.execute(f'SELECT * FROM users WHERE chat_id={update.effective_chat.id}').fetchone() == None:
        insertNewReq(update,context,matched)

    else:
        #update db records of matched party
        db.c.execute(f'''
                    UPDATE users
                    SET matched = {matched}
                    WHERE chat_id = {update.effective_chat.id}
                    ''')
        db.conn.commit()

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
add_gender = MessageHandler(Filters.text, gender)
add_age = MessageHandler(Filters.text, age)
add_bio = MessageHandler(Filters.text, bio)
add_catch_random = MessageHandler(Filters.all, catch_random)

if __name__ == "__main__":
    print(isMatchAvailable())
    print(retrieveMatchRow())
