from __future__ import absolute_import, print_function
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import KafkaProducer
#from kafka.client import KafkaClient
from kafka.client import SimpleClient
from kafka.consumer import SimpleConsumer
from kafka.producer import SimpleProducer
import json
# import urllib2


# update api url
#  data = json.load(urllib2.urlopen("http://127.0.0.1:5000/movies"))
#  movienames= data['moviename'][0]

#  print(movienames)
#### sample data -
#movienames=[u'#moana', u'#doctorstrange', u'#allied', u'#arrivalmovie', u'#badsanta2', u'#almostchristmasmovie', u'#assassinscreed', u'#collateralbeauty', u'#fantasticbeastsandwheretofindthem', u'#jackie', u'#lalaland', u'#passengers', u'#rogueonestarwarsstory', u'#sing']
tagsToSearch = [u'#aszoqeh']#[u'#CambMA']


# SimpleClient and SimpleProducer are deprecated, change them later if you can
client = SimpleClient('kafka:9092')
producer = SimpleProducer(client)
# Create a producer to write json messages to kafka
# producer = KafkaProducer(bootstrap_servers=['kafka:9092'], # default is localhost:9092
    # value_serializer=lambda v: json.dumps(v).encode('utf-8'))

f = open('tweet_streaming.dat','w')

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
        print(data.encode('utf-8'))
        producer.send_messages('Twitter', data.encode('utf-8')) # send_messages( String topic, bytes msg); so convert string msg to bytes first
        json.dump(data, f)
        f.write('\n')
        #print(data)
        return True

    def on_error(self, status_code):
        print(status_code)

        #if status_code == 420:
            # returning False in on_error disconnects the stream
        #    return False

        # returning non-False reconnects the stream, with backoff.

if __name__ == '__main__':
    l = StdOutListener()
    # Setup tweepy to authenticate with Twitter credentials:
    auth = OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.set_access_token(config["access_token"], config["access_token_secret"])

    stream = Stream(auth, l)
    stream.filter(track=tagsToSearch,languages=["en"])
