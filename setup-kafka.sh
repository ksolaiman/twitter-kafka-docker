#!/bin/bash

# A non-default bridge network enables convenient name-to-hostname discovery
docker network create kafka-net

docker run -d --rm --name zookeeper --network kafka-net zookeeper:3.4
# docker run -d --rm --name kafka --network kafka-net --env ZOOKEEPER_IP=zookeeper ches/kafka
# mounting multiple volume : multiple -v with different option
docker run -d --rm \
--name kafka --network kafka-net \
--env ZOOKEEPER_IP=zookeeper \
ches/kafka
#-v "$(pwd)"/kafka/data:/data \
#-v "$(pwd)"/kafka/logs:/logs \

docker run --rm --network kafka-net ches/kafka kafka-topics.sh --create --topic Twitter --replication-factor 1 \
--partitions 1 --zookeeper zookeeper:2181

# In separate terminals:
#docker run --rm -it --interactive --network kafka-net ches/kafka kafka-console-producer.sh --topic test --broker-list kafka:9092
#docker run --rm -it --network kafka-net ches/kafka kafka-console-consumer.sh --topic test --from-beginning --bootstrap-server kafka:9092

<< --MULTILINE-COMMENT--
# https://vsupalov.com/docker-build-pass-environment-variables/
docker build \
--build-arg var_name='tags.txt' \
-f Dockerfile_producer -t ksolaima/kafka-producer .
# docker run --rm -it --network kafka-net ksolaima/kafka-producer
# mount the host dir. to container dir. with : -v host-directory:container-directory
# docker run --rm -it --network kafka-net -v /Users/Salvi/CodeRepo/Research/RealM/Kafka/docker/twitter-kafka-1/data:/data ksolaima/kafka-producer
# setting mount directory in respect of current directory

# change first part of -v if you want to save it elsewhere, the host directory has to be created beforehand
docker run --rm -it --network kafka-net \
-e TOPIC=Twitter \
-e HOSTNAME=kafka \
-e PORT=9092 \
-e hashtag_file=tags.txt \
-e consumer_key=7FZTvlJt8eVKu1tuDdIani7va \
-e consumer_secret=E45Vju021cgh7Jy32AwCVrPvHW1I9nK0CRafms3rwyhxY0uf0x \
-e access_token=762217521571180544-WiSHyXsaV6MJ9reso2WqS4mVh8moVyS \
-e access_token_secret=L6O2hoZpzxUUBnqvZ5Qn1OAo2Jmdfo5pUzpdwPRoaVEMg \
-v "$(pwd)"/data:/data \
ksolaima/kafka-producer
--MULTILINE-COMMENT--

docker build \
--build-arg var_name='tags.txt' \
--file Dockerfile_stream_producer -t ksolaima/kafka-producer-stream .

docker run --rm \
-it \
--network kafka-net \
-e TOPIC=Twitter \
-e HOSTNAME=kafka \
-e PORT=9092 \
-e hashtag_file=tags.txt \
-e consumer_key=o4AkNpNizimGou4seGGiC4jA4 \
-e consumer_secret=06R01rDGETzqouPTe5J4OZayuqHJWMxRFV8wtD4l92nGB3Ayrp \
-e access_token=737852660183932928-QiW3dDWxkfru7A3DbdlFfuLItcBkl8J \
-e access_token_secret=xkHpXx0zuooAJq8G2clPA9NymZEndtPDxDdsu3OzXqRyz \
-v "$(pwd)"/data:/data \
ksolaima/kafka-producer-stream

docker build -f Dockerfile -t ksolaima/kafka-consumer .
docker run --rm -it -p 8000:6000 --network kafka-net ksolaima/kafka-consumer


docker build \
--build-arg var_name='screen_names.txt' \
-f Dockerfile_timeline_producer -t ksolaima/kafka-timeline-producer .
# docker run --rm -it --network kafka-net ksolaima/kafka-producer
# mount the host dir. to container dir. with : -v host-directory:container-directory
# docker run --rm -it --network kafka-net -v /Users/Salvi/CodeRepo/Research/RealM/Kafka/docker/twitter-kafka-1/data:/data ksolaima/kafka-producer
# setting mount directory in respect of current directory

# change first part of -v if you want to save it elsewhere, the host directory has to be created beforehand
docker run --rm -it --network kafka-net \
-e TOPIC=Twitter \
-e HOSTNAME=kafka \
-e PORT=9092 \
-e hashtag_file=screen_names.txt \
-e consumer_key=7FZTvlJt8eVKu1tuDdIani7va \
-e consumer_secret=E45Vju021cgh7Jy32AwCVrPvHW1I9nK0CRafms3rwyhxY0uf0x \
-e access_token=762217521571180544-WiSHyXsaV6MJ9reso2WqS4mVh8moVyS \
-e access_token_secret=L6O2hoZpzxUUBnqvZ5Qn1OAo2Jmdfo5pUzpdwPRoaVEMg \
-v "$(pwd)"/data:/data \
ksolaima/kafka-timeline-producer


docker build \
--build-arg var_name='screen_names.txt' \
--file Dockerfile_stream_producer -t ksolaima/kafka-producer-timeline-stream .

docker run --rm \
-it \
--network kafka-net \
-e TOPIC=Twitter \
-e HOSTNAME=kafka \
-e PORT=9092 \
-e type=follow \
-e hashtag_file=screen_names.txt \
-e consumer_key=o4AkNpNizimGou4seGGiC4jA4 \
-e consumer_secret=06R01rDGETzqouPTe5J4OZayuqHJWMxRFV8wtD4l92nGB3Ayrp \
-e access_token=737852660183932928-QiW3dDWxkfru7A3DbdlFfuLItcBkl8J \
-e access_token_secret=xkHpXx0zuooAJq8G2clPA9NymZEndtPDxDdsu3OzXqRyz \
-v "$(pwd)"/data:/data \
ksolaima/kafka-producer-timeline-stream