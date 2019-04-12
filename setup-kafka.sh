#!/bin/bash

# A non-default bridge network enables convenient name-to-hostname discovery
docker network create kafka-net

docker run -d --rm --name zookeeper --network kafka-net zookeeper:3.4
# docker run -d --rm --name kafka --network kafka-net --env ZOOKEEPER_IP=zookeeper ches/kafka
# mounting multiple volume : multiple -v with different option
docker run -d --rm \
-v "$(pwd)"/kafka/data:/data \
-v "$(pwd)"/kafka/logs:/logs \
--name kafka --network kafka-net \
--env ZOOKEEPER_IP=zookeeper \
ches/kafka


docker run --rm --network kafka-net ches/kafka kafka-topics.sh --create --topic Twitter --replication-factor 1 \
--partitions 1 --zookeeper zookeeper:2181

# In separate terminals:
#docker run --rm -it --interactive --network kafka-net ches/kafka kafka-console-producer.sh --topic test --broker-list kafka:9092
#docker run --rm -it --network kafka-net ches/kafka kafka-console-consumer.sh --topic test --from-beginning --bootstrap-server kafka:9092

docker build -f Dockerfile_producer -t ksolaima/kafka-producer .
# docker run --rm -it --network kafka-net ksolaima/kafka-producer
# mount the host dir. to container dir. with : -v host-directory:container-directory
# docker run --rm -it --network kafka-net -v /Users/Salvi/CodeRepo/Research/RealM/Kafka/docker/twitter-kafka-1/data:/data ksolaima/kafka-producer
# setting mount directory in respect of current directory
docker run --rm -it --network kafka-net -v "$(pwd)"/data:/data ksolaima/kafka-producer
## docker build --file Dockerfile_stream_producer -t ksolaima/kafka-producer-stream .
docker run -d --rm --network kafka-net ksolaima/kafka-producer-stream

docker build -f Dockerfile -t ksolaima/kafka-consumer .
docker run --rm -it -p 8000:6000 --network kafka-net ksolaima/kafka-consumer
