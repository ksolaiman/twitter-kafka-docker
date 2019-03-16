# base image
FROM python:3-onbuild

# specify the port number the container should expose
EXPOSE 6000

# add python files to run
# the / at the end is the WORKDIR
# ADD config.py /
# ADD extract_tweets_restful.py /
COPY simple_Kafka_consumer.py requirements.txt /tmp/

# COPY requirements.txt /
WORKDIR /tmp/

# Run commands for installing packages
# RUN pip install pkg_name
# RUN pip install -r requirements.txt


VOLUME [ "/data", "/logs" ]
 
# start app
CMD [ "python", "./simple_Kafka_consumer.py" ]


