import pytest
from unittest.mock import patch, MagicMock
from pinai_agent_sdk.pinai_agent_sdk import (
    PINAIAgentSDK,
    AGENT_CATEGORY_SOCIAL,
    AGENT_CATEGORY_AI_CHAT
)
from eth_account import Account

# Test private keys (these are test accounts, DO NOT use in production)
TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
# Test agent owner account (this is a test account, DO NOT use in production)
TEST_OWNER_PRIVATE_KEY = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

def test_register_agent_with_blockchain():
    """Test registering an agent with blockchain interaction"""
    
    # Initialize SDK with blockchain support
    sdk = PINAIAgentSDK(
        api_key="test-api-key",
        base_url="http://localhost:8000",  # Test API URL
        privatekey=TEST_PRIVATE_KEY,
        blockchainRPC="http://127.0.0.1:8545"
    )
    
    # Create test owner account
    test_owner = Account.from_key(TEST_OWNER_PRIVATE_KEY)
    
    # Mock Web3 and contract methods
    sdk.web3 = MagicMock()
    sdk.web3.eth.get_transaction_count.return_value = 1
    sdk.web3.eth.max_priority_fee = 1000000000
    sdk.web3.eth.get_block.return_value = {'baseFeePerGas': 1000000000}
    sdk.web3.to_wei.return_value = 0
    sdk.web3.keccak.return_value = b'0' * 32
    sdk.web3.to_checksum_address = MagicMock(return_value="0xChecksumAddress")
    
    # Mock contract functions
    mock_function = MagicMock()
    mock_function.build_transaction.return_value = {
        'from': '0x123',
        'nonce': 1,
        'value': 0,
        'gas': 500000,
        'type': '0x2',
        'maxFeePerGas': 3000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    sdk.contract = MagicMock()
    sdk.contract.functions.create.return_value = mock_function
    
    # Mock account
    mock_signed_tx = MagicMock()
    mock_signed_tx.raw_transaction = b'0x123'
    
    mock_account = MagicMock()
    mock_account.address = "0x0000000000000000000000000000000000000123"  # Use valid Ethereum address format
    mock_account.sign_transaction.return_value = mock_signed_tx
    sdk.account = mock_account
    
    # Mock transaction sending and receipt
    sdk.web3.eth.send_raw_transaction.return_value = b'0x456'
    sdk.web3.eth.wait_for_transaction_receipt.return_value = {'status': 1, 'blockNumber': 12345}
    
    # Mock HTTP API call
    with patch.object(sdk, '_make_request') as mock_request:
        mock_request.return_value = {"id": 123, "status": "success"}
        
        # Register agent with specific owner
        result = sdk.register_agent(
            name="Test Agent",
            description="Test agent for blockchain interaction",
            category=AGENT_CATEGORY_SOCIAL,
            wallet="0x1234567890123456789012345678901234567890",
            agent_owner=test_owner.address
        )
        
        # Verify HTTP API was called
        assert mock_request.called
        
        # Verify blockchain interaction was successful
        assert sdk.contract.functions.create.called
        assert sdk.account.sign_transaction.called
        assert sdk.web3.eth.send_raw_transaction.called
        assert sdk.web3.eth.wait_for_transaction_receipt.called
        
        # Verify results
        assert result["id"] == 123
        assert result["status"] == "success"

def test_register_agent_without_owner():
    """Test registering an agent without specifying owner"""
    
    # Initialize SDK with blockchain support
    sdk = PINAIAgentSDK(
        api_key="test-api-key",
        base_url="http://localhost:8000",  # Test API URL
        privatekey=TEST_PRIVATE_KEY,
        blockchainRPC="http://127.0.0.1:8545"
    )
    
    # Mock Web3 and contract methods
    sdk.web3 = MagicMock()
    sdk.web3.eth.get_transaction_count.return_value = 1
    sdk.web3.eth.max_priority_fee = 1000000000
    sdk.web3.eth.get_block.return_value = {'baseFeePerGas': 1000000000}
    sdk.web3.to_wei.return_value = 0
    sdk.web3.keccak.return_value = b'0' * 32
    sdk.web3.to_checksum_address = MagicMock(return_value="0xChecksumAddress")
    
    # Mock contract functions
    mock_function = MagicMock()
    mock_function.build_transaction.return_value = {
        'from': '0x123',
        'nonce': 1,
        'value': 0,
        'gas': 500000,
        'type': '0x2',
        'maxFeePerGas': 3000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    sdk.contract = MagicMock()
    sdk.contract.functions.create.return_value = mock_function
    
    # Mock account
    mock_signed_tx = MagicMock()
    mock_signed_tx.raw_transaction = b'0x123'
    
    mock_account = MagicMock()
    mock_account.address = "0x0000000000000000000000000000000000000123"  # Use valid Ethereum address format
    mock_account.sign_transaction.return_value = mock_signed_tx
    sdk.account = mock_account
    
    # Mock transaction sending and receipt
    sdk.web3.eth.send_raw_transaction.return_value = b'0x456'
    sdk.web3.eth.wait_for_transaction_receipt.return_value = {'status': 1, 'blockNumber': 12345}
    
    # Mock HTTP API call
    with patch.object(sdk, '_make_request') as mock_request:
        mock_request.return_value = {"id": 456, "status": "success"}
        
        # Register agent without specifying owner
        result = sdk.register_agent(
            name="Test Agent",
            description="Test agent for blockchain interaction",
            category=AGENT_CATEGORY_AI_CHAT
        )
        
        # Verify HTTP API was called
        assert mock_request.called
        
        # Verify blockchain interaction was successful
        assert sdk.contract.functions.create.called
        assert sdk.account.sign_transaction.called
        assert sdk.web3.eth.send_raw_transaction.called
        assert sdk.web3.eth.wait_for_transaction_receipt.called
        
        # Verify results
        assert result["id"] == 456
        assert result["status"] == "success"

def test_unregister_agent():
    """Test unregistering an agent"""
    
    # Initialize SDK with blockchain support
    sdk = PINAIAgentSDK(
        api_key="test-api-key",
        base_url="http://localhost:8000",  # Test API URL
        privatekey=TEST_PRIVATE_KEY,
        blockchainRPC="http://127.0.0.1:8545"
    )
    
    # Set agent info
    sdk._agent_info = {"id": 789}
    
    # Mock Web3 and contract methods
    sdk.web3 = MagicMock()
    sdk.web3.eth.get_transaction_count.return_value = 1
    sdk.web3.eth.max_priority_fee = 1000000000
    sdk.web3.eth.get_block.return_value = {'baseFeePerGas': 1000000000}
    sdk.web3.to_checksum_address = MagicMock(return_value="0xChecksumAddress")
    
    # Mock contract functions
    mock_function = MagicMock()
    mock_function.build_transaction.return_value = {
        'from': '0x123',
        'nonce': 1,
        'gas': 300000,
        'type': '0x2',
        'maxFeePerGas': 3000000000,
        'maxPriorityFeePerGas': 1000000000,
    }
    sdk.contract = MagicMock()
    sdk.contract.functions.updateAgentStatusByAgentId.return_value = mock_function
    
    # Mock account
    mock_signed_tx = MagicMock()
    mock_signed_tx.raw_transaction = b'0x123'
    
    mock_account = MagicMock()
    mock_account.address = "0x0000000000000000000000000000000000000123"  # Use valid Ethereum address format
    mock_account.sign_transaction.return_value = mock_signed_tx
    sdk.account = mock_account
    
    # Mock transaction sending and receipt
    sdk.web3.eth.send_raw_transaction.return_value = b'0x456'
    sdk.web3.eth.wait_for_transaction_receipt.return_value = {'status': 1, 'blockNumber': 12345}
    
    # Mock HTTP API call
    with patch.object(sdk, '_make_request') as mock_request:
        mock_request.return_value = {"status": "success"}
        
        # Unregister agent
        result = sdk.unregister_agent()
        
        # Verify HTTP API was called
        assert mock_request.called
        
        # Verify blockchain interaction was successful
        assert sdk.contract.functions.updateAgentStatusByAgentId.called
        assert sdk.account.sign_transaction.called
        assert sdk.web3.eth.send_raw_transaction.called
        assert sdk.web3.eth.wait_for_transaction_receipt.called
        
        # Verify results
        assert result["status"] == "success"
        
        # Verify agent info was cleared
        assert sdk._agent_info is None

def test_string_truncation():
    """Test string truncation functionality"""
    
    # Initialize SDK
    sdk = PINAIAgentSDK(
        api_key="test-api-key",
        base_url="http://localhost:8000"
    )
    
    # Test string that doesn't need truncation
    short_string = "Short string"
    assert sdk._truncate_string(short_string) == short_string
    
    # Test string that needs truncation
    long_string = "x" * 300
    truncated = sdk._truncate_string(long_string)
    assert len(truncated) == 256
    assert truncated == long_string[:256]
    
    # Test empty string
    assert sdk._truncate_string("") == ""
    assert sdk._truncate_string(None) == ""
    
    # Test custom max length
    custom_length = 10
    assert len(sdk._truncate_string(long_string, custom_length)) == custom_length

if __name__ == "__main__":
    # Run tests
    pytest.main(["-xvs", "tests/test_pinai_agent_sdk.py"]) 