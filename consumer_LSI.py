from kafka import KafkaConsumer
from json import loads
import pandas as pd
import re
# from textprocessing import preprocessing
#from django.utils.encoding import smart_str
from flask import Flask, render_template, Response, json


def ks():
    for message in consumer:
        output = []
        message = message.value
        output.append(message)
        # print('{} added'.format(message))

        try:
            print(message['full_text'])
        except:
            print(message['text'])

        # yield (message['full_text']) # worked
        # print(type(message))

        #extracttweetfeatures(tweets, output)
        #cleantweettext(tweets)
        #print(tweets['text'])


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

    ks()