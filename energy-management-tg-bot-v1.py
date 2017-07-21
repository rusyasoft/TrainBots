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
import time

STATIC_PASSWORD = "pusik"

def callback_minute(bot, job):
    bot.send_message(job.context, text="callback timer up !")


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


global g_update
g_update = None

global mqtt_client

global servers_status_dict
servers_status_dict = dict()

eng2kor_dict = {'MinwonServer': u'민원서버', 'MainServer':u'매인서버', 'Gateway': u'개이트웨이'}

def reset_servers_status():
    global servers_status_dict
    for nodename in servers_status_dict:
        servers_status_dict[nodename] = 'off'


def start(bot, update, args, job_queue, chat_data):
    global g_update
    if args[0] == STATIC_PASSWORD:
        print "PASSWORD CORRECT, the bot activated !"
        g_update = update
        update.message.reply_text(u"민원 받는 모드 시작했습니다")

    #################
    #chat_id = update.message.chat_id
    #job = job_queue.run_repeating(callback_minute, 10, first=None, context=chat_id)
    #update.message.reply_text("start function!")

def stop(bot, update):
    global g_udpate
    if g_update != None:
        g_update = None
        update.message.reply_text(u'민원 받는 모드 긑었습니다\n')
		
def server_status(bot, update):
    global servers_status_dict
    if servers_status_dict is not None:
        ret_s = u"---- 서버 상태 ----\n"
        for nn in servers_status_dict:
            if nn not in eng2kor_dict:
                ret_s += str(nn) + ": " + str(servers_status_dict[nn]) + "\n"
            else:
                ret_s += eng2kor_dict[nn] + ": " + str(servers_status_dict[nn]) + "\n"
    update.message.reply_text(ret_s)


def button(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="---- Selected option ---: " % query.data,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def help(bot, update):
    help_msg = u"/start <비밀번호> 를 내고 민원 읽기 모드으로 밖월수 있습니다..\n"
    help_msg += u"/server_status 서버 상태 정보를 받기.\n"
    update.message.reply_text(help_msg)


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
updater.dispatcher.add_handler(CommandHandler('server_status', server_status))
updater.dispatcher.add_error_handler(error)


######### mqtt client #######

def status_reporter(client, topic):
    if topic == "/keti/energy/statusrequest":
        client.publish("/keti/energy/systemstatus", '{"nodename":"TelegramBotServer", "status":"on"}', 1)
        return True
    return False

def on_connect(client, userdata, flags, rc):
    print "Connected to MQTT Broker with result code ", str(rc)
    """
    res = client.subscribe("/keti/energy/minwon", 1)
    print "res = ", res
    #res = client.subscribe("/keti/energy/statusrequest")
    #print "res = ", res
    time.sleep(3)
    res = client.subscribe("/keti/energy/systemstatus", 1)
    print "res = ", res
    print "subscribed to multiple topics..."
    """

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos) )

def on_message(client, userdata, msg):
    try:
        print msg.topic, '->', str(msg.payload)
        if msg.topic == "/keti/energy/systemstatus":
            try:
                json_dict = json.loads(msg.payload)
                print 'json_dict = ', json_dict
                if 'nodename' in json_dict and 'status' in json_dict:
                    servers_status_dict[json_dict['nodename']] = json_dict['status']
                print 'servers_status_dict = ', servers_status_dict
            except:
                pass
        #elif status_reporter(client, msg.topic) == False:
        else:
            print '-->', msg.payload
            global g_update
            if g_update != None:
                #g_update.message.reply_text(msg.payload)
                json_parsed_msg = json.loads(msg.payload)
                print 'json_parsed_msg ->',
                print json_parsed_msg
                s = u"열차번호: " + str(json_parsed_msg["trainID"]) + "\n"
                s+= u"온도: " + str(json_parsed_msg["cur_temp"]) + "C\n"
                s+= u"습도: " + str(json_parsed_msg["cur_hum"]) + "%\n"
                s+= u"민원선택: " + str(json_parsed_msg["complaint"]) + "\n"
                s+= u"민원 메시지: " + json_parsed_msg["message"] + "\n"
                g_update.message.reply_text(s)
    except:
        print sys.exc_info()



mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

mqtt_client.connect('117.16.136.173', 1883, 600)

res = mqtt_client.subscribe("/keti/energy/minwon", 1)
print "minwon subscribe res = ", res
#res = client.subscribe("/keti/energy/statusrequest")
#print "res = ", res
res = mqtt_client.subscribe("/keti/energy/systemstatus", 1)
print "systemstatus subscribe res = ", res
print "subscribed to multiple topics..."
time.sleep(3)


def MQTTStarterThread():
    global mqtt_client
    print "MQTT Loop starting ..."
    mqtt_client.loop_start()
    #mqtt_client.loop_forever()
    print "MQTT Loop started ..."

def StatusRequesterThread():
    global mqtt_client
    try:
        while True:
            time.sleep(10)
            reset_servers_status()
            print "."
            mqtt_client.publish("/keti/energy/statusrequest", "status_request_msg")
            print ","
    except:
        print "Exitting !"


print "--1--"
t = threading.Thread(target=MQTTStarterThread())
#t.daemon = True
t.start()

print "--2--"


# Start the Bot
updater.start_polling()
time.sleep(5)

print "--3--"

print "--4--"

# forever cycle starts
requester_t = threading.Thread(target=StatusRequesterThread())
requester_t.daemon = True
requester_t.start()
print "--5--"



# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()

print "--6--"
