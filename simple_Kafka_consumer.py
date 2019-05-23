from kafka import KafkaConsumer
from json import loads
import pandas as pd
import os
import psycopg2
from psycopg2.extensions import AsIs
import json

'''
app = Flask(__name__)
@app.route('/')
def index():
    # return Response(ks(), mimetype='text/plain') # worked
    return Response(ks(), mimetype="application/json")  # worked
'''

def initialize(db_name = "tweetdata"):
    '''
    Initialize a function that takes postgres database name as arguent and sets up a the postgres connection.
    Connection to postgres database is established using psycopg2 postgres connector and cursor is initiated to run
    SQL queries. Function returns, the tweets dataframe, postgres connector and the SQL cursor as objects.
    '''
    # set-up a postgres connection
    conn = psycopg2.connect(database=db_name, user=os.environ['username'],password=os.environ['pass'],
                            host=os.environ['database_host'], port=os.environ['database_port'])
    dbcur = conn.cursor()
    print("connection successful")
    return (conn, dbcur)

def load_data(tweet, user, conn, dbcur):
    '''
    load function takes tweet and user json data, postgres connector and cursor.
    Function inserts the rows into the postgres database
    A tweet must have an id (else we return empty tweet object), a valid text and a valid user who posted it
    '''

    print(tweet)
    if tweet is None:
        pass
    elif tweet['text'] is None:
        pass
    elif tweet['user_id'] is None:
        pass
    else:
        columns = user.keys()
        values = [user[column] for column in columns]
        querystr = dbcur.mogrify("INSERT INTO twitter_user_records (%s) VALUES %s"
                                 " ON CONFLICT DO NOTHING;", (AsIs(','.join(columns)), tuple(values)))
        dbcur.execute(querystr)

        columns = tweet.keys()
        values = [tweet[column] for column in columns]
        querystr = dbcur.mogrify("INSERT INTO tweets_record (%s) VALUES %s"
                                     " ON CONFLICT DO NOTHING;", (AsIs(','.join(columns)), tuple(values)))
        dbcur.execute(querystr)
        conn.commit()

def extracttweetfeatures(message, tweet_type, tweet, user):
    '''
    extracttweetfeatures function takes json message, tweets dict and user dict as input. Output returns formatted
    tweets and user dict objects that is inserted in DB later.
    Function extracts the important features such as
    tweet text, language, country, user name, coordinates, location, retweets count. etc
    '''
    try:
        print(message['id_str'])
        tweet['id'] = message['id_str']
    except KeyError:
        tweet = None
        return
    try:
        tweet['created_at'] = message['created_at']
    except:
        tweet['created_at'] = None

    try:
        tweet['text'] = message['full_text']
    except KeyError:
        try:
            tweet['text'] = message['text']
        except KeyError:
            tweet['text'] = None

    try:
        tweet['truncated'] = message['truncated']
    except:
        tweet['truncated'] = None

    try:
        tweet['in_reply_to_status_id'] = message['in_reply_to_status_id']
    except:
        tweet['in_reply_to_status_id'] = None
    try:
        tweet['in_reply_to_user_id'] = message['in_reply_to_user_id']
    except:
        tweet['in_reply_to_user_id'] = None
    try:
        tweet['in_reply_to_screen_name'] = message['in_reply_to_screen_name']
    except:
        tweet['in_reply_to_screen_name'] = None

    try:
        tweet['user_id'] = message['user']['id_str']
        user['id'] = message['user']['id_str']
    except:
        tweet['user_id'] = user['id'] = None
    try:
        user['name'] = message['user']['name']
    except:
        user['name'] = None
    try:
        user['screen_name'] = message['user']['screen_name']
    except:
        user['screen_name'] = None
    try:
        user['location'] = message['user']['location'] if message['user']['location'] is not None else None
    except:
        user['location'] = None
    try:
        user['description'] = message['user']['description']
    except:
        user['description'] = None
    try:
        user['followers_count'] = message['user']['followers_count']
    except:
        user['followers_count'] = 0
    try:
        user['friends_count'] = message['user']['friends_count']
    except:
        user['friends_count'] = 0
    try:
        user['listed_count'] = message['user']['listed_count']
    except:
        user['listed_count'] = 0
    try:
        user['favourites_count'] = message['user']['favourites_count']
    except:
        user['favourites_count'] = 0
    try:
        user['statuses_count'] = message['user']['statuses_count']
    except:
        user['statuses_count'] = 0


    try:
        tweet['latitude'] = message['coordinates']['coordinates'][1] if message['coordinates'] != None else None
    except:
        tweet['latitude'] = None
    try:
        tweet['longitude'] = message['coordinates']['coordinates'][0] if message['coordinates'] != None else None
    except:
        tweet['longitude'] = None

    try:
        tweet['place'] = message['place']['full_name']
    except:
        tweet['place'] = 'Not available'

    try:
        if message['is_quote_status'] == 'true':
            tweet['quoted_status_id_str'] = message['quoted_status_id_str']
        else:
            tweet['quoted_status_id_str'] = None

        tweet['is_quote_status'] = message['is_quote_status']
    except:
        tweet['quoted_status_id_str'] = None
        tweet['is_quote_status'] = False

    try:
        tweet['retweet_count'] = message['retweet_count']
    except:
        tweet['retweet_count'] = 0

    try:
        tweet['favorite_count'] = message['favorite_count']
    except:
        tweet['favorite_count'] = 0

    try:
        tweet['hashtags'] = list(item['text'] for item in message['entities']['hashtags'])
    except:
        tweet['hashtags'] = None

    try:
        tweet['urls'] = list(item['url'] for item in message['entities']['urls'])
    except:
        tweet['urls'] = None

    # Each user_mentions is also a 'user' object, but for now just saving the user_name in the main table, not saving
    # them separately in 'user' table
    try:
        tweet['user_mentions'] = list(item['name'] for item in message['entities']['user_mentions'])
    except:
        tweet['user_mentions'] = None

    try:
        tweet['favorited'] = message['favorited']
    except:
        tweet['favorited'] = False
    try:
        tweet['retweeted'] = message['retweeted']
    except:
        tweet['retweeted'] = False

    try:
        tweet['lang'] = message['lang']
    except:
        tweet['lang'] = 'Not available'

    tweet['metadata'] = json.dumps(message)
    tweet['relevance'] = os.environ['relevance']
    tweet['type'] = tweet_type
    tweet['uploaded_by'] = os.environ['uploader']

