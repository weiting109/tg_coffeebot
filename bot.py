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

RULES_AGREE, PREFERENCES = range(3)

def info_to_str(user_data):
    """
    Returns user data in string format.

    e.g. to use this function
    context.user_data['age'] = 20
    update.message.reply_text(info_to_str(context.user_data))
    """
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}') #user_data[property] - value

    return "\n".join(facts).join(['\n', '\n'])

# Start callback function returns a greeting
def start(update,context):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id,text=f"Hi @{user.username}! Welcome to Better To(gather)'s party-matching bot! We'll match you with other attendees with similar hobbies or interests. Exciting hor?")

    reply_kb = [['I agree.','I do not agree.']]
    markup = ReplyKeyboardMarkup(reply_kb, one_time_keyboard=True)

    update.message.reply_text("""We want to keep our Telegram page an open chat, but we are also a “family-friendly” page, so please keep comments and wall posts clean.,
        We want you to tell us what’s on your mind or provide a platform for likeminded individuals to connect through their interests, but if it falls into any of the categories below, we want to let you know beforehand that we will have to remove it:,
        \n1. We do not allow graphic, obscene, explicit or racial comments or submissions nor do we allow comments that are abusive, hateful or intended to defame anyone or any organization.
        \n2. We do not allow third-party solicitations or advertisements. This includes promotion or endorsement of any financial, commercial or non-governmental agency. Similarly, we do not allow attempts to defame or defraud any financial, commercial or non-governmental agency.
        \n3. We do not allow comments that support or encourage illegal activity.
        \nLet’s make this a safe space for everyone! :D""",
        reply_markup=markup)

    return RULES_AGREE

def rules_agree(update,context):
    text = update.message.text
    if text == 'I do not agree.':
        update.message.reply_text("You must agree to the rules to be matched. Send \start to start again.")
        return ConversationHandler.END
    else:
        update.message.reply_text("Welcome! Let's get started.")
        return ConversationHandler.END

def main():
    # Updater continuously fetches new updates from TG to be passed to Dispatcher
    updater = Updater(token=BOT_TOKEN,use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',start)],
        states={
            RULES_AGREE: [MessageHandler(Filters.text,
                                        rules_agree)]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conv_handler)

    # Start bot
    updater.start_polling()

    # Run the bot until Ctr-C or process receives SIGINT/SIGTERM/SIGABRT
    # start_polling() is non-blocking, and will stop the bot gracefully
    updater.idle()

if __name__ == '__main__':
    main()
