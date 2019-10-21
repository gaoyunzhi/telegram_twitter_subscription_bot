#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
import traceback as tb
import json
import tweepy
import threading
import time

START_MESSAGE = ('Command: `/subscribe_twitter twitter_user_link`. If you do this inside group/channel, please '
								 'add this bot as admin.')


with open('CREDENTIALS') as f:
	CREDENTIALS = json.load(f)

try:
	with open('SUBSCRIPTION') as f:
		SUBSCRIPTION = json.load(f)
except:
	SUBSCRIPTION = {}

def saveSubscription():
	with open('SUBSCRIPTION', 'w') as f:
		f.write(json.dumps(SUBSCRIPTION, sort_keys=True, indent=2))

def getTwitterSubscription():
	print(SUBSCRIPTION)
	account_ids = set()
	for subs in SUBSCRIPTION.values():
		account_ids.update(subs.keys())
	return account_ids

def getSubscribers(tuid):
	# if this bot does grow larger, we will need a relational db.
	chat_ids = set()
	for chat_id, subs in SUBSCRIPTION.items():
		if tuid in subs:
			chat_ids.add(chat_id)
	return chat_ids

def getTContent(data):
	if data['truncated']:
		return data['extended_tweet']['full_text']
	else:
		return data['text']

def getContent(data):
	if data['retweeted_status']:
		return getTContent(data['retweeted_status'])
	else:
		return getTContent(data)

class TwitterListener(tweepy.StreamListener):
	def on_data(self, data):
		tweet_data = json.loads(data)
		if tweet_data['in_reply_to_status_id_str']:
			return
		tuid = tweet_data['user']['id_str']
		chat_ids = getSubscribers(tuid)
		if not chat_ids:
			return
		for chat_id in chat_ids:
			updater.bot.send_message(chat_id=chat_id, text=getContent(tweet_data))

def twitterPushImp():
	global twitterApi
	global twitterStream
	auth = tweepy.OAuthHandler(CREDENTIALS['twitter_consumer_key'], CREDENTIALS['twitter_consumer_secret'])
	auth.set_access_token(CREDENTIALS['twitter_access_token'], CREDENTIALS['twitter_access_secret'])
	twitterApi = tweepy.API(auth)
	twitterListener = TwitterListener()
	twitterStream = tweepy.Stream(auth=twitterApi.auth, listener=twitterListener)
	twitterStream.filter(follow=getTwitterSubscription())

def updateSubInfo(msg, bot):
	try:
		saveSubscription()
		twitterPushImp()
		info = 'Twitter Subscription List: \n' +  '\n'.join(sorted(SUBSCRIPTION[str(msg.chat_id)].values()))
		msg.reply_text(info, quote=False, parse_mode='Markdown', disable_web_page_preview=True)
	except Exception as e:
		print(e)
		tb.print_exc()

def getTwitterUser(link):
	screenname = [x for x in link.split('/') if x][-1]
	user = twitterApi.get_user(screenname)
	return str(user.id), '[' + user.name + '](twitter.com/' + str(user.screen_name) + ')'

def exportImp(msg, bot):
	command, link = msg.text.split()
	if not 'subscribe' in command:
		msg.reply_text(START_MESSAGE, quote=False)
		return
	tuid, desc = getTwitterUser(link)
	if not tuid:
		return
	SUBSCRIPTION[str(msg.chat_id)] = SUBSCRIPTION.get(str(msg.chat_id), {})
	subs = SUBSCRIPTION[str(msg.chat_id)]
	if 'unsubscribe' in command:
		if not subs or tuid not in subs:
			return msg.reply_text('FAIL. No such subscription', quote=False)
		del subs[tuid]
		updateSubInfo(msg, bot)
		return
	subs[tuid] = desc
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

def twitterPush():
	while True:
		try:
			twitterPushImp()
		except Exception as e:
			time.sleep(30)
			print(e)
			tb.print_exc()

t2 = threading.Thread(target=twitterPush)
t2.start()

twitterPushImp()

updater.start_polling()
updater.idle()

