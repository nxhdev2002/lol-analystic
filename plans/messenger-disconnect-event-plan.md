# Plan: Publish Messenger Disconnected Event on Facebook MQTT Disconnection

## Objective
When the Facebook MQTT connection disconnects, publish a "messenger.disconnected" event to RabbitMQ to notify other systems of the disconnection.

## Requirements
- Publish event only once per session to avoid duplicates.
- Integrate with existing RabbitMQ event system.
- Include relevant data in the event (account ID, reason for disconnection).

## Implementation Steps

1. **Define MessengerDisconnectedEvent in src/events.py**
   - Create a new Pydantic model for the event.
   - Include fields: account_id (str), reason (str, optional).
   - Add to EVENT_TYPES mapping.

2. **Add QUEUE_MESSENGER_DISCONNECTED in src/config.py**
   - Define the routing key for the disconnect event queue.

3. **Create or Modify Publisher**
   - Either create a new publisher class or add method to existing MessagePublisher.
   - Method to publish MessengerDisconnectedEvent.

4. **Modify listeningEvent Class in src/__messageListenV2.py**
   - Add publisher parameter to __init__.
   - Add disconnect_published flag to prevent duplicates.
   - In on_disconnect callback: check flag, publish event if not already published, set flag to True.

5. **Update fbClient.receiveMessage() in src/main.py**
   - Pass the message_publisher instance to listeningEvent instantiation.

6. **Testing**
   - Verify event is published on disconnection.
   - Ensure no duplicate events for the same session.
   - Check event data is correct.

## Event Schema
```python
class MessengerDisconnectedEvent(BaseEvent):
    event_type: str = "messenger.disconnected"
    data: MessengerDisconnectedData
```

Where MessengerDisconnectedData includes:
- account_id: Facebook account ID
- reason: Reason for disconnection (e.g., "connection_lost", "network_error")

## Workflow
1. MQTT connection established.
2. On disconnect callback triggered.
3. If not already published for this session:
   - Create MessengerDisconnectedEvent.
   - Publish to RabbitMQ.
   - Mark as published.
4. Other systems can consume the event and react accordingly.