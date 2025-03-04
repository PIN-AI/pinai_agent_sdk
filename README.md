# PINAI Intent SDK

PINAI Intent SDK is a Python client library for interacting with the PINAI Intent Match API and blockchain-based agent registration.

## Installation

```bash
pip install pinai-intent-sdk
```

## Quick Start

```python
from pinai_intent_sdk import PINAIIntentSDK
from datetime import datetime

# Initialize SDK with HTTP API only
sdk = PINAIIntentSDK(
    base_url="https://ifemsp3wkd.us-east-1.awsapprunner.com/",
    api_key="your-hipin-api-key"
)

# Initialize SDK with blockchain support
sdk_with_blockchain = PINAIIntentSDK(
    base_url="https://ifemsp3wkd.us-east-1.awsapprunner.com/",
    api_key="your-hipin-api-key",
    privatekey="your-ethereum-private-key",  # Optional: For blockchain integration
    blockchainRPC="https://sepolia.base.org"  # Optional: Custom RPC endpoint
)

# Register a new agent (HTTP API only)
agent = sdk.register_agent(
    name="My Agent",
    category="general",
    description="A general purpose agent",
    api_endpoint="https://my-agent-endpoint.com",
    capabilities=["text", "image"],
    pricing_model={"per_request": 0.001},
    response_time=1.0,
    availability=1.0,
    metadata={"version": "1.0"}
)

# Register a new agent with blockchain integration
agent_with_blockchain = sdk_with_blockchain.register_agent(
    name="My Blockchain Agent",
    category="general",
    description="A blockchain-enabled agent",
    api_endpoint="https://my-agent-endpoint.com",
    capabilities=["text", "image"],
    pricing_model={"per_request": 0.001},
    response_time=1.0,
    availability=1.0,
    metadata={"version": "1.0"},
    agent_owner="0x..."  # Optional: Ethereum address of the agent owner
)

# List agents
agents = sdk.list_agents(category="general", capability="text")

# Get single agent info
agent_info = sdk.get_agent("general_my_agent")

# Update agent information
updated_agent = sdk.update_agent(
    agent_id="general_my_agent",
    response_time=0.8,
    availability=0.95
)

# Unregister agent
sdk.unregister_agent("general_my_agent")

# Get agent metrics
metrics = sdk.get_agent_metrics(
    agent_id="general_my_agent",
    start_time=datetime(2024, 1, 1),
    end_time=datetime(2024, 1, 31)
)
```

## Key Features

- Agent Management
  - Register new agents (with optional blockchain integration)
  - Update agent information
  - Get agent details
  - Unregister agents
- Agent Queries
  - List agents with category and capability filters
- Performance Monitoring
  - Get agent metrics within specified time ranges
- Blockchain Integration
  - On-chain agent registration
  - Smart contract interaction
  - Token-based agent ownership

## Blockchain Integration

When initialized with a private key, the SDK will register agents both through the HTTP API and on the blockchain. The blockchain integration provides:

- Decentralized agent registry
- Token-based ownership
- Verifiable agent status
- Secure stake management

### Configuration

- `privatekey`: Ethereum private key for blockchain transactions
- `blockchainRPC`: RPC endpoint URL (defaults to Base Sepolia)
- `agent_owner`: Optional Ethereum address for agent ownership (defaults to transaction signer)

## Documentation

For detailed documentation, visit [https://docs.pinai.io](https://docs.pinai.io)
```