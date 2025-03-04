import pytest
from unittest.mock import patch
from pinai_intent_sdk import PINAIIntentSDK
from pinai_intent_sdk.models import AgentCategory
from eth_account import Account

# Test private key (this is a test account, DO NOT use in production)
TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
# Test account for agent owner (this is a test account, DO NOT use in production)
TEST_OWNER_PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

def test_register_agent_with_blockchain():
    """Test registering an agent with blockchain interaction"""
    
    # Initialize SDK with blockchain support
    sdk = PINAIIntentSDK(
        base_url="http://localhost:8000",  # Dummy API URL
        privatekey=TEST_PRIVATE_KEY,
        blockchainRPC="http://127.0.0.1:8545"
    )
    
    # Create test owner account
    test_owner = Account.from_key(TEST_OWNER_PRIVATE_KEY)
    
    # Mock the HTTP API call since we're only testing blockchain
    with patch.object(sdk, '_make_request') as mock_request:
        mock_request.return_value = {"status": "success"}
        
        # Register an agent with specific owner
        result = sdk.register_agent(
            name="Test Agent",
            category=AgentCategory.TRANSPORT,
            description="Test agent for blockchain interaction",
            api_endpoint="http://test-agent.com",
            capabilities=["test"],
            pricing_model={"per_request": 0.001},
            response_time=1.0,
            availability=1.0,
            agent_owner=test_owner.address
        )
        
        # Verify HTTP API was called
        assert mock_request.called
        
        # Note: The blockchain transaction verification is handled within the SDK
        # If we reach this point without exceptions, the blockchain interaction was successful
        assert result["status"] == "success"

def test_register_agent_without_owner():
    """Test registering an agent without specifying owner"""
    
    # Initialize SDK with blockchain support
    sdk = PINAIIntentSDK(
        base_url="http://localhost:8000",  # Dummy API URL
        privatekey=TEST_PRIVATE_KEY,
        blockchainRPC="http://127.0.0.1:8545"
    )
    
    # Mock the HTTP API call since we're only testing blockchain
    with patch.object(sdk, '_make_request') as mock_request:
        mock_request.return_value = {"status": "success"}
        
        # Register an agent without owner (should default to sender)
        result = sdk.register_agent(
            name="Test Agent",
            category=AgentCategory.TRANSPORT,
            description="Test agent for blockchain interaction",
            api_endpoint="http://test-agent.com",
            capabilities=["test"],
            pricing_model={"per_request": 0.001},
            response_time=1.0,
            availability=1.0
        )
        
        # Verify HTTP API was called
        assert mock_request.called
        
        # Note: The blockchain transaction verification is handled within the SDK
        # If we reach this point without exceptions, the blockchain interaction was successful
        assert result["status"] == "success" 