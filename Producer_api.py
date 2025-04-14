from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from random_invoice_generator import create_random_invoice  # your function that generates invoice dicts
from utils.config_loader import load_config


# TOTAL_MESSAGES = 1000000


# Load producer configs
Producer_config=load_config("Producer_configs.json")
general_configs=load_config("general_configs.json")

# Load general configs required
TOPIC_NAME=general_configs["topic"]
SCHEMA_REGISTRY_URL=general_configs["schema.registry.url"]
SCHEMA_SUBJECT=general_configs["schema_subject"]
TOTAL_MESSAGES = general_configs["number_of_messages"]

# Schema Registry client
schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

# Fetch latest registered schema from registry
latest_schema_obj = schema_registry_client.get_latest_version(SCHEMA_SUBJECT)
latest_schema = latest_schema_obj.schema
json_serializer = JSONSerializer(schema_str=latest_schema.schema_str, schema_registry_client=schema_registry_client)



# Initialize producer with remaining config
producer = SerializingProducer({
    **Producer_config,
    "key.serializer": lambda v, ctx: v.encode("utf-8"),
    "value.serializer": json_serializer
})



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
