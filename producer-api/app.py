from kafka.errors import NoBrokersAvailable # type: ignore
from flask import Flask, request, jsonify   # type: ignore
from kafka import KafkaProducer             # type: ignore
from datetime import datetime
import logging
import json
import uuid
import time
import os

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
_producer = None

EVENTS_FILE = "/shared/events.json"
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "events")


# Create with retry to make sure all processess are running
def get_producer_with_retry(max_wait_seconds: int = 30) -> KafkaProducer:
    deadline = time.time() + max_wait_seconds
    last_err = None

    while time.time() < deadline:
        try:
            p = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
                acks="all",
                retries=5,
                linger_ms=10,
            )
            logging.info("Connected to Kafka at %s", BOOTSTRAP)
            return p
        
        except NoBrokersAvailable as e:
            last_err = e
            logging.info("Kafka not ready yet (%s), retrying...", BOOTSTRAP)
            time.sleep(1)

    raise last_err or RuntimeError("Kafka not available")


def producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = get_producer_with_retry()
    return _producer

# API Health check 
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP", "timestamp": datetime.utcnow().isoformat()}), 200

# Create an event
@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)
    if not data or "type" not in data:
        return jsonify({"error": "Invalid event payload (missing 'type')"}), 400

    event = {
        "id": str(uuid.uuid4()),
        "type": data["type"],
        "payload": data.get("payload", {}),
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        fut = producer().send(TOPIC, key=event["type"], value=event)
        metadata = fut.get(timeout=10)
        
        logging.info("Produced event %s to %s [%s:%s]", event["id"], TOPIC, metadata.partition, metadata.offset)
        return jsonify({"status": "queued", "event": event}), 201
    
    except Exception as e:
        logging.exception("Failed to publish event to Kafka")
        return jsonify({"error": "Kafka publish failed", "details": str(e)}), 503

# List all events
@app.route("/events", methods=["GET"])
def get_events():
    if not os.path.exists(EVENTS_FILE):
        return jsonify({"count": 0, "events": []})

    with open(EVENTS_FILE, "r") as f:
        data = json.load(f)

    return jsonify({
        "count": len(data),
        "events": data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
