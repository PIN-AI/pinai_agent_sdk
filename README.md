# QA

## Frequently Asked Questions

**Q: How do I get an API key?**  
A: You can obtain an API key from the [PINAI Agent platform](https://agent.pinai.tech/profile) after login.

**Q: How many agents can one account create?**  
A: No limit.

**Q: How do I handle a large number of concurrent users?**  
A: Consider using multi-threading or asynchronous processing, and implement appropriate rate limiting and load balancing.

## Support and Resources

- [GitHub Repository](https://github.com/PIN-AI/pinai_agent_sdk)
- [Telegram Group QR Code](https://github.com/PIN-AI/pinai_agent_sdk/blob/main/TelegramQRCode.jpg)


---

Good luck with your Hackathon! If you have any questions, feel free to contact the PINAI team. 

# PINAI Agent SDK Development Guide

## Introduction

PINAI Agent SDK is a powerful toolkit that allows developers to quickly create and deploy intelligent agents. This guide will help you get started and provide best practices and API references.

## Installation

```bash$$
pip install pinai-agent-sdk
```

## Quick Start In 3 Lines

```python
from pinai_agent_sdk import PINAIAgentSDK
client = PINAIAgentSDK(api_key="") # you can get it from https://agent.pinai.tech/profile.

client.start_and_run(
    on_message_callback=lambda message: client.send_m$$essage(content=message),
    agent_id=42  # [PINAI]Hackathon Assistant Agent
)
```

##  Register and Unregister Agent

```python
from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL
client = PINAIAgentSDK(api_key="")

# If success, agent id will return  
agent_info = client.register_agent(
    name="Your Agent",
    description="Your Agent description",
    category=AGENT_CATEGORY_SOCIAL,  # Choose from available categories
    # Optional: wallet="your_wallet_address"
)

client.unregister_agent(
    agent_id=9
)
```


```python
from pinai_agent_sdk import PINAIAgentSDK
client = PINAIAgentSDK(api_key="") # you can get it from https://agent.pinai.tech/profile.

client.start_and_run(
    on_message_callback=lambda message: client.send_message(content=message),
    agent_id=42  # [PINAI]Hackathon Assistant Agent
)
```

## Full demo with  reply

Here are the basic steps to create a simple agent:

```python
import os
from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL

# Initialize the SDK client
API_KEY = os.environ.get("PINAI_API_KEY", "your_api_key_here")
# For blockchain integration (optional) init in  PINAIAgentSDK.
PRIVATE_KEY = os.environ.get("ETHEREUM_PRIVATE_KEY")
RPC_URL = os.environ.get("BLOCKCHAIN_RPC_URL", "https://sepolia.base.org")

client = PINAIAgentSDK(api_key=API_KEY)

# Define message handling function
def handle_message(message):
    """
    Process incoming messages and respond
    
    Args:
        message (dict): Message object with format:
            {
                "session_id": "unique-session-id",
                "id": 12345,  # Message ID
                "content": "user message text",
                "created_at": "2023-01-01T12:00:00"
            }
    """
    print(f"Received: {message['content']}")

    session_id = message.get("session_id")
    if not session_id:
        print("Message missing session_id, cannot respond")
        return
    
    # Get user's message
    user_message = message.get("content", "")

    # Get persona info
    persona_info = client.get_persona(session_id)
    
    # Create your response (this is where your agent logic goes)
    response = f"Echo: {user_message}"
    
    # Send response back to user
    client.send_message(content=response)
    print(f"Sent: {response}")

# Register a new agent
agent_info = client.register_agent(
    name="My Hackathon Agent",
    description="A simple agent built during the hackathon",
    category=AGENT_CATEGORY_SOCIAL
)
agent_id = agent_info.get("id")
print(f"Agent registered with ID: {agent_id}")

# Start the agent and listen for messages
print("Starting agent... Press Ctrl+C to stop")
client.start_and_run(
    on_message_callback=handle_message,
    agent_id=agent_id
)
```

## Core Concepts

### Agent

An agent is the intelligent assistant you create that can interact with users. Each agent has a unique ID, name, description, and category.

### Session

A session represents a conversation with a user. Each session has a unique `session_id` used to track interactions with a specific user.

### Message

A message is the unit of information exchanged between the agent and users. Messages can contain text content and media (images, videos, audio, or files).

## Agent Categories

PINAI platform supports the following agent categories:

| Category Constant | Display Name | Description |
|---------|---------|------|
| `AGENT_CATEGORY_SOCIAL` | Social | Social agents |
| `AGENT_CATEGORY_DAILY` | Daily Life/Utility | Daily life and utility agents |
| `AGENT_CATEGORY_PRODUCTIVITY` | Productivity | Productivity tool agents |
| `AGENT_CATEGORY_WEB3` | Web3 | Web3-related agents |
| `AGENT_CATEGORY_SHOPPING` | Shopping | Shopping agents |
| `AGENT_CATEGORY_FINANCE` | Finance | Finance agents |
| `AGENT_CATEGORY_AI_CHAT` | AI Chat | AI chat agents |
| `AGENT_CATEGORY_OTHER` | Other | Other types of agents |

## API Reference Sample

### Initializing the SDK

```python
from pinai_agent_sdk import PINAIAgentSDK

client = PINAIAgentSDK(
    api_key="your_api_key",  # Required: PINAI API key
    base_url="https://api.example.com",  # Optional: API base URL
    timeout=30,  # Optional: Request timeout (seconds)
    polling_interval=1.0,  # Optional: Message polling interval (seconds)
    privatekey="your_private_key",  # Optional: Ethereum private key for blockchain interaction
    blockchainRPC="https://sepolia.base.org"  # Optional: Blockchain RPC URL for on-chain agent registration
)
```

### Registering an Agent

```python
agent_info = client.register_agent(
    name="My Agent",  # Required: Agent name
    description="This is an example agent",  # Required: Agent description
    category=AGENT_CATEGORY_SOCIAL,  # Required: Agent category
    wallet="your_wallet_address",  # Optional: Wallet address
    cover="cover_image_url",  # Optional: Cover image URL
    metadata={"key": "value"},  # Optional: Additional metadata
    agent_owner="0x123..."  # Optional: Ethereum address of the agent owner (for blockchain registration)
)
```

### Unregistering an Agent

```python
result = client.unregister_agent(agent_id=123)
```

### Starting an Agent

```python
# Blocking mode (until Ctrl+C)
client.start_and_run(
    on_message_callback=handle_message,
    agent_id=123
)

```

### Sending Messages

```python
response = client.send_message(
    content="Hello, world!",  # Required: Message content
    session_id="unique-session-id",  # Optional: Session ID
    media_type="image",  # Optional: Media type, default is "none"
    media_url="https://example.com/image.jpg",  # Optional: Media URL
    meta_data={"key": "value"}  # Optional: Additional metadata
)
```

### Getting User Information

```python
persona = client.get_persona(session_id="unique-session-id")
```

### Uploading Media

```python
media_info = client.upload_media(
    file_path="/path/to/image.jpg",  # File path
    media_type="image"  # Media type: "image", "video", "audio", "file"
)
media_url = media_info.get("url")
```

## Media Types and Limitations

| Media Type | Supported Extensions | Size Limit |
|---------|------------|---------|
| image | .jpg, .jpeg, .png, .gif, .webp | 10MB |
| video | .mp4, .webm, .mov | 100MB |
| audio | .mp3, .wav, .ogg | 50MB |
| file | .pdf, .txt, .zip, .docx | 20MB |

## Error Handling

The SDK provides various exception types to help handle different error scenarios:

- `AuthenticationError`: API authentication failure (401 errors)
- `PermissionError`: Insufficient permissions (403 errors)
- `ResourceNotFoundError`: Requested resource not found (404 errors)
- `ResourceConflictError`: Resource conflict (409 errors)
- `ValidationError`: Request validation failure (400 errors)
- `ServerError`: Server returns 5xx errors
- `NetworkError`: Network connection issues
- `Web3Error`: Blockchain interaction failures

Example:

```python
try:
    client.send_message(content="Hello")
except ValidationError as e:
    print(f"Validation error: {e}")
except AuthenticationError as e:
    print(f"Authentication error: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

## Best Practices

### 1. Securely Store API Keys

Don't hardcode API keys in your code. Use environment variables or secure key management services.

```python
import os
API_KEY = os.environ.get("PINAI_API_KEY")
```

### 2. Implement Robust Message Handling

Always check if messages contain necessary fields and handle exceptions properly.

```python
def handle_message(message):
    if not message or "content" not in message:
        print("Received invalid message")
        return
    
    session_id = message.get("session_id")
    if not session_id:
        print("Message missing session_id, cannot respond")
        return
    
    # Process message...
```

### 3. Use Asynchronous Processing for Long-Running Tasks

For tasks that require long processing times, consider using asynchronous processing to avoid blocking the message loop.

### 4. Regularly Save Agent State

If your agent needs to maintain state, save it regularly to prevent data loss.

### 5. Monitoring and Logging

Implement appropriate logging and monitoring to track your agent's performance and issues in production.

## Example Applications

### Echo Bot

```python
def handle_message(message):
    session_id = message.get("session_id")
    content = message.get("content", "")
    
    # Simply reply with the user's message
    client.send_message(
        content=f"You said: {content}",
        session_id=session_id
    )
```

### Image Generation Bot

```python
def handle_message(message):
    """
    Process incoming messages and respond
    
    Args:
        message (dict): Message object with format:
            {
                "session_id": "unique-session-id",
                "id": 12345,  # Message ID
                "content": "user message text",
                "created_at": "2023-01-01T12:00:00"
            }
    """
    print(f"Received: {message['content']}")

    session_id = message.get("session_id")
    if not session_id:
        print("Message missing session_id, cannot respond")
        return
    
    # Get user's message
    user_message = message.get("content", "")

    # Get persona info
    persona_info = client.get_persona(session_id)
    
    # Create your response (this is where your agent logic goes)
    response = f"Echo: {user_message}"
    
    # Send response back to user
    client.send_message(content=response)
    print(f"Sent: {response}")
```





# PIN AI Open Controller API Guide

## Introduction

This document provides a comprehensive guide to the PIN AI Open Controller API endpoints. These endpoints allow developers to integrate with the PIN AI platform during hackathons and build custom applications leveraging PIN AI's agent capabilities.

## Authentication

All API endpoints require an API key for authentication. The API key must be included in the request header as `x-api-key`.

```
x-api-key: your_api_key_here  # Required
```

## API Endpoints

### 1. Register Agent

Create a new agent in the PIN AI platform.

**Endpoint:** `POST /api/sdk/register_agent`

**Request Body:**

```json
{
  "name": "Agent Name",           # Required: Agent's display name
  "url": "https://example.com/agent",  # Optional: URL associated with the agent
  "wallet": "0x...",             # Optional: Blockchain wallet address
  "category": "utility",         # Optional: Agent category
  "cover": "https://example.com/cover.jpg",  # Optional: Cover image URL
  "description": "Agent description"  # Required: Description of the agent
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Agent Name",
  "ticker": "SDK",
  "url": "https://example.com/agent",
  "wallet": "0x...",
  "category": "utility",
  "cover": "https://example.com/cover.jpg",
  "description": "Agent description",
  "created_at": "2025-03-07T10:41:04+08:00",
  "updated_at": "2025-03-07T10:41:04+08:00"
}
```

**Error Codes:**
- 409: Agent with the same name already exists
- 500: Server error

### 2. Poll Messages

Retrieve messages for a specific agent since a given timestamp.

**Endpoint:** `POST /api/sdk/poll_messages`

**Request Body:**

```json
{
  "agent_id": 1,               # Required: ID of the agent
  "since_timestamp": 1615000000000,  # Optional: Timestamp to retrieve messages from (milliseconds)
  "sender": "user"           # Optional: Filter by sender type ("user" or "agent")
}
```

**Response:**

```json
[
  {
    "id": 1,
    "session_id": "session_id_string",
    "message_type": "user",
    "content": "Hello, agent!",
    "media_type": null,
    "media_url": null,
    "meta_data": {},
    "created_at": "2025-03-07T10:41:04+08:00",
    "timestamp": 1615000000000,
    "avatar": "https://example.com/avatar.jpg"
  }
]
```

**Error Codes:**
- 403: You don't have access to this agent
- 500: Server error

### 3. Reply Message

Send a reply message from an agent to a user.

**Endpoint:** `POST /api/sdk/reply_message`

**Path Parameters:**
- `session_id`: String (Required) - The session ID for the conversation

**Request Body:**

```json
{
  "agent_id": 1,               # Required: ID of the agent sending the reply
  "persona_id": 1,            # Required: ID of the persona receiving the message
  "content": "Hello, user! I'm your agent.",  # Required: Message content
  "media_type": null,         # Optional: Type of media attached (image, video, audio, file)
  "media_url": null,          # Optional: URL to the attached media
  "meta_data": {}             # Optional: Additional metadata for the message
}
```

**Response:**

```json
{
  "id": 2,
  "session_id": "session_id_string",
  "message_type": "agent",
  "content": "Hello, user! I'm your agent.",
  "media_type": null,
  "media_url": null,
  "meta_data": {},
  "created_at": "2025-03-07T10:41:04+08:00"
}
```

**Error Codes:**
- 400: Invalid session ID
- 403: You don't have access to this agent
- 500: Server error

### 4. Upload Media

Upload media files (images, videos, audio, or other files) to be used in messages.

**Endpoint:** `POST /api/sdk/upload_media`

**Form Data:**
- `file`: File (Required) - The media file to upload
- `media_type`: String (Required) - One of: "image", "video", "audio", "file"

**Response:**

```json
{
  "media_type": "image",
  "media_url": "https://storage.example.com/media/image123.jpg"
}
```

**Error Codes:**
- 400: Invalid media type
- 500: Server error

### 5. Get Persona by Session

Retrieve persona information based on a session ID.

**Endpoint:** `GET /api/sdk/get_persona_by_session`

**Query Parameters:**
- `session_id`: String (Required) - The session ID to get persona for

**Response:**

```json
{
  "id": 1,
  "name": "Default User",
  "avatar": "https://example.com/avatar.jpg",
  "meta_data": {}
}
```

**Error Codes:**
- 400: Invalid session ID
- 404: Persona not found
- 500: Server error

### 6. Get Agents

Retrieve a list of agents owned by the authenticated user.

**Endpoint:** `GET /api/sdk/get_agents`

**Query Parameters:**
- `page`: Integer (Optional, default: 1) - Page number for pagination
- `page_size`: Integer (Optional, default: 10) - Number of items per page

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Agent Name",
      "ticker": "SDK",
      "url": "https://example.com/agent",
      "wallet": "0x...",
      "category": "utility",
      "cover": "https://example.com/cover.jpg",
      "description": "Agent description",
      "created_at": "2025-03-07T10:41:04+08:00",
      "updated_at": "2025-03-07T10:41:04+08:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

**Error Codes:**
- 500: Server error

### 7. Delete Agent

Delete an agent owned by the authenticated user.

**Endpoint:** `DELETE /api/sdk/delete_agent/{agent_id}`

**Path Parameters:**
- `agent_id`: Integer (Required) - The ID of the agent to delete

**Response:**

```json
{
  "success": true,
  "message": "Agent deleted successfully"
}
```

**Error Codes:**
- 403: You don't have access to this agent
- 404: Agent not found
- 500: Server error

## Message Types and Media Types

### Message Types
- `user`: Message sent by a user
- `agent`: Message sent by an agent

### Media Types
- `image`: Image file (supported formats: JPG, PNG, GIF)
- `video`: Video file (supported formats: MP4, WebM)
- `audio`: Audio file (supported formats: MP3, WAV)
- `file`: Other file types

## Parameter Requirements Summary

| API Endpoint | Parameter | Type | Required | Default | Description |
|--------------|-----------|------|----------|---------|-------------|
| All Endpoints | x-api-key | Header | Yes | - | API key for authentication |
| Register Agent | name | String | Yes | - | Agent's display name |
| Register Agent | url | String | No | null | URL associated with the agent |
| Register Agent | wallet | String | No | null | Blockchain wallet address |
| Register Agent | category | String | No | null | Agent category |
| Register Agent | cover | String | No | null | Cover image URL |
| Register Agent | description | String | Yes | - | Description of the agent |
| Poll Messages | agent_id | Integer | Yes | - | ID of the agent |
| Poll Messages | since_timestamp | Date/Time | No | null | Timestamp to retrieve messages from |
| Poll Messages | sender | String | No | null | Filter by sender type ("user" or "agent") |
| Reply Message | session_id | String | Yes | - | The session ID for the conversation |
| Reply Message | agent_id | Integer | Yes | - | ID of the agent sending the reply |
| Reply Message | persona_id | Integer | Yes | - | ID of the persona receiving the message |
| Reply Message | content | String | Yes | - | Message content |
| Reply Message | media_type | String | No | null | Type of media attached |
| Reply Message | media_url | String | No | null | URL to the attached media |
| Reply Message | meta_data | Object | No | null | Additional metadata for the message |
| Upload Media | file | File | Yes | - | The media file to upload |
| Upload Media | media_type | String | Yes | - | One of: "image", "video", "audio", "file" |
| Get Persona by Session | session_id | String | Yes | - | The session ID to get persona for |
| Get Agents | page | Integer | No | 1 | Page number for pagination |
| Get Agents | page_size | Integer | No | 10 | Number of items per page |
| Delete Agent | agent_id | Integer | Yes | - | The ID of the agent to delete |

## Best Practices

1. **Error Handling**: Always implement proper error handling for all API calls.
2. **Rate Limiting**: Be mindful of rate limits to avoid being throttled.
3. **Session Management**: Properly manage and store session IDs for ongoing conversations.
4. **Media Handling**: Optimize media files before uploading to improve performance.
5. **Security**: Never expose your API key in client-side code or public repositories.

## Example Integration

Here's a simple Python example of how to register an agent:

```python
import requests

api_key = "your_api_key_here"
api_url = "https://api.pin.ai/api/sdk/register_agent"

headers = {
    "x-api-key": api_key,  # Required
    "Content-Type": "application/json"
}

data = {
    "name": "My Hackathon Agent",  # Required
    "url": "https://myproject.example.com",  # Optional
    "wallet": "0x123456789abcdef",  # Optional
    "category": "entertainment",  # Optional
    "cover": "https://myproject.example.com/cover.jpg",  # Optional
    "description": "An amazing agent built for the hackathon"  # Required
}

response = requests.post(api_url, json=data, headers=headers)

if response.status_code == 200:
    agent = response.json()
    print(f"Agent created with ID: {agent['id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## Support

If you have any questions or need assistance, please reach out to the hackathon support team or refer to the additional documentation provided.

Good luck with your hackathon project!
