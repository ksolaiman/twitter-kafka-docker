# from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import tweepy
import json
from kafka import KafkaProducer
import os
from urllib import request

##########################################################################
num_of_tweets=10000 # enter number of tweets x 100 that need to be extracted

#### e.g. value of 3 would return max of 300 tweets
##########################################################################

data = {}
exec(compile(open("app_tags.py", "r").read(), "app_tags.py", 'exec'))

# update api url
# data = json.load(request.urlopen("http://127.0.0.1:5000/tags"))

tags = data['tag'][0]

tagsToSearch = ' OR '.join(tags)
#### sample data -
#  movienames='#moana OR #doctorstrange OR #allied OR #arrivalmovie OR #badsanta2 OR #almostchristmasmovie OR #assassinscreed  OR #collateralbeauty  OR #fantasticbeastsandwheretofindthem  OR #jackie  OR #lalaland  OR #passengers  OR #rogueonestarwarsstory  OR #sing'

# tagsToSearch = '#CambMA'
print(tagsToSearch)
#-----------------------------------------------------------------------
# load  API credentials
#-----------------------------------------------------------------------
config = {}
# execfile("config.py", config)
exec(compile(open("config.py", "r").read(), "config.py", 'exec'), config)

#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
# Setup tweepy to authenticate with Twitter credentials:
auth = tweepy.AppAuthHandler(config["consumer_key"], config["consumer_secret"])
# auth.set_access_token(config["access_token"], config["access_token_secret"])

# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

# Create a producer to write json messages to kafka
#producer = KafkaProducer(bootstrap_servers=['kafka:9092'], # default is localhost:9092
#    value_serializer=lambda v: json.dumps(v).encode('utf-8'))
try:
	producer = KafkaProducer(bootstrap_servers=[""+os.environ['HOSTNAME']+":"+os.environ['PORT']+""],
							 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
except:
	print("hostname or port not set")


parent_directory = '/data/'

# f = open(parent_directory+'tweet_restful.dat','w')

i=0
# 100 is the limit API can read at a time from a search
status_cursor = tweepy.Cursor(api.search, q=tagsToSearch, result_type='recent', lang='en', count=100,
							  tweet_mode='extended')
search_results = status_cursor.iterator.next()

n_max = float('+inf')
n_min = float('-inf')
for i in range(num_of_tweets):
	count = 0
	for tweet in search_results:
		count += 1
		tweet_id = tweet._json['id']
		tweet_id_str = tweet._json['id_str']
		#print tweet['id']
		if tweet_id < n_max:
			min_id=tweet_id
			n_max = tweet_id
		if tweet_id > n_min:
			max_id=tweet_id
			n_min = tweet_id
		# f.write(str(tweet._json) + '\n')

		# Check if the tweet has already been found or not, tweet_id is a unique id for each tweet
		# Tweets can be normal tweet, extended tweet, retweets (RT) or quoted_tweets
		# https://dev.to/kehers/formatting-tweets-a-look-at-extended-tweets-retweets-and-quotes-n5j
		# We can extract each type of tweets later from reading each file
		try:
			fh = open(parent_directory + tweet_id_str+".json", "r")
		# if file not found, tweet is new, write to file + Kafka + in dictionary file
		except FileNotFoundError:
			tweet_json = json.dumps(tweet._json, indent=4)
			with open(parent_directory + tweet_id_str + ".json", "w") as jf:
				jf.write(tweet_json)
			input("wait")
			try:
				# producer.send('Twitter', tweet._json)
				producer.send(os.environ['TOPIC'], tweet._json)
			except:
				print("Set the environment variable for [TOPIC]")

			# Write into dictionary file
			# tweet_id - type - user_screen_name
			with open(parent_directory+'tweet_restful.dat','w') as f:
				f.write(tweet_id_str)
				retweeted = False
				quoted = False
				normal = False
				try:
					retweeted = tweet._json['retweeted_status']
					quoted = tweet._json['quoted_status']
				except:
					normal = True

				if retweeted:
					f.write("\t"+"Retweet")
				elif quoted:
					f.write("\t" + "Quote")
				else:
					f.write("\t" + "Original")

				f.write("\t" + tweet._json['user']['screen_name'])
				f.write('\n')

	i += 1
	print (count)
	if count == 1:
		break
	status_cursor = tweepy.Cursor(api.search, q=tagsToSearch, result_type='recent', lang='en',
								  count=100, max_id=min_id, tweet_mode='extended')
	search_results = status_cursor.iterator.next()

producer.close()