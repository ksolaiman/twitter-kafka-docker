from kafka import KafkaConsumer
from json import loads
import pandas as pd
import re
# from textprocessing import preprocessing
#from django.utils.encoding import smart_str
from flask import Flask, render_template, Response, json

app = Flask(__name__)


def initialize():
    '''
    Initialize a function that takes postgres database name as arguent and sets up a pandas dataframe.
    '''
    tweets = pd.DataFrame() # set-up an pandas dataframe
    return tweets


def extracttweetfeatures(tweets,output):
    '''
    extracttweetfeatures function takes tweets dataframe and a output list as input. Output list comprises of the list
    of all tweets in a json format consumed by json consumer. Function theN extracts the important features such as
    tweet text, movie name, language, country, user name, coordinates, location, retweets count.
    '''
    # print(tweets)
    # print(output)

    try:
        # tweets['text'] = map(lambda tweet: tweet['text'], output) # full_text instead of text in REST tweets
        tweets['text'] = pd.DataFrame.from_dict(output)['text']
    except IndexError:
        tweets['text'] = 'Data Error'
    try:
        tweets['movie'] = map(lambda tweet: tweet['entities']['hashtags'][0]['text'], output)
    except IndexError:
        tweets['movie'] = 'Data Error'
    try:
        tweets['lang'] = map(lambda tweet: tweet['user']['lang'], output)
    except IndexError:
        tweets['lang'] = 'Data Error'
    try:
        tweets['country'] = map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, output)
    except IndexError:
        tweets['country'] = 'Data Error'
    try:
        tweets['user_nm'] = map(lambda tweet: tweet['user']['name'].encode('utf-8'), output)
    except IndexError:
        tweets['user_nm'] = 'Data Error'

    try:
        tweets['screen_nm'] = map(lambda tweet: tweet['user']['screen_name'].encode('utf-8'), output)
    except IndexError:
        tweets['screen_nm'] = 'Data Error'
    try:
        tweets['coordinates_lat'] = map(lambda tweet: str(tweet['coordinates']['coordinates'][1]) if tweet['coordinates'] != None else None, output)
    except IndexError:
        tweets['coordinates_lat'] = 'Not available'
    except KeyError:
        tweets['coordinates_lat'] = 'Not available'
    except TypeError:
        tweets['coordinates_lat'] = 'Not available'
    try:
        tweets['coordinates_long'] = map(lambda tweet: str(tweet['coordinates']['coordinates'][0]) if tweet['coordinates'] != None else None , output)
    except IndexError:
        tweets['coordinates_long'] = 'Not available'
    except KeyError:
        tweets['coordinates_long'] = 'Not available'
    except TypeError:
        tweets['coordinates_long'] = 'Not available'

    try:
        tweets['location'] = map(lambda tweet: tweet['user']['location'] if tweet['user'] != None else None, output)
    except IndexError:
        tweets['location'] = 'Data Error'
    try:
        tweets['retweets_count'] = map(lambda tweet: tweet['retweeted_status']['retweet_count'], output)
    except IndexError:
        tweets['retweets_count'] = 0
    except KeyError:
        tweets['retweets_count'] = 0
    try:
        tweets['followers_count'] = map(lambda tweet: tweet['user']['followers_count'], output)
    except IndexError:
        tweets['followers_count'] = 0
    except KeyError:
        tweets['followers_count'] = 0
    try:
        tweets['favourites_count'] = map(lambda tweet: tweet['user']['favourites_count'], output)
    except IndexError:
        tweets['favourites_count'] = 0
    except KeyError:
        tweets['favourites_count'] = 0
    try:
        tweets['friends_count'] = map(lambda tweet: tweet['user']['friends_count'], output)
    except IndexError:
        tweets['friends_count'] = 0
    except KeyError:
        tweets['friends_count'] = 0


def cleantweettext(tweets):
    '''
    cleantweettext function takes tweets dataframe. Function adds a text_clean column to tweets dataframe by
    running text cleansing functions.
    '''
    tweets['text_clean'] = [re.sub(r"http\S+", "", v) for v in tweets.text.values.tolist()]
    tweets['text_clean'] = [re.sub(r"#\S+", "", v) for v in tweets.text_clean.values.tolist()]
    tweets['text_clean'] = [re.sub(r"@\S+", "", v) for v in tweets.text_clean.values.tolist()]
    tweets['text_clean'] = [re.sub(r"u'RT\S+", "", v) for v in tweets.text_clean.values.tolist()]
    #tweets['text'] = [v.replace('\n'," ") for v in tweets.text.values.tolist()]
    #tweets['text'] = [v.replace(u"\u2018", " ").replace(u"\u2019", " ") for v in tweets.text.values.tolist()]

    print(tweets['text_clean'])
    '''
    try:
       tweets['text'] = [smart_str(v) for v in tweets.text.values.tolist()]
    except UnicodeDecodeError:
       tweets['text'] = [v.decode('utf-8') for v in tweets.text.values.tolist()]
    try:
       tweets['user_nm'] = [smart_str(v) for v in tweets.user_nm.values.tolist()]
    except UnicodeDecodeError:
       tweets['user_nm'] = [v.decode('utf-8') for v in tweets.user_nm.values.tolist()]
    try:
       tweets['location'] = [smart_str(v) for v in tweets.location.values.tolist()]
    except UnicodeDecodeError:
       tweets['location'] = [v.decode('utf-8') for v in tweets.location.values.tolist()]

    tweets['text_clean'] = preprocessing.clean_text(text=tweets.text_clean.values, remove_short_tokens_flag=False ,lemmatize_flag=True)

    print(tweets['text_clean'])
    '''

def print_iterator(it):
    for x in it:
        print(x, end=' ')
    print('')



@app.route('/')
def index():
    # return a multipart response
    # return "bal amar"
    # return Response(ks(), mimetype='text/plain') # worked
    # return render_template("sample.html", test=ks())
    #ks()
    """
    import json

    dict_ = {"20090209.02s1.1_sequence.txt": [645045714, 3559.6422951221466, 206045184],
             "20090209.02s1.2_sequence.txt": [645045714, 3543.8322949409485, 234618880]}
    values = [{"file_name": k, "file_information": v} for k, v in dict_.items()]
    result = json.dumps(values, indent=4)
    return result
    """
    return Response(ks(), mimetype="text/json") # worked

                    # mimetype='multipart/x-mixed-replace; boundary=frame')

def ks():
    tweets = initialize()
    i = 0
    ans = []
    for message in consumer:
        output = []
        message = message.value
        output.append(message)
        print('{} added'.format(message))

        # yield (message['full_text']) # worked
        # print(type(message))

        # worked
        values = [{k:v} for k, v in message.items()]
        yield json.dumps(values, indent=4)
        # worked

        #extracttweetfeatures(tweets, output)
        #cleantweettext(tweets)
        #print(tweets['text'])
        # input("wait")
        #i+=1
        #if i > 10:
        #    break


    # print([list(item) for item in tweets.text.values.tolist()])
    # cleantweettext(tweets)


#if __name__ == "__main__":
#    main()

if __name__ == "__main__":
    consumer = KafkaConsumer(
        'Twitter',
        bootstrap_servers=['kafka:9092'],  # ['192.168.1.4:9092'], #
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        # group_id='my-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    app.run(host="0.0.0.0", port=6000)
    #ks()