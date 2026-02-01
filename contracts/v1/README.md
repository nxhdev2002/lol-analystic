# Event Contracts v1

This directory contains JSON Schema definitions for all events in the microservices architecture.

## Event Types

| Event Type | Schema File | Publisher | Consumer(s) |
|------------|-------------|-----------|-------------|
| `message.received` | `message.received.schema.json` | fbchat-core | lol-service |
| `message.send` | `message.send.schema.json` | lol-service | fbchat-core |
| `cookie.changed` | `cookie.changed.schema.json` | mini-fb-service | fbchat-core |
| `match.ended` | `match.ended.schema.json` | lol-service | - |
| `messenger.disconnected` | `messenger.disconnected.schema.json` | fbchat-core | mini-fb-service |

## Schema Format

All schemas follow this structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://fbchat.events/v1/<event-type>.schema.json",
  "title": "<EventType>Event",
  "description": "Event published when...",
  "type": "object",
  "required": ["event_type", "timestamp", "data"],
  "properties": {
    "event_type": {
      "const": "<event-type>",
      "type": "string"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    },
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique event identifier"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "Correlation ID for tracing across services"
    },
    "producer": {
      "type": "string",
      "description": "Service name that produced the event"
    },
    "data": {
      "type": "object",
      "description": "Event-specific data"
    }
  }
}
```

## Generating Schemas

Run the schema export script from the repository root:

```bash
python scripts/export_schemas.py
```

This script exports JSON schemas from the Pydantic models in `fbchat-core`.

## Versioning

- `v1`: Initial version with basic event types
- Future versions will be added as `v2/`, `v3/`, etc.

## Backward Compatibility

- v1 schemas allow `additionalProperties: true` to support future extensions
- Services should validate inbound events against the schema
- Unknown fields should be ignored, not cause validation errors
