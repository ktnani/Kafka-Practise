from confluent_kafka import DeserializingConsumer,SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer,JSONSerializer
from confluent_kafka.serialization import StringDeserializer, SerializationContext, MessageField
from utils.config_loader import load_config



# Load producer configs
Consumer_config=load_config("Consumer_configs.json")
general_configs=load_config("general_configs.json")

# Load general configs required
TOPIC_NAME=general_configs["topic"]
SCHEMA_REGISTRY_URL=general_configs["schema.registry.url"]
SCHEMA_SUBJECT=general_configs["schema_subject"]
TOTAL_MESSAGES = general_configs["number_of_messages"]

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



# consumer_conf = {
#     'bootstrap.servers': 'localhost:9092',
#     'key.deserializer': key_deserializer,
#     'value.deserializer': value_deserializer,
#     'client.id': "invoice-topic",
#     'group.id':"invoice-topic-consumers",
#     "auto.offset.reset":"earliest"

# }



consumer = DeserializingConsumer({
    **Consumer_config,
    "key.deserializer":key_deserializer,
    "value.deserializer":value_deserializer
    })
consumer.subscribe([TOPIC_NAME])

print(f"📥 Listening to topic: {TOPIC_NAME}...")
try:
    i=0
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("❌ Error:", msg.error())
            continue

        keyinfo = msg.key()
        valueinfo = msg.value()

        print(f"\n✅ Received message with key: {keyinfo}")
        print("📦 Payload:")
        print(valueinfo)  # This will be a Python dict (JSON-deserialized)
        i+=1

except KeyboardInterrupt:
    print("\n🛑 Stopping consumer.")
    print(f"\n Total msgs received:{i}")
finally:
    consumer.close()