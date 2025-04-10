from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from random_invoice_generator import create_random_invoice  # your function that generates invoice dicts

# Configs
TOPIC_NAME = "invoice-topic"
TOTAL_MESSAGES = 1000000
SCHEMA_REGISTRY_URL = "http://localhost:8081"
SCHEMA_SUBJECT = "invoice-topic-value"

# Schema Registry client
schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

# Fetch latest registered schema from registry
latest_schema_obj = schema_registry_client.get_latest_version(SCHEMA_SUBJECT)
latest_schema = latest_schema_obj.schema
json_serializer = JSONSerializer(schema_str=latest_schema.schema_str, schema_registry_client=schema_registry_client)

# Kafka producer config
producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'key.serializer': lambda v, ctx: v.encode("utf-8"),
    'value.serializer': json_serializer
}

producer = SerializingProducer(producer_conf)

# Send messages
print(f"🚀 Sending {TOTAL_MESSAGES:,} invoices to topic '{TOPIC_NAME}'...")

for i in range(TOTAL_MESSAGES):
    invoice = create_random_invoice()
    key = invoice.get("InvoiceNumber") or invoice.get("Invoice", {}).get("InvoiceNumber", "UNKNOWN")

    producer.produce(
        topic=TOPIC_NAME,
        key=key,
        value=invoice
    )

    if i % 10000 == 0:
        print(f"✅ Sent {i:,} invoices...")
        producer.flush()

producer.flush()
print("🎉 All messages sent.")
