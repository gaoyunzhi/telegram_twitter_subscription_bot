import os
import sys

def kill():
	os.system("ps aux | grep python | grep twitter_subscription_bot | awk '{print $2}' | xargs kill -9")

def setup():
	kill()
	if 'kill' in sys.argv:
		return

	RUN_COMMAND = 'nohup python3 -u twitter_subscription_bot.py &'

	if 'debug' in sys.argv:
		os.system(RUN_COMMAND[6:-2])
	else:
		os.system(RUN_COMMAND)


if __name__ == '__main__':
	setup()