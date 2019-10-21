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
	for _, subs in SUBSCRIPTION:
		account_ids.update(subs.keys())
	return account_ids

def getSubscribers(tid):
	# if this bot does grow larger, we will need a relational db.
	chat_ids = set()
	for chat_id, subs in SUBSCRIPTION:
		if tid in subs:
			chat_ids.add(chat_id)
	return chat_ids

def updateSubInfo(msg, bot):
	try:
		saveSubscription()
		twitterStream.filter(follow=getTwitterSubscription())
		info = 'Twitter Subscription List: \n' +  '\n'.join(sorted(SUBSCRIPTION[str(msg.chat_id)].values()))
		msg.reply_text(info, quote=False, parse_mode='Markdown', disable_web_page_preview=True)
	except Exception as e:
		print(e)
		tb.print_exc()

def getTwitterUser(link):
	screenname = [x for x in link.split('/') if x][-1]
	user = twitterApi.get_user(screenname)
	return str(user.id), ''[' + user.name + '](twitter.com/' + str(user.screen_name) + ')''

def exportImp(msg, bot):
	command, link = msg.text.split()
	if not 'subscribe' in command:
		msg.reply_text(START_MESSAGE, quote=False)
		return
	tid, desc = getTwitterId(link)
	if not tid:
		return
	subs = SUBSCRIPTION[str(msg.chat_id)]
	if 'unsubscribe' in command:
		if not subs or tid not in subs:
			return msg.reply_text('FAIL. No such subscription', quote=False)
		del subs[tid]
		updateSubInfo(msg, bot)
		return
	subs[tid] = desc
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

class TwitterListener(tweepy.StreamListener):
    def on_data(self, data):
        tweet_data = json.loads(data)
        if tweet_data['in_reply_to_status_id_str']:
            return
        tid = tweet_data['user']['id_str']
        chat_ids = getSubscribers(tid)
        if not chat_ids:
        	return
        if user_id in accountIds:
            user_screenname = tweet_data['user']['screen_name']
            tweet_id = tweet_data['id_str']
            # 获取tweet内容
            tweet_content = ''
            if tweet_data['truncated']:
                tweet_content = tweet_data['extended_tweet']['full_text']
            else:
                tweet_content = tweet_data['text']
            # 推送这个推特链接到telegram频道
            tweet_link = 'https://twitter.com/' + user_screenname + '/status/' + tweet_id
            is_retweet = False
            try:
                if tweet_data['retweeted_status']:
                    is_retweet = True
                    tweet_id = tweet_data['retweeted_status']['id_str']
                    user_screenname = tweet_data['retweeted_status']['user']['screen_name']
                    tweet_link = 'https://twitter.com/' + user_screenname + '/status/' + tweet_id
                    if tweet_data['retweeted_status']['truncated']:
                        tweet_content = '(' + tweet_data['user']['name'] + ' 转) ' + tweet_data['retweeted_status']['extended_tweet']['full_text']
                    else:
                        tweet_content = '(' + tweet_data['user']['name'] + ' 转) ' + tweet_data['retweeted_status']['text']

            except Exception as e:
                print(e)
                pass

            # 去除内容中的链接
            # tweet_content = re.sub(r"http\S+", "", tweet_content)
            # tweet_content = re.sub(r"RT +@[^ :+]+:?", "", tweet_content)
            tweet_content_size = getsizeof(tweet_content)
            # print(tweet_content)
            message = tweet_content + "\n" + tweet_link
            if tweet_content_size <= 180:
                if is_retweet:
                    message = '(' + tweet_data['user']['name'] + ' 转)' + " \n" + tweet_link
                else:
                    message = tweet_link
            # 请私聊我获取{{bot_token}}
            # print(tweet_data)
            # print(message)
            requests.post("https://api.telegram.org/{{bot_token}}/sendMessage", data={'chat_id': '@tweet_push', 'text': message, 'disable_web_page_preview': False})

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

