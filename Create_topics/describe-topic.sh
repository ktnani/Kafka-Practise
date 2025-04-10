#!/bin/bash
export KAFKA_HOME=/Users/koushikreddy/Downloads/confluent-7.9.0
$KAFKA_HOME/bin/kafka-topics --describe  --zookeeper localhost:2181 --topic invoice-topic