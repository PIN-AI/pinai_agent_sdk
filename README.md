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
client.register_agent(
    name="My Agent",
    category="general",
    description="A general purpose agent",
    logo="https://example.com/logo.png",  # Optional
    metadata={"version": "1.0"}  # Optional additional metadata
)

# Define message handler function
def handle_message(message):
    """
    Handle messages received from the server
    
    Message format:
    {
        "sessionId": "session-id",
        "timestamp": 12345678,  # Timestamp in milliseconds
        "content": "message content"
    }
    """
    print(f"Message received: {message['content']}")
    
    # Reply to message
    client.send_message(
        content="This is a reply message"
    )
    
    # You can also reply with an image
    # client.send_message(
    #     content="This is a reply with an image",
    #     image_url="https://example.com/image.jpg"
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
    category="general",
    description="Agent description",
    logo="https://example.com/logo.png",  # Optional
    metadata={"version": "1.0", "author": "Your Name"}  # Optional
)
```

### Listening for Messages

```python
def handle_message(message):
    # Process received message
    print(f"Message received: {message}")
    
    # Reply to message
    client.send_message(content="Reply content")

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
client.send_message(content="This is a message")

# Send message with image
client.send_message(
    content="This is a message with an image",
    image_url="https://example.com/image.jpg"
)
```

### Stopping the Listener

```python
# Stop listening for messages and clean up resources
client.stop()
```

### Unregistering an Agent

```python
client.unregister_agent(name="My Agent")
```

## Exception Handling

The SDK will raise exceptions when errors occur. It's recommended to use try-except blocks to handle potential exceptions:

```python
try:
    client.register_agent(name="My Agent", category="general", description="Agent description")
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