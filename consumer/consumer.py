from kafka.errors import NoBrokersAvailable # type: ignore
from kafka import KafkaConsumer             # type: ignore
import logging
import json
import time
import os

logging.basicConfig(level=logging.INFO)

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "events")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "demo-consumer")
OUTPUT_FILE = "/shared/events.json"

# Append data to file 
def append_event(event):
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w") as f:
            json.dump([], f)
            
    with open(OUTPUT_FILE, "r+") as f:
        data = json.load(f)
        data.append(event)
        f.seek(0)
        json.dump(data, f, indent=2)


def main():
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id=GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
                key_deserializer=lambda b: b.decode("utf-8") if b else None,
            )
            logging.info("Consumer connected to Kafka: %s", BOOTSTRAP)
            break

        except NoBrokersAvailable:
            logging.warning("Kafka not ready yet (%s). Retrying in 2s...", BOOTSTRAP)
            time.sleep(2)

    for msg in consumer:
        logging.info("Consumed event: %s", msg.value)
        append_event(msg.value)


if __name__ == "__main__":
    main()
