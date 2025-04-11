from confluent_kafka import DeserializingConsumer,SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer,JSONSerializer
from confluent_kafka.serialization import StringDeserializer, SerializationContext, MessageField
# Configs
TOPIC_NAME = "invoice-topic"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
SCHEMA_SUBJECT = "invoice-topic-value"


def dict_from_dict(obj, ctx):
    return obj

# Schema Registry client
schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

# Fetch latest schema string from registry
latest_schema_obj = schema_registry_client.get_latest_version(SCHEMA_SUBJECT)
latest_schema = latest_schema_obj.schema
schema_str = latest_schema_obj.schema.schema_str

#Serializers
json_serializer = JSONSerializer(schema_str=latest_schema.schema_str, schema_registry_client=schema_registry_client)

# Deserializers
key_deserializer = StringDeserializer("utf_8")
value_deserializer = JSONDeserializer( schema_str=schema_str,
    schema_registry_client=schema_registry_client,
    from_dict=dict_from_dict)


# Kafka producer config
producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'key.serializer': lambda v, ctx: v.encode("utf-8"),
    'value.serializer': json_serializer
}

consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'key.deserializer': key_deserializer,
    'value.deserializer': value_deserializer,
    'client.id': "invoice-topic",
    'group.id':"invoice-topic-consumers",
    "auto.offset.reset":"earliest"

}

producer = SerializingProducer(producer_conf)

consumer = DeserializingConsumer(consumer_conf)
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
        if valueinfo.get("DeliveryType") == "HOME-DELIVERY" and valueinfo.get("DeliveryAddress").get("ContactNumber") is None:
            print("Sending data to invalid pos topic")
            producer.produce(topic="invalid-pos-topic",key=keyinfo,value=valueinfo)
        else:
            print("Sending data to valid pos topic")
            producer.produce(topic="valid-pos-topic",key=keyinfo,value=valueinfo)

        print(f"\n✅ Received message with key: {keyinfo}")
        print("📦 Payload:")
        print(valueinfo)  # This will be a Python dict (JSON-deserialized)
        i+=1
        if i % 10000 == 0:
            producer.flush()

except KeyboardInterrupt:
    print("\n🛑 Stopping consumer.")
    print(f"\n Total msgs received:{i}")
finally:
    consumer.close()