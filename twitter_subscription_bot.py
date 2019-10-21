#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import requests
from bs4 import BeautifulSoup
import traceback as tb
import time

DEBUG_GROUP = -1001198682178  # @bot_debug
START_MESSAGE = ('Send link to the bot using command: `/export_youtube_playlist'
								 ' playlist_link`. If you do this inside group/channel, please '
								 'add this bot as admin.')
SLEEP_TIME = 10  # unit: second


def linkFormat(link):
	if '://' not in link:
		return 'https://' + link
	return link


def trimURL(link):
	if '://' not in link:
		return link
	loc = link.find('://')
	return link[loc + 3:]


def getVideoList(soup):
	table = soup.find('table', id='pl-video-table')

	for a in table.find_all('a', class_='pl-video-title-link'):
		href = a['href']
		href = href[:href.find('&')]
		url = 'www.youtube.com' + href
		yield url


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
	link = linkFormat(msg.text.split()[1])
	r = requests.get(link)
	soup = BeautifulSoup(r.text, 'html.parser')
	result = list(getVideoList(soup))
	if len(result) == 0:
		msg.reply_text('Can not find any video', quote=False)
		msg.delete()
	setInfo(msg, bot, link, soup)
	for url in result:
		msg.reply_text(url, quote=False)
		time.sleep(SLEEP_TIME)
	msg.delete()


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


with open('TOKEN') as f:
	TOKEN = f.readline().strip()

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(MessageHandler(Filters.command, export))
dp.add_handler(MessageHandler(Filters.private, start))

updater.start_polling()
updater.idle()
