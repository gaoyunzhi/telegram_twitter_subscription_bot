import os
import sys

def kill():
	os.system("ps aux | grep python | grep twitter_subscription_bot | awk '{print $2}' | xargs kill -9")

def setup(mode = ''):
	if mode == 'kill':
		kill()
		return

	RUN_COMMAND = 'nohup python3 -u twitter_subscription_bot.py &'

	if mode != 'debug':
		r = os.system('sudo pip3 install -r requirements.txt')
		if r != 0:
			os.system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
			os.system('sudo python3 get-pip.py')
			os.system('rm get-pip.py')
			os.system('sudo pip3 install -r requirements.txt')
	try:
		from telegram.ext import Updater, MessageHandler, Filters
	except:
		os.system('sudo pip3 install python-telegram-bot --upgrade') # need to use some experiement feature, e.g. message filtering
	
	kill()

	if mode == 'debug':
		os.system(RUN_COMMAND[6:-2])
	else:
		os.system(RUN_COMMAND)


if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1])
	else:
		setup('')