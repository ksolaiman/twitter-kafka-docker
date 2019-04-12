# from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import tweepy
import json
from kafka import KafkaProducer
# import urllib2

##########################################################################

num_of_tweets=10000 # enter number of tweets x 100 that need to be extracted

#### e.g. value of 3 would return max of 300 tweets
##########################################################################

# update api url
#  data = json.load(urllib2.urlopen("http://127.0.0.1:5000/movies"))

#  movienames= data['moviename'][0]
# print movienames
#  movienames= ' OR '.join(movienames)
#### sample data -
#  movienames='#moana OR #doctorstrange OR #allied OR #arrivalmovie OR #badsanta2 OR #almostchristmasmovie OR #assassinscreed  OR #collateralbeauty  OR #fantasticbeastsandwheretofindthem  OR #jackie  OR #lalaland  OR #passengers  OR #rogueonestarwarsstory  OR #sing'

tagsToSearch = '#CambMA'
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
auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])

# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

# Create a producer to write json messages to kafka
producer = KafkaProducer(bootstrap_servers=['kafka:9092'], # default is localhost:9092
    value_serializer=lambda v: json.dumps(v).encode('utf-8'))

f = open('/data/tweet_restful.dat','w')

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
		#print tweet['id']
		if tweet_id < n_max:
			min_id=tweet_id
			n_max = tweet_id
		if tweet_id > n_min:
			max_id=tweet_id
			n_min = tweet_id
		f.write(str(tweet._json) + '\n')
		producer.send('Twitter', tweet._json)

	f.write('\n')

	i += 1
	print (count)
	if count == 1:
		break
	status_cursor = tweepy.Cursor(api.search, q=tagsToSearch, result_type='recent', lang='en',
								  count=100, max_id=min_id, tweet_mode='extended')
	search_results = status_cursor.iterator.next()

# producer.close()