
"""
Handlers for NDP Better To(gather) chatbot
"""
import logging
import datetime
import random
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
DISCLAIMER, RULES, INTRO, NAME, GENDER, BIO, AGE = range(7)

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

def remainingMatches(update):
    """
    Check if user has reached maximum number of matches allowed each day (5 matches per 24 hours)
    """
    daily_allowed_matches = 5
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date()

    count_user1 = db.c.execute(f"SELECT * FROM matches WHERE user1_id='{update.effective_user.username}' AND datetime='{today}'").fetchall()
    count_user1 = len(count_user1)

    count_user2 = db.c.execute(f"SELECT * FROM matches WHERE user2_id='{update.effective_user.username}' AND datetime='{today}'").fetchall()
    count_user2 = len(count_user2)

    return daily_allowed_matches - (count_user1 + count_user2)

def start(update, context):

    user = update.message.from_user
    logger.info("User %s has started a match request", user.first_name)

    #check if user has hit maximum number of matches allowed daily
    remaining_matches = remainingMatches(update)
    if remaining_matches == 0:
        update.message.reply_text('Sorry, you have no matches left today!')
        return ConversationHandler.END

    else:
        #check if user has obtained a match before trying again
        if matchedPreviously(update, context):
            match = db.c.execute(f'SELECT * FROM users WHERE chat_id={update.effective_chat.id}').fetchone()
            matched = match[CoffeeDB.col['matched']]
            context.user_data['name'] = match[CoffeeDB.col['firstname']]
            context.user_data['gender'] = match[CoffeeDB.col['gender']]
            context.user_data['age'] = match[CoffeeDB.col['agegroup']]
            context.user_data['bio'] = match[CoffeeDB.col['bio']]

            if matched==1:
            #if user has gotten a match before, jump straight to bio section
                update.message.reply_text(f'''
                Welcome back to Better To(gather)'s party-matching bot! You have {remaining_matches} matches left today.\n
                \nTell us another interesting thing about yourself?''')

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

                "\nYou shall not pass...without the password! Please enter:"
                )

                #changes state of conv_handler. should make this function a bit more flexible
                return DISCLAIMER

            else:
                update.message.reply_text('Oops! Must have username then can continue. Set username first then try again!')
                return ConversationHandler.END

