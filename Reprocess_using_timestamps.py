from confluent_kafka import Consumer,TopicPartition
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.schema_registry.schema_registry_client import SchemaRegistryClient
from confluent_kafka.serialization import StringDeserializer, SerializationContext, MessageField
from confluent_kafka import DeserializingConsumer,SerializingProducer
from utils.config_loader import load_config


# Load producer configs
Consumer_config=load_config("Consumer_configs.json")
general_configs=load_config("general_configs.json")

# Load general configs required
TOPIC_NAME=general_configs["topic"]
SCHEMA_REGISTRY_URL=general_configs["schema.registry.url"]
SCHEMA_SUBJECT=general_configs["schema_subject"]
TOTAL_MESSAGES = general_configs["number_of_messages"]
timestamp_in_ms= 1744410980312

def dict_from_dict(obj, ctx):
    return obj

# Schema Registry client
schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

# Fetch latest schema string from registry
latest_schema_obj = schema_registry_client.get_latest_version(SCHEMA_SUBJECT)
latest_schema = latest_schema_obj.schema
schema_str = latest_schema_obj.schema.schema_str



# Deserializers
key_deserializer = StringDeserializer("utf_8")
value_deserializer = JSONDeserializer( schema_str=schema_str,
    schema_registry_client=schema_registry_client,
    from_dict=dict_from_dict)



#Define a consumer object
consumer = DeserializingConsumer({
    **Consumer_config,
    "key.deserializer":key_deserializer,
    "value.deserializer":value_deserializer
    })
#consumer.subscribe([TOPIC_NAME])

#List all the partitions in the topic dynamically
def get_partitions_in_topic(consumer,TOPIC_NAME):
   metadata=consumer.list_topics(topic=TOPIC_NAME,timeout=5)
   partitions = [
    p.id for p in metadata.topics[TOPIC_NAME].partitions.values()]
   return partitions


#Ask Kafka for offsets for each partition at the timestamp
def retrieve_timestamp_reqs( TOPIC_NAME,partitions,timestamp_in_ms,consumer):
 
 timestamp_reqs=[TopicPartition(TOPIC_NAME,p,timestamp_in_ms) for p in partitions]
 timestamp_offsets=consumer.offsets_for_times(timestamp_reqs)

 return timestamp_offsets

# partition_dict=get_partitions_in_topic(consumer,TOPIC_NAME)
# timestamp_Reqs=retrieve_timestamp_reqs(TOPIC_NAME,partition_dict,timestamp_in_ms,consumer)

# print(partition_dict)
# print(timestamp_Reqs)

#Assign consumer to these partitions
def assign_consumer_to_offsets(consumer,timestamp_Reqs):
    
    consumer.assign(timestamp_Reqs)
    for tp in timestamp_Reqs:
        if tp.offset != -1:
           consumer.seek(tp)
        else:
           print(f"No data found after {timestamp_in_ms} in partition {tp.partition}")

    

         
def main(TOPIC_NAME,timestamp_in_ms,consumer):
    
    partition_dict=get_partitions_in_topic(consumer,TOPIC_NAME)
    timestamp_Reqs=retrieve_timestamp_reqs(TOPIC_NAME,partition_dict,timestamp_in_ms,consumer)
    consumer_assignment=assign_consumer_to_offsets(consumer,timestamp_Reqs)
    print("Reprocessing messages from timestamp...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue
        try:
            print("Message value:", msg.value())
        except Exception as e:
            print("❌ Schema validation error:", e)
            print("Raw payload (bytes):", msg.value())

        #print(f"Reprocessed [{msg.topic()}-{msg.partition()}@{msg.offset()}] {msg.value().decode('utf-8')}")
        # Your validation & forwarding to valid/invalid topics can go here

main(TOPIC_NAME,timestamp_in_ms,consumer)


    
