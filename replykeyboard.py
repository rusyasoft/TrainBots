#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic example for a bot that uses inline keyboards.
# This program is dedicated to the public domain under the CC0 license.

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(bot, update):
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]
    #reply_markup = InlineKeyboardMarkup(keyboard)

    buttons = [ [u'녹동', u'소태',u'학동증심사입구'],
                [u'남광주', u'문화전당',u'금남로4가',u'금남로5가'], 
                [u'양동시장', u'돌고개', u'농성', u'화정'], 
                [u'쌍촌',u'운천', u'상무', u'김대중',u'공항'],
                [u'송정공원', u'광주송정역',u'도선', u'평동']  ]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Selected option: %s" % query.data,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


# Create the Updater and pass it your bot's token.
updater = Updater("444481571:AAH7A2MKPnhgfgaxxyKABOpDArjAWWuEU24") ##"285382875:AAEOqprHI7ydnU2B3G5S5mgtF-Fdb_U8lSg")

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_error_handler(error)

# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
