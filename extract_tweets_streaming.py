from __future__ import absolute_import, print_function
from tweepy.streaming import StreamListener
from tweepy import AppAuthHandler
from tweepy import OAuthHandler
from tweepy import Stream
from kafka.client import SimpleClient
from kafka.producer import SimpleProducer
import json
# import urllib2
import os
from ast import literal_eval
import json
from kafka import KafkaProducer

def jsonify(data):
    try:
        temp = json.loads(data)
        return temp
    except ValueError as e:
        print(e)
        return None

# update api url
#  data = json.load(urllib2.urlopen("http://127.0.0.1:5000/movies"))
#  movienames= data['moviename'][0]

data = {}
exec(compile(open("app_tags.py", "r").read(), "app_tags.py", 'exec'))

#  print(movienames)
#### sample data -
# movienames=[u'#moana', u'#doctorstrange', u'#allied', u'#arrivalmovie', u'#badsanta2', u'#almostchristmasmovie', u'#assassinscreed', u'#collateralbeauty', u'#fantasticbeastsandwheretofindthem', u'#jackie', u'#lalaland', u'#passengers', u'#rogueonestarwarsstory', u'#sing']

tagsToSearch = data['tag'][0]

# Reason it was giving wrong tweets was you were making string with u, but that's u from unicode, so just the joined
# tags separated by comma is enough, don't need next line
# WRONG : tagsToSearch = "['" + "', '".join(tags) + "']"

# tagsToSearch = [u'#aszoqeh', u'#moana']#[u'#CambMA'] #

# SimpleClient and SimpleProducer are deprecated, change them later if you can
# client = SimpleClient(os.environ['HOSTNAME']+":"+os.environ['PORT'])
# producer = SimpleProducer(client)

try:
	producer = KafkaProducer(bootstrap_servers=[""+os.environ['HOSTNAME']+":"+os.environ['PORT']+""],
							 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
except:
	print("hostname or port not set")

parent_directory = '/data/'
# f = open(parent_directory+'tweet_streaming.dat','w')

#-----------------------------------------------------------------------
# load  API credentials
#-----------------------------------------------------------------------
config = {}
# execfile("config.py", config)
exec(compile(open("config.py", "r").read(), "config.py", 'exec'), config)

class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        data = jsonify(data)

        if data is None:
            return True     # just go back from here, don't do anything

        # print(data.encode('utf-8')) # encode converts str it to bytes, but now it's obsolete, coz data is dict object now

        # producer.send_messages(os.environ['TOPIC'], data.encode('utf-8')) # send_messages( String topic, bytes msg); so convert string msg to bytes first

        tweet_id = data['id']
        tweet_id_str = data['id_str']

        print(tweet_id)
        print(os.environ['TOPIC'])

        try:
            fh = open(parent_directory + tweet_id_str + ".json", "r")
        # if file not found, tweet is new, write to file + Kafka + in dictionary file
        except FileNotFoundError:
            tweet_json = json.dumps(data, indent=4)
            print(tweet_json)
            with open(parent_directory + tweet_id_str + ".json", "w") as jf:
                jf.write(tweet_json)
            input("wait")
            try:
                producer.send(os.environ['TOPIC'], data)
            except:
                print("Set the environment variable for [TOPIC]")

            # Write into dictionary file
            # tweet_id - type - user_screen_name
            with open(parent_directory + 'tweet_streaming.dat', 'w') as f:
                f.write(tweet_id_str)
                retweeted = False
                quoted = False
                normal = False
                try:
                    retweeted = data['retweeted_status']
                    quoted = data['quoted_status']
                except:
                    normal = True

                if retweeted:
                    f.write("\t" + "Retweet")
                elif quoted:
                    f.write("\t" + "Quote")
                else:
                    f.write("\t" + "Original")

                f.write("\t" + data['user']['screen_name'])
                f.write('\n')

        # json.dump(data, f)
        # f.write('\n')
        # print(data)
        return True

    def on_error(self, status_code):
        # What each error code means
        # https: // developer.twitter.com / en / docs / tweets / filter - realtime / guides / connecting
        print(status_code)

        #if status_code == 420:
            # returning False in on_error disconnects the stream
        #    return False

        # returning non-False reconnects the stream, with backoff.

if __name__ == '__main__':
    listener = StdOutListener()
    # Setup tweepy to authenticate with Twitter credentials:
    auth = OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_token"], config["access_token_secret"])

    stream = Stream(auth, listener)
    stream.filter(track=tagsToSearch,languages=["en"])