def write_to_DB(consumer, conn, dbcur):
    for message in consumer:
        message = message.value         # VVI - the actual tweet json is in value

        try:
            # Retweets always contain two Tweet objects.
            if message['retweeted_status']:
                tweet = {}
                user = {}
                extracttweetfeatures(message, 'retweet', tweet, user)
                load_data(tweet, user, conn, dbcur)

                tweet = {}
                user = {}
                extracttweetfeatures(message['retweeted_status'], 'original', tweet, user)
                load_data(tweet, user, conn, dbcur)
        except KeyError:
            # Quote Tweets will contain at least two Tweet objects, and in some cases, three. The Tweet being Quoted,
            # which itself can be a Quoted Tweet, is provided in a "quoted_status" object.
            try:
                if message['quoted_status']:
                    # Retweet with comments, so save this new tweet and original
                    tweet = {}
                    user = {}
                    extracttweetfeatures(message, 'quoted', tweet, user)
                    load_data(tweet, user, conn, dbcur)

                    try:
                        if message['quoted_status']['quoted_status']:
                            tweet = {}
                            user = {}
                            extracttweetfeatures(message['quoted_status'], 'quoted', tweet, user)
                            load_data(tweet, user, conn, dbcur)

                            tweet = {}
                            user = {}
                            extracttweetfeatures(message['quoted_status']['quoted_status'], 'original', tweet, user)
                            load_data(tweet, user, conn, dbcur)
                    except:
                        tweet = {}
                        user = {}
                        extracttweetfeatures(message['quoted_status'], 'original', tweet, user)
                        load_data(tweet, user, conn, dbcur)

            except KeyError:
                # Original
                tweet = {}
                user = {}
                extracttweetfeatures(message, 'original', tweet, user)
                load_data(tweet, user, conn, dbcur)


# if __name__ == "__main__":
#    main()

if __name__ == "__main__":
    consumer = KafkaConsumer(
        os.environ['TOPIC'],
        bootstrap_servers=["" + os.environ['HOSTNAME'] + ":" + os.environ['PORT'] + ""], # bootstrap_servers=['kafka:9092'],  # ['192.168.1.4:9092'], #
        auto_offset_reset=os.environ['offset'], # 'earliest'/'latest',
        enable_auto_commit=os.environ['auto_commit'], # True/False
        group_id='twitter',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    conn, dbcur = initialize(db_name=os.environ['db_name'])

    write_to_DB(consumer, conn, dbcur)
