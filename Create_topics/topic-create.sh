#!/bin/bash
export KAFKA_HOME=/Users/koushikreddy/Downloads/confluent-7.9.0
$KAFKA_HOME/bin/kafka-topics --create --bootstrap-server localhost:9092 --topic invoice-topic --partitions 5 --replication-factor 3 --config segment.bytes=1000000