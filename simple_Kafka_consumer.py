from kafka import KafkaConsumer
from json import loads
import pandas as pd
import re
# from textprocessing import preprocessing
# from django.utils.encoding import smart_str
from flask import Flask, render_template, Response, json
import os

app = Flask(__name__)


@app.route('/')
def index():
    # return Response(ks(), mimetype='text/plain') # worked
    return Response(ks(), mimetype="application/json")  # worked


def ks(consumer):
    for message in consumer:
        output = []
        message = message.value
        output.append(message)
        # print('{} added'.format(message))

        # yield (message['full_text']) # worked
        # print(type(message))


        try:
            print(message['full_text'])
        except:
            print(message['text'])
        input("wat")

        '''
            values = message
            values.pop("display_text_range", None)
            values.pop("retweeted_status", None)

            # worked
            values = [{k:v} for k, v in values.items()]
            yield json.dumps(values, indent=4)
            # worked

            #extracttweetfeatures(tweets, output)
            #cleantweettext(tweets)
            #print(tweets['text'])


        # print([list(item) for item in tweets.text.values.tolist()])
        # cleantweettext(tweets)
        '''


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

    # app.run(host="0.0.0.0", port=6000)
    ks(consumer)
