import sys
import argparse
import twitter

from twitter import *

token           = ""
token_key       = ""
con_secret      = ""
con_secret_key  = ""


# Argument Parsing
p = argparse.ArgumentParser(description="My great script")
#p.add_argument("sourceDir", type=str, help="source directory")
p.add_argument('--mentions', action='store_true', required=False, help='shows mentions for your account')
p.add_argument('--user', type=str, dest='user', required=False, help='shows tweets for a specific @username')
p.add_argument('--messages', action='store_true', required=False, help='shows direct messages for your account')
p.add_argument('--tweet', type=int, dest='tweet', required=False, help='shows a given tweet')
args = p.parse_args()


# Twitter API Object
t = Twitter(auth=OAuth(token, token_key, con_secret, con_secret_key))


# Print Tweet
def line_statuses(statuses, prefix=''):
    sc = 0
    output = ''
    for tweet in statuses:
        if (sc < 15):
            sc+=1
            tweet_text = tweet['text'].replace('\n', ' ').replace('\r', '')
            if prefix == 'screen_name':
                prefix = '@' + tweet['user']['screen_name'] + ' said: '
            output += prefix + tweet_text + '\n'
    return output

# Starting
print '... slurping up dah tweets.....'
print '\n'


if '--mentions' in (sys.argv):
    mentions = t.statuses.mentions_timeline()
    print '\n'
    print 'Your Mentions -------------------------------------------------------'
    print line_statuses(mentions, 'screen_name')


if '--user' in (sys.argv):
    if 'user' in args:
        user_statuses = t.statuses.user_timeline(screen_name=args.user)
        print '\n'
        print 'Tweets by ' + args.user + ' ----------------------------------------------'
        print line_statuses(user_statuses)

if '--messages' in (sys.argv):
	messages = t.direct_messages(count=10)
	print 'Your Messages ------------------------------------------------------'

	for msg in messages:
                print 'From @' + str(msg['sender_screen_name']) + ' at ' + msg["created_at"]
		#print 'From: ' + str(msg['sender_id']) + '@twitter.com' + ' at ' + msg["created_at"] + '\n'
		print msg['text']
		print '---------------------------------------------------'

if '--tweet' in (sys.argv):
	tweet = t.statuses.show(id=args.tweet)
	print 'Tweet:' + str(args.tweet) + ' ------------------------------------------'
	print '@' + tweet['user']['screen_name'] + ' said: ' + tweet['text']
	#print line_statuses(tweet)
