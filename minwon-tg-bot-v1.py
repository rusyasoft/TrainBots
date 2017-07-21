#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic example for a bot that uses inline keyboards.
# This program is dedicated to the public domain under the CC0 license.

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Job

import paho.mqtt.client as mqtt
import json
import threading
import sys

STATIC_PASSWORD = "pusik"

def callback_minute(bot, job):
    bot.send_message(job.context, text="callback timer up !")


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


global g_update
g_update = None


def start(bot, update, args, job_queue, chat_data):
    """
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    """
    #print "args = ", args
    global g_update
    if args[0] == STATIC_PASSWORD:
        print "PASSWORD CORRECT, the bot activated !"
        g_update = update
        update.message.reply_text(u'민원 받는 모드 시작했습니다')

    #################
    #chat_id = update.message.chat_id
    #job = job_queue.run_repeating(callback_minute, 10, first=None, context=chat_id)
    #update.message.reply_text("start function!")

def stop(bot, update):
    global g_udpate
    if g_update != None:
        g_update = None
        update.message.reply_text(u'민원 받는 모드 긑었습니다')

def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Selected option: %s" % query.data,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def help(bot, update):
    update.message.reply_text(u"/start <비밀번호> 를 내고 민원 읽기 모드으로 밖월수 있습니다.")


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))

# Create the Updater and pass it your bot's token.
updater = Updater("285382875:AAEOqprHI7ydnU2B3G5S5mgtF-Fdb_U8lSg")

updater.dispatcher.add_handler(CommandHandler('start', start,
                                    pass_args=True,
                                    pass_job_queue=True,
                                    pass_chat_data=True))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_error_handler(error)


######### mqtt client #######

def status_reporter(client, topic):
    if topic == "/keti/energy/statusrequest":
        client.publish("/keti/energy/systemstatus", '{"nodename":"TelegramBotServer", "status":"on"}')
        return True
    return False

def on_connect(client, userdata, flags, rc):
    print "Connected to MQTT Broker with result code ", str(rc)

    client.subscribe("/keti/energy/minwon")
    client.subscribe("/keti/energy/statusrequest")
    print "subscribed to multiple topics"

def on_message(client, userdata, msg):
    try:
        if status_reporter(client, msg.topic) == False:
            print '-->', msg.payload
            global g_update
            if g_update != None:
                #g_update.message.reply_text(msg.payload)
                json_parsed_msg = json.loads(msg.payload)
                print 'json_parsed_msg ->',
                print json_parsed_msg
                s = u"열차번호: " + str(json_parsed_msg["trainID"]) + "\n"
                s+= u"온도: " + str(json_parsed_msg["cur_temp"]) + "F  Desired Temperature: " + str(json_parsed_msg["ask_temp"]) + "F\n"
                s+= u"습도: " + str(json_parsed_msg["cur_hum"]) + "%  Desired Humidity: " + str(json_parsed_msg["ask_hum"]) + "%\n"
                s+= u"민원 메시지: " + json_parsed_msg["message"] + "\n"
                g_update.message.reply_text(s)
    except:
        print sys.exc_info()


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect('117.16.136.173', 1883, 600)

def MQTTStarterThread():
    mqtt_client.loop_start()

t = threading.Thread(target=MQTTStarterThread())
t.start()




# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
