# Mini Event-Driven System (Flask + Kafka + Docker)

## Overview

This project is a minimal event-driven system designed to demonstrate:

- REST API development using Flask (Python)
- Apache Kafka integration for asynchronous communication
- Consumer-based event processing
- Persistent storage using Docker volumes
- End-to-end system validation through a read endpoint
- Docker-based environment orchestration
- Basic distributed system architecture concepts

The system simulates an event ingestion pipeline where events are received via HTTP, published to Kafka, consumed asynchronously, and persisted to shared storage. 

---

## Architecture

The system consists of four main components:

1. **Producer API (Flask)**
2. **Apache Kafka (Broker)**
3. **Zookeeper**
4. **Consumer Service**
5. **Shared Storage (Docker volume -> events.json)**

### High-Level Flow

```
Client
  ↓
Flask REST API (POST /events)
  ↓
Kafka Topic -> events
  ↓
Consumer Service
  ↓
Docker volume (events.json)
  ↓
Flask REST API (GET /events)
  ↓
Client
```

### Working with the API

Health check
```
curl http://localhost:500/health
```

Post a new event into the "DB"
```
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{"type":"TEST_EVENT_0"}'
```

Read all events
```
curl http://localhost:5000/events | jq
```