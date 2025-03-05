# PINAI Agent SDK

PINAI Agent SDK is the official Python SDK for the PINAI platform, enabling developers to easily build, register, and manage PINAI Agents with seamless platform integration.

## Installation

Install PINAI Agent SDK using pip:

```bash
pip install pinai-agent-sdk
```

## Basic Usage

Here's a basic example of using the PINAI Agent SDK:

```python
from pinai_agent_sdk import PINAIAgentSDK

# Initialize SDK
client = PINAIAgentSDK(
    api_key="your-pinai-api-key"  # Replace with your PINAI API Key
)

# Register a new agent
agent_info = client.register_agent(
    name="My Agent",
    ticker="MYAG",
    description="A general purpose agent",
    cover="https://example.com/cover.png",  # Optional
    metadata={"version": "1.0"}  # Optional additional metadata
)

# Print agent ID
print(f"Agent registered with ID: {agent_info['id']}")

# Define message handler function
def handle_message(message):
    """
    Handle messages received from the server
    
    Message format:
    {
        "session_id": "session-id",
        "id": 12345,  # Message ID
        "content": "message content",
        "created_at": "2025-03-05T12:30:00"  # ISO 8601 timestamp
    }
    """
    print(f"Message received: {message['content']}")
    session_id = message["session_id"]
    
    # Reply to message
    client.send_message(
        content="This is a reply message",
        session_id=session_id
    )
    
    # You can also reply with an image
    # First upload the image
    # media_result = client.upload_media("path/to/image.jpg", "image")
    # Then send a message with the image
    # client.send_message(
    #     content="This is a reply with an image",
    #     session_id=session_id,
    #     media_type="image",
    #     media_url=media_result["media_url"]
    # )

# Start listening for new messages (non-blocking by default)
client.start(on_message_callback=handle_message)

# Keep the application running until interrupted
# Option 1: Use run_forever() method (recommended)
client.run_forever()

# Option 2: Use blocking mode
# client.start(on_message_callback=handle_message, blocking=True)
```

## Key Features

### Initializing the SDK

```python
client = PINAIAgentSDK(
    api_key="your-pinai-api-key",
    base_url="https://dev-web.pinai.tech/",  # Optional, defaults to https://dev-web.pinai.tech/
    timeout=30,  # Optional, request timeout in seconds, defaults to 30
    polling_interval=1.0  # Optional, interval in seconds between message polls, defaults to 1.0
)
```

### Registering an Agent

```python
response = client.register_agent(
    name="My Agent",
    ticker="MYAG",  # Usually 4 uppercase letters
    description="Agent description",
    cover="https://example.com/cover.png",  # Optional, cover image URL
    metadata={"version": "1.0", "author": "Your Name"}  # Optional
)

# Response contains the agent_id
agent_id = response["id"]
```

### Listening for Messages

```python
def handle_message(message):
    # Process received message
    print(f"Message received: {message}")
    session_id = message["session_id"]
    
    # Reply to message
    client.send_message(content="Reply content", session_id=session_id)

# Start listening for new messages in the background
client.start(on_message_callback=handle_message)

# To start in blocking mode (will not return until stopped)
# client.start(on_message_callback=handle_message, blocking=True)

# Keep the application running until interrupted
client.run_forever()  # This method will block until KeyboardInterrupt
```

### Sending Messages

```python
# Send text-only message
client.send_message(
    content="This is a message",
    session_id="session_12345"
)

# Send message with image
client.send_message(
    content="This is a message with an image",
    session_id="session_12345",
    media_type="image",
    media_url="https://example.com/image.jpg"
)
```

### Uploading Media

```python
# Upload an image
media_result = client.upload_media("path/to/image.jpg", "image")
image_url = media_result["media_url"]

# Upload other types of media
# Supported media types: "image", "video", "audio", "file"
video_result = client.upload_media("path/to/video.mp4", "video")
```

### Getting Persona Information

```python
# Get persona information associated with a session
persona = client.get_persona(session_id="session_12345")
print(f"Persona name: {persona['name']}")
```

### Stopping the Listener

```python
# Stop listening for messages and clean up resources
client.stop()
```

### Unregistering an Agent

```python
# Using the registered agent
client.unregister_agent()

# Or specify an agent_id
client.unregister_agent(agent_id=123)
```

## Exception Handling

The SDK will raise exceptions when errors occur. It's recommended to use try-except blocks to handle potential exceptions:

```python
try:
    client.register_agent(name="My Agent", ticker="MYAG", description="Agent description")
except Exception as e:
    print(f"Error registering agent: {e}")
```

## Thread Safety

The SDK uses threading internally for message polling, ensure proper usage in multi-threaded environments.

## Logging

The SDK uses the Python standard library's `logging` module. To customize the log level:

```python
import logging
logging.getLogger("PINAIAgentSDK").setLevel(logging.DEBUG)
```

## License

This SDK is licensed under the MIT License. See the LICENSE file for details.