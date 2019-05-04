# twitter-kafka-docker
- Starts a zookeeper server
- Starts a single broker kafka server
- Starts the twitter restful data collection of hashtags in tags.txt. The image is available directly from [Docker Hub](https://cloud.docker.com/u/ksolaima/repository/docker/ksolaima/kafka-producer).
- Starts the twitter streaming data collection of hashtags in tags.txt. The image is available directly from [Docker Hub](https://cloud.docker.com/u/ksolaima/repository/docker/ksolaima/kafka-producer-stream). It will keep streaming as long as the servers are alive.
- Starts the twitter restful data collection of timelines from screen_names.txt. The image is available directly from [Docker Hub](https://cloud.docker.com/u/ksolaima/repository/docker/ksolaima/kafka-timeline-producer).
- Starts the twitter streaming data collection of timelines from screen_names.txt. The image is available directly from [Docker Hub](https://cloud.docker.com/u/ksolaima/repository/docker/ksolaima/kafka-producer-timeline-stream). It will keep streaming as long as the servers are alive.
- Starts the consumer to consume the twitter data as json. This is where the code for putting it in PostGres should go.
- In mac, docker runs in a vm environment. So in the vm, runs in ```0.0.0.0:6000```. To see the page in host machine browser, it showed in ```192.168.99.100:8000```. Basically it would show in docker-ip:host-port address. May act differently in linux or windows.

## Pre-Requisites

- Install docker
- TWITTER setup : 
Create an app on https://apps.twitter.com/ and then create auth tokens. These will be used as environment variables for the producers.


## Usage

- Start with ```./setup-kafka.sh```
- See ```./setup-kafka.sh``` to understand the environment variables.


## Any change in the desired output

If you want to change the way the json files are prepared or shown, you need to update the ```simple_Kafka_consumer.py ``` file. Any change there will be reflected when you run again with ```./setup-kafka.sh```.