def disclaimer(update, context):
    user = update.message.from_user
    logger.info("User %s 's password: %s", user.first_name, update.message.text)

    if update.message.text != "ILOVESG":
        update.message.reply_text("Alamak, wrong password! Try again?")

        return DISCLAIMER

    else:
        #set reply_keyboard
        reply_keyboard = [["Yes, I understand"]]

        update.message.reply_text(
        "OK very nice. Hello! "
        "This is an open chat, and  a platform for like-minded individuals to connect and forge friendships. "
        "Note that this bot will share your Telegram handle with your match partner.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

        return RULES

def rules(update, context):
    user = update.message.from_user
    logger.info("User %s 's reply: %s", user.first_name, update.message.text)

    #set reply_keyboard
    reply_keyboard = [["OK, can"]]

    update.message.reply_text(
    "Great! Please help us to build a safe space, by not posting:\n"

    "\n1. Graphic, obscene, explicit or racially/religiously offensive content. \n"

    "\n2. Anything abusive, hateful or intended to defame or defraud anyone or any organization. \n"

    "\n3. Third-party solicitations or advertisements. This includes promotion or endorsement of any financial, "
    "commercial or non-governmental agency. Comments that support or encourage illegal activity. \n"

    "\nThank you for your support! \n"
    "If you encounter an abusive individual, drop us a FB message at https://www.facebook.com/Grounduppartysg/. \n"
    "\nNote that you can only match with a maximum of 5 guests each day. Type anything to continue!",
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

def identicalMatchExists(user, match_username):
    """
    Check if the matched users have been matched previously to prevent repeated matches
    """
    if user.username < match_username:
        user1, user2 = user.username, match_username

    else:
        user1, user2 = match_username, user.username

    res = db.c.execute(f"SELECT * FROM matches WHERE user1_id = '{user1}' AND user2_id = '{user2}'").fetchall()
    return len(res) > 0

def retrieveMatchRow(user):
    """
    Checks if the matched users have been matched previously (prevent repeated matches)
    Retrieves first available and eligible user to be matched
    """
    #retrieve all available matches
    available_matches = db.c.execute("SELECT * FROM users WHERE matched=0").fetchall()

    #iterate through matches, checking if identicalMatchExists
    for match in available_matches:
        matched_userID = match[CoffeeDB.col['user_id']]
        matched_username = match[CoffeeDB.col['username']]

        if identicalMatchExists(user, matched_username):
            match_success = 0
            continue

        else:
            match_success = 1
            #update db records of matched party
            db.c.execute(f'''
                        UPDATE users
                        SET matched = 1
                        WHERE user_id = {matched_userID}
                        ''')
            db.conn.commit()
            break

    if match_success==0:
        return 0
    else:
        return match

def insertNewMatch(update, match_username):
    """
    Create new row in matches table when a new match is made
    Composite key decided by alphabetical order to prevent repeated matches
    """
    if update.effective_user.username < match_username:
        user1, user2 = update.effective_user.username, match_username

    else:
        user1, user2 = match_username, update.effective_user.username

    match_info = (user1,
                 user2,
                 datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date())

    db.c.execute('INSERT INTO matches VALUES (?,?,?)',match_info)
    db.conn.commit()

def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)

    #store user's age in dict (accessed through context.user_data)
    context.user_data['bio'] = update.message.text
    update.message.reply_text('Okay, finding a match for you...')

    #check for match
    #if match unavailable, proceed to end conversation; if available, notify both parties
    if isMatchAvailable():
        match = retrieveMatchRow(user)

        #if unique match is available:
        if match!=0:
            match_chatid = match[CoffeeDB.col['chat_id']]
            match_username =  match[CoffeeDB.col['username']]
            match_name = match[CoffeeDB.col['firstname']]
            match_gender = match[CoffeeDB.col['gender']]
            match_agegroup = match[CoffeeDB.col['agegroup']]
            match_bio = match[CoffeeDB.col['bio']]

            #send message to curr user
            update.message.reply_text(f'''
                                    We've found a match - meet @{match_username}!
                                    \nName: {match_name}
                                    \nPreferred pronouns: {match_gender}
                                    \nAge group: {match_agegroup}
                                    \nBio: {match_bio}
                                    \nGo ahead and drop {match_name} a text by tapping on @{match_username} to say hello :-) Happy chatting and enjoy the party!''')

            #send message to match
            message = (f'''
                        We've found a match - meet @{user.username}!
                        \nName: {context.user_data['name']}
                        \nPreferred pronouns: {context.user_data['gender']}
                        \nAge group: {context.user_data['age']}
                        \nBio: {context.user_data['bio']}
                        \nGo ahead and drop {context.user_data['name']} a text by tapping on @{user.username} to say hello :-) Happy chatting and enjoy the party!''')

            context.bot.send_message(match_chatid, message)
            matched = 1 #current User has been matched
            insertNewMatch(update, match_username)
            logger.info(f"User @{match_username} has been matched with user @{user.username}")

        else:
            update.message.reply_text('Waiting for match...')
            logger.info("Only identical matches available, waiting for further match requests")
            matched = 0

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


random_replies = [
    "I don't understand leh, try another reply",
    "Huh what you saying",
    "Happy national day! Shiok got public holiday",
    "Why you keep messaging me",
    "Still waiting for match? Check out what's happening on https://www.nationaldayparty.com/"
]

random_stickers = [
    "CAACAgUAAxkBAAEBJdlfKZ2zeT8Cosuodfpqz-ukzYJ6NAACFQADTn4wGLA4KMnhWKFZGgQ",
    "CAACAgUAAxkBAAEBJd1fKZ3LKf3kA_8V5Iqjhg_-YCYY4QACKAADTn4wGKcqT6Y78XK-GgQ",
    "CAACAgUAAxkBAAEBJd9fKZ3YJfH2U_jzbkXQC2cpZZp2zgACGgADTn4wGC-PBAaiswILGgQ",
    "CAACAgUAAxkBAAEBJeFfKZ3rn_kN84_CrqI5w2v0659pCwACJgADTn4wGG8kWg49qba_GgQ",
    "CAACAgUAAxkBAAEBJeNfKZ33uWZlR-RUKHWXS682drkAAYcAAjcAA05-MBjPxtwEbufPZRoE",
    "CAACAgUAAxkBAAEBJeVfKaI2zjrEIilbdmKh0q13ZeyE-gACIAADTn4wGFGMZSkhSNi-GgQ",
    "CAACAgUAAxkBAAEBJedfKaI6zOT06Qw6G1zBQUF_6U5RjQACHwADTn4wGDE22lRtk0hQGgQ",
    "CAACAgUAAxkBAAEBJelfKaJDGb8M98UiG6g1YKB3X1SwaAACFgADTn4wGNPkI4-y1Es5GgQ",
    "CAACAgUAAxkBAAEBJetfKaJI1Z-1EkxpueFXVbf3x8pa1wACVQADTn4wGBFEEQQx3ytSGgQ",
    "CAACAgUAAxkBAAEBJfVfKaMR8Y22ZFBsH3v48nu-MFSDVgACIQADXJ7ICTdvc98aneCaGgQ",
    "CAACAgUAAxkBAAEBJflfKaM72eyWdLJbeLUlooR2_WduhgACHwADXJ7ICbDLXkyMiIb6GgQ"
]

def catch_random(update, context):
    """
    Randomize replies to unrecognized commands or messages with Singapore-themed stickers/text
    """
    user = update.message.from_user
    logger.info("User %s sent an unrecognized command %s", user.first_name, update.message.text)

    reply_keyboard = [["/start", "Knock knock"]]

    reply = random.choice(random_replies)
    sticker = random.choice(random_stickers)

    if random.choice([0,1,2])==0:
        update.message.reply_text(reply,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    else:
        update.message.reply_sticker(sticker,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))


add_start_cmd = CommandHandler('start', start)
add_disclaimer = MessageHandler(Filters.text & ~Filters.command, disclaimer)
add_rules = MessageHandler(Filters.text & ~Filters.command, rules)
add_intro = MessageHandler(Filters.text & ~Filters.command, intro)
add_name = MessageHandler(Filters.text & ~Filters.command, name)
add_gender = MessageHandler(Filters.text & ~Filters.command, gender)
add_age = MessageHandler(Filters.text & ~Filters.command, age)
add_bio = MessageHandler(Filters.text & ~Filters.command, bio)
add_catch_random = MessageHandler(Filters.all, catch_random)

if __name__ == "__main__":
    print(isMatchAvailable())
    print(retrieveMatchRow())
