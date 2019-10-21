import os
import sys
import json

def setup(is_reload = False):
	RUN_COMMAND = 'nohup python3 twitter_subscription_bot.py &'

	CREDENTIALS = {}
	try:
		with open('CREDENTIALS') as f:
			CREDENTIALS = json.load(f)
	except:
		pass

	if not CREDENTIALS['bot_token'] or not CREDENTIALS['twitter_token']:
		print('ERROR: please fill the CREDENTIALS file in json format, with bot_token and twitter_token.')
		return

	if not is_reload:
		os.system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
		os.system('python3 get-pip.py')
		os.system('rm get-pip.py')

		os.system('pip3 install -r requirements.txt')
		os.system('pip3 install python-telegram-bot --upgrade') # need to use some experiement feature, e.g. message filtering
			
	# kill the old running bot if any. If you need two same bot running in one machine, use mannual command instead
	os.system('ps aux | grep python | grep twitter_subscription_bot | awk '{print $2}' | xargs kill -9')
	return os.system(RUN_COMMAND)


if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1] == 'reload')
	else:
		setup('')