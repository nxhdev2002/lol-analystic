#!/usr/bin/env python3
"""
Export JSON Schema files from Pydantic event models.

This script reads the Pydantic models from fbchat-core and exports
them as JSON Schema files to contracts/v1/.

Usage:
    python scripts/export_schemas.py
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Add src to path to import event models
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from events import (
    MessageReceivedEvent,
    MessageSendEvent,
    CookieChangedEvent,
    MatchEndedEvent,
    MessengerDisconnectedEvent,
)

# Event type to schema filename mapping
EVENT_SCHEMAS: Dict[str, Any] = {
    "message.received": MessageReceivedEvent,
    "message.send": MessageSendEvent,
    "cookie.changed": CookieChangedEvent,
    "match.ended": MatchEndedEvent,
    "messenger.disconnected": MessengerDisconnectedEvent,
}

# Output directory
CONTRACTS_DIR = Path(__file__).parent.parent / "contracts" / "v1"


def export_schema(event_type: str, model_class: type) -> None:
    """Export a single event model to JSON Schema."""
    schema = model_class.model_json_schema()
    
    # Add standard metadata
    schema["$id"] = f"https://fbchat.events/v1/{event_type}.schema.json"
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    
    # Ensure additionalProperties is true for backward compatibility
    if "additionalProperties" not in schema:
        schema["additionalProperties"] = True
    
    # Write to file
    output_file = CONTRACTS_DIR / f"{event_type}.schema.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Exported {event_type} to {output_file}")


def main():
    """Export all event schemas."""
    print("Exporting event schemas to contracts/v1/...")
    print()
    
    # Create contracts directory if it doesn't exist
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Export each event type
    for event_type, model_class in EVENT_SCHEMAS.items():
        try:
            export_schema(event_type, model_class)
        except Exception as e:
            print(f"[ERROR] Failed to export {event_type}: {e}")
            sys.exit(1)
    
    print()
    print(f"Successfully exported {len(EVENT_SCHEMAS)} event schemas.")


if __name__ == "__main__":
    main()
