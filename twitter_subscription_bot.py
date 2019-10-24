#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
import traceback as tb
import json
import tweepy
import threading
import export_to_telegraph

START_MESSAGE = ('Command: `/subscribe_twitter twitter_user_link`. If you do this inside group/channel, please '
								 'add this bot as admin.')

twitterStream = None

record = {}

with open('CREDENTIALS') as f:
	CREDENTIALS = json.load(f)

export_to_telegraph.token = CREDENTIALS.get('telegraph')

try:
	with open('SUBSCRIPTION') as f:
		SUBSCRIPTION = json.load(f)
except:
	SUBSCRIPTION = {}

def saveSubscription():
	with open('SUBSCRIPTION', 'w') as f:
		f.write(json.dumps(SUBSCRIPTION, sort_keys=True, indent=2))

def getTwitterSubscription():
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

def getContent(data):
	if data.get('retweeted_status'):
		data = data['retweeted_status']
	text = data.get('extended_tweet', {}).get('full_text')
	if text:
		return text
	return data.get('text')

def getUrlInfo(tweet_data):
	r = {}
	url_data = tweet_data.get('entities', {}).get('urls', []) + \
		tweet_data.get('retweeted_status', {}).get('entities', {}).get('urls', []) + \
		tweet_data.get('extended_tweet', {}).get('entities', {}).get('urls', []) + \
		tweet_data.get('retweeted_status', {}).get('extended_tweet', {}).get('entities', {}).get('urls', [])
	for url in url_data:
		r[url['url']] = url['expanded_url']
	return r

def trimUrl(url):
	if '://' not in url:
		return url
	return url[url.find('://') + 3:]

def getKey(content, url_info):
	for url in url_info:
		if url in content:
			return url_info[url]
	return content[:20]

def replaceUrl(content, url, new_url):
	x = content.find(url)
	if x > 0 and content[x - 1] not in [' ', '\n']:
		new_url = ' ' + new_url
	if 'photo' in new_url.split():
		new_url = ''
	return content.replace(url, new_url)

def formatContent(content, url_info):
	for url in url_info:
		if url not in content:
			continue
		real_url = url_info[url]
		if 'photo' in real_url.split('/'):
			content = content.replace(url, '')
			continue
		telegraph_url = export_to_telegraph.export(real_url)
		if telegraph_url:
			content = replaceUrl(content, url, telegraph_url)
			continue
		if len(real_url) < len(url) + 10:
			content = replaceUrl(content, url, trimUrl(real_url))
			continue
		content = replaceUrl(content, url, trimUrl(url))
	return content

class TwitterListener(tweepy.StreamListener):
	def on_data(self, data):
		global record
		try:
			tweet_data = json.loads(data)
			with open('tmp', 'w') as f:
				f.write(str(tweet_data))
			if tweet_data.get('in_reply_to_status_id_str') or not tweet_data.get('user') or \
				tweet_data.get('quoted_status'):
				return
			with open('tmp2', 'w') as f:
				f.write(str(tweet_data))
			tuid = tweet_data['user']['id_str']
			chat_ids = getSubscribers(tuid)
			if not chat_ids:
				return
			with open('tmp3', 'w') as f:
				f.write(str(tweet_data))
			content = getContent(tweet_data)
			url_info = getUrlInfo(tweet_data)
			key_suffix = getKey(content, url_info)
			content = tweet_data['user']['name'] + ' | ' + formatContent(content, url_info)
			for chat_id in chat_ids:
				key = str(chat_id) + key_suffix
				r = updater.bot.send_message(chat_id=chat_id, text=content)
				if key in record:
					updater.bot.delete_message(chat_id=chat_id, message_id=record[key])
				record[key] = r['message_id']
		except Exception as e:
			print(e)
			tb.print_exc()

	def on_error(self, status_code):
		print('on_error = ' + str(status_code))
		tb.print_exc()

def twitterPush():
	global twitterStream
	global twitterApi
	print('loading/reloading twitter subscription')
	if twitterStream:
		twitterStream.disconnect()
	twitterListener = TwitterListener()
	twitterStream = tweepy.Stream(auth=twitterApi.auth, listener=twitterListener)
	twitterStream.filter(follow=getTwitterSubscription())

def twitterRestart():
	t = threading.Thread(target=twitterPush)
	t.start()

def updateSubInfo(msg, bot):
	try:
		saveSubscription()
		twitterRestart()
		info = 'Twitter Subscription List: \n' +  '\n'.join(sorted(SUBSCRIPTION[str(msg.chat_id)].values()))
		msg.reply_text(info, quote=False, parse_mode='Markdown', disable_web_page_preview=True)
	except Exception as e:
		print(e)
		tb.print_exc()

def getTwitterUser(link):
	global twitterApi
	screenname = [x for x in link.split('/') if x][-1]
	user = twitterApi.get_user(screenname)
	return str(user.id), '[' + user.name + '](twitter.com/' + str(user.screen_name) + ')'

def manageImp(msg, bot):
	if len(msg.text.split()) != 2:
		msg.reply_text(START_MESSAGE, quote=False)
		return
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
	if tuid in subs:
		return msg.reply_text('FAIL. Already subscribed', quote=False)
	subs[tuid] = desc
	updateSubInfo(msg, bot)
	return

def manage(update, context):
	try:
		if 'start' in update.effective_message.text:
			return update.effective_message.reply_text(START_MESSAGE, quote=False)
		manageImp(update.effective_message, context.bot)
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

dp.add_handler(MessageHandler(Filters.command, manage))
dp.add_handler(MessageHandler(Filters.private, start))

auth = tweepy.OAuthHandler(CREDENTIALS['twitter_consumer_key'], CREDENTIALS['twitter_consumer_secret'])
auth.set_access_token(CREDENTIALS['twitter_access_token'], CREDENTIALS['twitter_access_secret'])
twitterApi = tweepy.API(auth)

def twitterBackgroudRestart():
	global twitterStream
	try:
		if not twitterStream or not twitterStream.running:
			twitterRestart()
	except Exception as e:
		print(e)
		tb.print_exc()
	threading.Timer(10 * 60, twitterBackgroudRestart).start()

twitterBackgroudRestart()

updater.start_polling()
updater.idle()

