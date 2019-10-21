import os
import sys
import json

REQUIRED_KEYS = set(['bot_token', 'twitter_consumer_key', 'twitter_consumer_secret', 'twitter_access_token', 'twitter_access_secret'])

def setup(is_reload = False):
	RUN_COMMAND = 'nohup python3 twitter_subscription_bot.py &'

	CREDENTIALS = {}
	try:
		with open('CREDENTIALS') as f:
			CREDENTIALS = json.load(f)
	except:
		pass

	for key in REQUIRED_KEYS:
		if key not in CREDENTIALS:
			print('ERROR: please fill the CREDENTIALS file in json format, required keys : ' + ', '.join(sorted(REQUIRED_KEYS)))
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