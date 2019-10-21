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

def getTwitterSubscription():
	account_ids = set()
	for _, ids in SUBSCRIPTION:
		account_ids.update(ids)
	return account_ids

def trimURL(link):
	if '://' not in link:
		return link
	loc = link.find('://')
	return link[loc + 3:]

def updateSubInfo(msg, bot):
	try:
		if msg.from_user and msg.chat.id == msg.from_user.id:
			return
		info = 'Twitter Subscription List: \n' +  
		msg.reply_text(info, quote=False)
	except Exception as e:
		print(e)
		tb.print_exc()


def exportImp(msg, bot):
	command, link = msg.text.split()
	if not 'subscribe' in command:
		msg.reply_text(START_MESSAGE, quote=False)
		return
	tid = getTwitterId(link)
	if not tid:
		return
	sub_list = SUBSCRIPTION[str(msg.chat_id)]
	if 'unsubscribe' in command:
		if not sub_list or str(tid) not in sublist:
			return msg.reply_text('FAIL. No such subscription', quote=False)
		sublist.remove(str(tid))
		saveSubscription()
		twitterStream.filter(follow=getTwitterSubscription())
		updateSubInfo(msg, bot)
		return
	sub_list.append(str(tid))
	saveSubscription()
	twitterStream.filter(follow=getTwitterSubscription())
	updateSubInfo(msg, bot)
	return




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

def twitter_push(updater):
	while True:
	    try:
	        auth = tweepy.OAuthHandler(CREDENTIALS['twitter_consumer_key'], CREDENTIALS['twitter_consumer_secret'])
	        auth.set_access_token(CREDENTIALS['twitter_access_token'], CREDENTIALS['twitter_access_secret'])
	        twitterApi = tweepy.twitterApi(auth)
	        twitterListener = TwitterListener()
	        twitterStream = tweepy.Stream(auth=twitterApi.auth, listener=twitterListener)
	        twitterStream.filter(follow=getTwitterSubscription())
	    except Exception as e: #抓取到一段时间都会断开连接,睡眠一段时间再重新连接
	        time.sleep(251)
	        print(e)

t2 = threading.Thread(target=twitter_push, arg=(updater,))
t2.start()

def telebot_poll(updater):
	updater.start_polling()
	updater.idle()

t1 = threading.Thread(target=telebot_poll, arg=(updater,))
t1.start()

