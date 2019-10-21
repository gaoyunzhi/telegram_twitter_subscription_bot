#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
import traceback as tb
import json
import tweepy
import threading

DEBUG_GROUP = -1001198682178  # @bot_debug
START_MESSAGE = ('Command: `/subscribe_twitter twitter_user_link`. If you do this inside group/channel, please '
								 'add this bot as admin.')


with open('CREDENTIALS') as f:
	CREDENTIALS = json.load(f)

def loadSubscription():
	try:
		with open('SUBSCRIPTION') as f:
			SUBSCRIPTION = json.load(f)
	except:
		SUBSCRIPTION = {}

def saveSubscription():
	with open('SUBSCRIPTION', 'w') as f:
		f.write(json.dump(SUBSCRIPTION))

def trimURL(link):
	if '://' not in link:
		return link
	loc = link.find('://')
	return link[loc + 3:]

def setInfo(msg, bot, link, soup):
	try:
		if msg.from_user and msg.chat.id == msg.from_user.id:
			return
		info = 'All videos from Youtube playlist: ' + trimURL(link)
		try:
			bot.set_chat_description(msg.chat.id, info)
		except:
			pass
		fist_reply = msg.reply_text(info, quote=False)
		bot.pin_chat_message(msg.chat.id, fist_reply.message_id)
		title = soup.find('h1', class_='pl-header-title').text
		bot.set_chat_title(msg.chat.id, title)
	except Exception as e:
		print(e)
		tb.print_exc()


def exportImp(msg, bot):
	command, link = msg.text.split()
	if 'unsubscribe' in command:



def export(update, context):
	try:
		if 'start' in update.effective_message.text:
			return update.effective_message.reply_text(START_MESSAGE, quote=False)
		exportImp(update.effective_message, context.bot)
	except Exception as e:
		print(e)
		tb.print_exc()


def start(update, context):
	try:
		if 'start' in update.effective_message.text:
			update.effective_message.reply_text(START_MESSAGE, quote=False)
	except Exception as e:
		print(e)
		tb.print_exc()

updater = Updater(CREDENTIALS['bot_token'], use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.command, export))
dp.add_handler(MessageHandler(Filters.private, start))

def telebot_poll(updater):
	updater.start_polling()
	updater.idle()

t1 = threading.Thread(target=telebot_poll, arg=(updater,))
t1.start()

def twitter_push(updater):
	while True:
	    try:
	        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	        auth.set_access_token(access_token, access_token_secret)
	        api = tweepy.API(auth)
	        print('start a new connection')
	        myStreamListener = MyStreamListener()
	        myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
	        # 实时监测我们关注的这些推特自媒体账号
	        myStream.filter(follow=accountIds)
	    except Exception as e: #抓取到一段时间都会断开连接,睡眠一段时间再重新连接
	        time.sleep(251)
	        print(e)

t2 = threading.Thread(target=twitter_push, arg=(updater,))
t2.start()

