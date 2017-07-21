#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) 

def start(bot, update):
    print "start message triggered"
    #update.message.reply_text('Hello World!' + u'\U000026BD')
    s = ""
    s += u'\U0001F687' + '--\t' + u'소태Sotae\t' + '--' + '\n'
    s +=  '--\t' + '*Sotae* <a href="http://www.example.com/">inline URL</a> \t' + '--' + '\n'
    s +=  '--\t' + 'Sotae`inline fixed-wdith code`' + '--' + '\n'
    s += u'\U0001F687' + '--\t' + 'Sotae\t' + '--' + '\n'
    s += '--\t' + 'Sotae\t' + '--' + '\n'
    update.message.reply_text(s, parse_mode='Markdown')
    bot.send_message(chat_id=update.message.chat_id,text="Example text with a phone [+79991234567](tel:+79991234567)", parse_mode='Markdown')




def hello(bot, update):
    print 'hello message triggered'
    update.message.reply_text(
        "Hello {}".format(update.message.from_user.first_name))

def echo_func(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def caps(bot, update, args):
	text_caps = ' '.join(args).upper()
	bot.send_message(chat_id=update.message.chat_id, text=text_caps)

#ketitestbot
#updater = Updater('285382875:AAEOqprHI7ydnU2B3G5S5mgtF-Fdb_U8lSg')

#gwangjubot
updater = Updater('444481571:AAH7A2MKPnhgfgaxxyKABOpDArjAWWuEU24')


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(MessageHandler(Filters.text, echo_func))

updater.dispatcher.add_handler(CommandHandler('caps', caps, pass_args=True))

updater.start_polling()
updater.idle()

