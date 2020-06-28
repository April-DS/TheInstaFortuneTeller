from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler
import subprocess
import glob
import json
from pprint import pprint
import pandas as pd
import hashtag_recommender


#import emoji
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
my_token = token
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ACCOUNT, CAPTION, PHOTO, ISCAROUSEL, WEEKDAY, HOUR1 = range(6)


def start(update, context):
    context.bot.sendSticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAL7X173OnG4BB0gyAhzmKZswHgR57fdAAI8AAOWn4wOzE_E-soOU2saBA')
    update.message.reply_text(
        'Hi! I am a fortune teller \U0001F9DB.\n'
        'I predict number of likes and propose best hashtags for your future post!\n'
        'You may use /stop command if it becomes too much for you.\n\n'
        'What is your instagram account?')
    return ACCOUNT


def account(update, context):
    user = update.message.from_user
    logger.info("Account of %s: %s", user.first_name, update.message.text)
    username = update.message.text
    with open('./User_info/username.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(username)
    update.message.reply_text('I want to know more... But I can lift the veil of secrecy..\n'
                              'Influencers \U0001F466 \U0001F467 usually use up to 300 characters in their captions.\n\n'
                              'Now it\'s your turn to type the caption for your future post!',
                              reply_markup=ReplyKeyboardRemove())

    return CAPTION

def caption(update, context):
    user = update.message.from_user
    logger.info("Caption of %s: %s", user.first_name, update.message.text)
    caption = update.message.text
    with open('./User_info/caption.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(caption)
    update.message.reply_text('Video gets more likes than still images...\n\n'
                              'Please, also send me the photo \U0001F5BC or a screenshot of the video \U0001F39E, which you are about to publish.\n'
                              'I want to check it up with my coffee grounds...',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO

def photo(update, context):
    user = update.message.from_user
    reply_keyboard = [['Carousel', 'Not Carousel']]
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('./User_info/user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'In my crystal ball \U0001F52E I see how people leave more likes when they swipe it like a carousel..\U0001F3A1	\n\n'
        'By the way, will it be a carousel?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ISCAROUSEL

def iscarousel(update, context):
    user = update.message.from_user
    reply_keyboard = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    logger.info("Carousel of %s: %s", user.first_name, update.message.text)
    carousel = update.message.text
    with open('./User_info/carousel.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(carousel)
    update.message.reply_text(
        'My cat \U0001F63C has just told me that it\'s better NOT to post your pictures on Saturday...\n\n'
        'When are you planning to publish your post?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return WEEKDAY

def weekday(update, context):
    user = update.message.from_user
    logger.info("Weekday of %s: %s", user.first_name, update.message.text)
    weekday = update.message.text
    with open('./User_info/weekday.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(weekday)
    update.message.reply_text(
        'My ancectors \U0001F9D3 \U0001F475 used to publish their posts between 17 and 20,  which is still a wise advice!'
        'At which hour are you planning to publish your post? \U0001F562 (0-23):',
        reply_markup=ReplyKeyboardRemove())

    return HOUR1

def hour1(update, context):
    user = update.message.from_user
    logger.info("Hour of %s: %s", user.first_name, update.message.text)
    hour1 = update.message.text
    with open('./User_info/hour.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(hour1)
    update.message.reply_text(
        'Please relax in your comortable chair while I forsee the future..\n'
        'Don\'t play play with me! \U0001F9DB')
    context.bot.sendSticker(chat_id=update.effective_chat.id,sticker='CAACAgIAAxkBAAL7bF73Q2SObFBa3WTr6hTocWVBCA78AAJGAAOWn4wO7zFng1lRJ54aBA')
    predict_range, predict_likes, predict_engagement, what_on_photo_message, hashtags_message_useful, hashtags_message_other = hashtag_recommender.start_all()
    update.message.reply_text(
        'My crystal ball \U0001F52E has shown me the best for your future post',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(predict_range)
    update.message.reply_text(predict_likes)
    update.message.reply_text(predict_engagement)

    update.message.reply_text(what_on_photo_message)
    update.message.reply_text(hashtags_message_useful)
    update.message.reply_text(hashtags_message_other)
    update.message.reply_text(
        'Enter /start if you are brave enough for one more session...')

    return ConversationHandler.END

def stop(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope I can make you popular on instagram some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(my_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states ACCOUNT, CAPTION, PHOTO, ISCAROUSEL, WEEKDAY, HOUR1
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ACCOUNT: [CommandHandler('stop', stop),
                    MessageHandler(Filters.text, account)],
                    
            CAPTION: [CommandHandler('stop', stop),
                    MessageHandler(Filters.all, caption)],
                    
            PHOTO: [CommandHandler('stop', stop),
                    MessageHandler(Filters.photo, photo)],

            ISCAROUSEL: [CommandHandler('stop', stop),
                    MessageHandler(Filters.text, iscarousel)],

            WEEKDAY: [CommandHandler('stop', stop),
                    MessageHandler(Filters.text, weekday)],

            HOUR1: [CommandHandler('stop', stop),
                    MessageHandler(Filters.text, hour1)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()