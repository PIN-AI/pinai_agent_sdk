"""
PINAIAgentSDK - Python SDK for PINAI Agent API
"""

import time
import threading
import logging
import requests
import json
import os
import uuid
from typing import Dict, List, Any, Optional, Callable, Union
from urllib.parse import urljoin
from web3 import Web3
from eth_account import Account

CONTRACT_ADDRESS = "0xD2004b20B39A6b4397df87dadDaEFB0aEfe32089"
DEFAULT_RPC = "https://sepolia.base.org"
MIN_STAKE = 0
REGISTRATION_FEE = 0
MAX_STRING_LENGTH = 256

CONTRACT_ABI = [
    # VERSION
    {
        "inputs": [],
        "name": "VERSION",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    # create
    {
        "inputs": [
            {"internalType": "address", "name": "_agentOwner", "type": "address"},
            {"internalType": "string", "name": "_agentName", "type": "string"},
            {"internalType": "string", "name": "_serviceEndpoint", "type": "string"},
            {"internalType": "string", "name": "_description", "type": "string"},
            {"internalType": "uint256", "name": "_agentId", "type": "uint256"},
            {"internalType": "bytes32", "name": "_category", "type": "bytes32"}
        ],
        "name": "create",
        "outputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    # updateAgentStatusByAgentId
    {
        "inputs": [
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "enum AgentManager.AgentStatus", "name": "newStatus", "type": "uint8"}
        ],
        "name": "updateAgentStatusByAgentId",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # getAgentByAgentId
    {
        "inputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "name": "getAgentByAgentId",
        "outputs": [{
            "components": [
                {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                {"internalType": "uint256", "name": "agentId", "type": "uint256"},
                {"internalType": "string", "name": "name", "type": "string"},
                {"internalType": "string", "name": "serviceEndpoint", "type": "string"},
                {"internalType": "string", "name": "description", "type": "string"},
                {"internalType": "bytes32", "name": "category", "type": "bytes32"},
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "tba", "type": "address"},
                {"internalType": "uint256", "name": "stakeAmount", "type": "uint256"},
                {"internalType": "uint8", "name": "reputationScore", "type": "uint8"},
                {"internalType": "enum AgentManager.AgentStatus", "name": "status", "type": "uint8"},
                {"internalType": "uint64", "name": "lastActiveTime", "type": "uint64"},
                {"internalType": "uint64", "name": "bidCount", "type": "uint64"},
                {"internalType": "uint64", "name": "dealCount", "type": "uint64"}
            ],
            "internalType": "struct AgentManager.Agent",
            "name": "",
            "type": "tuple"
        }],
        "stateMutability": "view",
        "type": "function"
    },
    # getAgentStatus
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "getAgentStatus",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Import constants
from .constants import (
    AGENT_CATEGORY_SOCIAL,
    AGENT_CATEGORY_DAILY,
    AGENT_CATEGORY_PRODUCTIVITY,
    AGENT_CATEGORY_WEB3,
    AGENT_CATEGORY_SHOPPING,
    AGENT_CATEGORY_FINANCE,
    AGENT_CATEGORY_AI_CHAT,
    AGENT_CATEGORY_OTHER,
    CATEGORY_DISPLAY_NAMES
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PINAIAgentSDK")

class PINAIAgentSDKError(Exception):
    """Base exception class for PINAIAgentSDK"""
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class AuthenticationError(PINAIAgentSDKError):
    """Raised when API authentication fails (401 errors)"""
    pass

class PermissionError(PINAIAgentSDKError):
    """Raised when permissions are insufficient (403 errors)"""
    pass

class ResourceNotFoundError(PINAIAgentSDKError):
    """Raised when a requested resource is not found (404 errors)"""
    pass

class ResourceConflictError(PINAIAgentSDKError):
    """Raised when there's a resource conflict (409 errors)"""
    pass

class ValidationError(PINAIAgentSDKError):
    """Raised when request validation fails (400 errors)"""
    pass

class ServerError(PINAIAgentSDKError):
    """Raised when the server returns 5xx errors"""
    pass

class NetworkError(PINAIAgentSDKError):
    """Raised when network connection issues occur"""
    pass

class PINAIAgentSDK:
    """
    SDK for PINAI Agent API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://dev-agent.api.pinai.tech", timeout: int = 30, polling_interval: float = 1.0, privatekey: Optional[str] = None, blockchainRPC: Optional[str] = None):
        """
        Initialize PINAIAgentSDK

        Args:
            api_key (str): PINAI API Key
            base_url (str, optional): Base URL for API. Defaults to "https://dev-agent.api.pinai.tech/users/api-keys".
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            polling_interval (float, optional): Interval in seconds between message polls. Defaults to 1.0.
            privatekey (str, optional): Private key for blockchain interaction. If provided, blockchain functionality will be enabled.
            blockchainRPC (str, optional): Blockchain RPC URL. Defaults to "https://sepolia.base.org".
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.polling_interval = polling_interval
        self.polling_thread = None
        self.stop_polling = False
        self.message_callback = None
        self._agent_info = None
        self._last_poll_timestamp = None
        self._session_id = None  
        self._personas_cache = {}  
        
        # Check if base_url ends with a slash, add it if not
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        logger.info(f"PINAIAgentSDK initialized with base URL: {base_url}")
        
        self.web3 = None
        self.contract = None
        self.account = None
        
        if privatekey:
            try:
                rpc_url = blockchainRPC or DEFAULT_RPC
                self.web3 = Web3(Web3.HTTPProvider(rpc_url))
                
                self.account = Account.from_key(privatekey)
                
                self.contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                    abi=CONTRACT_ABI
                )
                
                logger.info(f"Blockchain components initialized with account: {self.account.address}")
            except Exception as e:
                logger.error(f"Failed to initialize blockchain components: {e}")
                raise
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, files: Dict = None) -> Dict:
        """
        Send HTTP request

        Args:
            method (str): HTTP method (GET, POST, DELETE, etc.)
            endpoint (str): API endpoint
            data (Dict, optional): Request data. Defaults to None.
            headers (Dict, optional): Request headers. Defaults to None.
            files (Dict, optional): Files to upload. Defaults to None.

        Returns:
            Dict: API response

        Raises:
            AuthenticationError: When API Key is invalid (401)
            PermissionError: When lacking permissions to perform action (403)
            ResourceNotFoundError: When requested resource does not exist (404)
            ResourceConflictError: When there's a resource conflict (409)
            ValidationError: When request parameters are invalid (400)
            ServerError: When server returns 5xx errors
            NetworkError: When network connection issues occur
        """
        url = urljoin(self.base_url, endpoint)
        
        # Prepare headers
        default_headers = {
            "X-API-Key": self.api_key
        }
        
        # Add Content-Type header if not a file upload
        if not files:
            default_headers["Content-Type"] = "application/json"
            
        # Merge custom headers
        if headers:
            default_headers.update(headers)
            
        try:
            if files:
                # For file uploads, use data parameter for form data
                response = requests.request(
                    method=method,
                    url=url,
                    data=data,
                    headers=default_headers,
                    files=files,
                    timeout=self.timeout
                )
            else:
                # For regular requests, use json parameter for JSON payload
                response = requests.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    headers=default_headers,
                    timeout=self.timeout
                )
            
            # Parse error details if available
            error_detail = None
            try:
                if response.status_code >= 400:
                    error_content = response.json()
                    error_detail = error_content.get('detail', None)
            except (ValueError, KeyError, json.JSONDecodeError):
                error_detail = response.text if response.text else None
            
            # Handle different HTTP status codes with specific exceptions
            if response.status_code == 400:
                raise ValidationError(
                    f"Bad request: {error_detail or 'Invalid parameters'}",
                    status_code=response.status_code,
                    response=response
                )
            elif response.status_code == 401:
                raise AuthenticationError(
                    f"Authentication failed: {error_detail or 'Invalid API Key'}",
                    status_code=response.status_code,
                    response=response
                )
            elif response.status_code == 403:
                raise PermissionError(
                    f"Permission denied: {error_detail or 'Insufficient permissions to perform this action'}",
                    status_code=response.status_code,
                    response=response
                )
            elif response.status_code == 404:
                raise ResourceNotFoundError(
                    f"Resource not found: {error_detail or 'The requested resource does not exist'}",
                    status_code=response.status_code,
                    response=response
                )
            elif response.status_code == 409:
                raise ResourceConflictError(
                    f"Resource conflict: {error_detail or 'A resource with the provided details already exists'}",
                    status_code=response.status_code,
                    response=response
                )
            if response.status_code == 422:
                raise ValidationError(
                    f"Error parameters: {error_detail or 'Invalid parameters'}",
                    status_code=response.status_code,
                    response=response
                )
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {error_detail or f'The server returned status code {response.status_code}'}",
                    status_code=response.status_code,
                    response=response
                )
            
            # If we get here, ensure the response status is successful
            response.raise_for_status()
            
            # Return JSON response
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError(f"Failed to connect to server: {e}", response=None)
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise NetworkError(f"Request timed out after {self.timeout} seconds", response=None)
        except requests.exceptions.RequestException as e:
            # This catches any other requests exceptions not caught above
            logger.error(f"Request error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                raise PINAIAgentSDKError(f"Request failed with status code {status_code}", status_code=status_code, response=e.response)
            else:
                raise NetworkError(f"Request failed: {e}", response=None)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            # This catches JSON parsing errors
            logger.error(f"Failed to parse response: {e}")
            raise PINAIAgentSDKError(f"Failed to parse response: {e}", response=response if 'response' in locals() else None)
            
    def register_agent(self, name: str, description: str, category: str = AGENT_CATEGORY_SOCIAL, wallet: str = "0x0", cover: str = None, metadata: Dict = None, agent_owner: Optional[str] = None) -> Dict:
        """
        Register a new agent

        Args:
            name (str): Agent name
            description (str): Agent description
            category (str): Agent category (must be one of the valid categories from the AGENT_CATEGORY_* constants)
            wallet (str, optional): Agent wallet address. Defaults to None.
            cover (str, optional): Agent cover image URL. Defaults to None.
            metadata (Dict, optional): Additional metadata. Defaults to None.
            agent_owner (str, optional): Ethereum address of the agent owner. If not provided, the current account address will be used.

        Returns:
            Dict: Registration response including agent ID
            
        Raises:
            ValidationError: When name, description or category are invalid
            ResourceConflictError: When agent name already exists (409)
            AuthenticationError: When API Key is invalid (401)
            ServerError: When server returns 5xx errors
            NetworkError: When network connection issues occur
            
        Example:
            >>> from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL
            >>> sdk = PINAIAgentSDK(api_key="your_api_key")
            >>> sdk.register_agent(
            ...     name="My Social Agent",
            ...     description="A social agent for chatting",
            ...     category="social"
            ... )
        """
        if not name or not description or not category:
            raise ValidationError("Agent name, description, and category are required fields")
            
        if category not in CATEGORY_DISPLAY_NAMES:
            categories_str = ", ".join([f"{k} ({v})" for k, v in CATEGORY_DISPLAY_NAMES.items()])
            raise ValidationError(f"Invalid category. Must be one of: {categories_str}")
            
        data = {
            "name": name,
            "description": description,
            "category": category,
            "wallet": "0x0"
        }
        
        if wallet:
            data["wallet"] = wallet
            
        if cover:
            data["cover"] = cover
            
        if metadata:
            data["metadata"] = metadata
            
        try:
            response = self._make_request("POST", "api/sdk/register_agent", data=data)
            
            # Save agent info for later use
            self._agent_info = response
            
            logger.info(f"Agent registered: {name} (ID: {response.get('id')})")
            
        except ResourceConflictError as e:
            # Provide more helpful error message for agent name conflicts
            logger.error(f"Agent registration failed: {e}")
            raise ResourceConflictError(
                f"An agent with the name '{name}' already exists. Please choose a different name.",
                status_code=e.status_code,
                response=e.response
            )
        # Other errors are already handled by _make_request
        
        # If blockchain functionality is enabled, call the smart contract
        if self.web3 and self.contract and self.account:
            try:
                # Get the agent ID from the response
                agent_id = response.get('id')
                if not agent_id:
                    logger.error("Failed to get agent ID from API response")
                    raise ValueError("Failed to get agent ID from API response")
                
                # Check and truncate string parameters
                safe_name = self._truncate_string(name)
                safe_description = self._truncate_string(description)
                # Use ticker as service endpoint
                safe_endpoint = self._truncate_string("http://default.endpoint")
                
                # Get nonce
                nonce = self.web3.eth.get_transaction_count(self.account.address)
                
                # Build contract transaction
                # Note: Contract requires sending MIN_STAKE + REGISTRATION_FEE
                min_stake = self.web3.to_wei(MIN_STAKE, 'ether')
                registration_fee = self.web3.to_wei(REGISTRATION_FEE, 'ether')
                total_value = min_stake + registration_fee
                
                # Set reasonable gas limit - increase to handle complex contract operations
                gas_limit = 800000 
                
                # Use provided agent_owner or default to current account address
                owner_address = agent_owner if agent_owner else self.account.address
                # Convert to checksum address
                owner_address = Web3.to_checksum_address(owner_address)
                
                # Convert category to bytes32
                category_bytes = self.web3.to_bytes(text=category).ljust(32, b'\0')
                
                logger.debug(f"Building contract transaction with parameters:")
                logger.debug(f"  - owner_address: {owner_address}")
                logger.debug(f"  - safe_name: {safe_name}")
                logger.debug(f"  - safe_endpoint: {safe_endpoint}")
                logger.debug(f"  - safe_description: {safe_description}")
                logger.debug(f"  - agent_id: {agent_id}")
                logger.debug(f"  - category: {category} (converted to bytes32)")
                
                # Build contract transaction
                contract_txn = self.contract.functions.create(
                    owner_address,
                    safe_name,
                    safe_endpoint,
                    safe_description,
                    agent_id,
                    category_bytes
                ).build_transaction({
                    'from': self.account.address,
                    'nonce': nonce,
                    'value': total_value,
                    'gas': gas_limit,
                    'type': '0x2',  # EIP-1559
                    'maxFeePerGas': self.web3.eth.max_priority_fee + (2 * self.web3.eth.get_block('latest')['baseFeePerGas']),
                    'maxPriorityFeePerGas': self.web3.eth.max_priority_fee,
                })
                
                # Sign transaction
                signed_txn = self.account.sign_transaction(contract_txn)
                
                # Send transaction
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
                # Wait for transaction confirmation
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(
                    tx_hash,
                    timeout=60,  # Increase timeout to 60 seconds
                    poll_latency=1
                )
                
                if tx_receipt['status'] != 1:
                    error_msg = "Blockchain transaction failed"
                    logger.error(error_msg)
                    # Try to get more details about the failure
                    try:
                        # Try to get transaction details
                        tx = self.web3.eth.get_transaction(tx_hash)
                        logger.error(f"Failed transaction details: {tx}")
                        # Try to get revert reason
                        result = self.web3.eth.call(tx, tx_receipt.blockNumber)
                        logger.error(f"Revert reason: {result}")
                    except Exception as e:
                        logger.error(f"Could not get detailed error info: {e}")
                    raise Exception("Blockchain transaction failed")
                
                logger.info(f"Agent registered on blockchain with agent_id: {agent_id}, transaction hash: {tx_hash.hex()}, block: {tx_receipt['blockNumber']}")
            except Exception as e:
                logger.error(f"Blockchain interaction failed: {str(e)}")
                logger.warning("Continuing with API-only registration due to blockchain error")
                # In production, you might want to raise the exception instead
                # raise Exception(f"Blockchain registration failed: {str(e)}")
        
        
        logger.info(f"Agent registered: {name} (ID: {response.get('id')})")
        return response
    
    def _truncate_string(self, input_str: str, max_length: int = MAX_STRING_LENGTH) -> str:
        """
        Truncate string to ensure it doesn't exceed the maximum length

        Args:
            input_str (str): Input string
            max_length (int, optional): Maximum length. Defaults to MAX_STRING_LENGTH.

        Returns:
            str: Truncated string
        """
        if not input_str:
            return ""
        
        if len(input_str) <= max_length:
            return input_str
        
        logger.warning(f"String truncated from {len(input_str)} to {max_length} characters")
        return input_str[:max_length]
        
    def unregister_agent(self, agent_id: int = None) -> Dict:
        """
        Unregister an agent

        Args:
            agent_id (int, optional): Agent ID. If not provided, uses the registered agent ID.

        Returns:
            Dict: Unregistration response
            
        Raises:
            ValidationError: When agent_id is missing
            ResourceNotFoundError: When agent doesn't exist (404)
            AuthenticationError: When API Key is invalid (401)
            ServerError: When server returns 5xx errors
            NetworkError: When network connection issues occur
        """
        # Use saved agent_id if not provided
        if agent_id is None:
            if not self._agent_info or "id" not in self._agent_info:
                raise ValidationError("No agent ID provided and no registered agent found")
            agent_id = self._agent_info["id"]
        
        # If blockchain functionality is enabled, call the smart contract
        if self.web3 and self.contract and self.account:
            try:
                # Get nonce
                nonce = self.web3.eth.get_transaction_count(self.account.address)
                
                # Set reasonable gas limit
                gas_limit = 300000
                
                logger.debug(f"Unregistering agent on blockchain - Agent ID: {agent_id}")
                
                # Call updateAgentStatusByAgentId method, set status to 2 (disabled)
                contract_txn = self.contract.functions.updateAgentStatusByAgentId(
                    agent_id,
                    2  # Status 2 means disabled
                ).build_transaction({
                    'from': self.account.address,
                    'nonce': nonce,
                    'gas': gas_limit,
                    'type': '0x2',  # EIP-1559
                    'maxFeePerGas': self.web3.eth.max_priority_fee + (2 * self.web3.eth.get_block('latest')['baseFeePerGas']),
                    'maxPriorityFeePerGas': self.web3.eth.max_priority_fee,
                })
                
                # Sign transaction
                signed_txn = self.account.sign_transaction(contract_txn)
                
                # Send transaction
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                logger.debug(f"Transaction sent with hash: {tx_hash.hex()}")
                
                # Wait for transaction confirmation
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(
                    tx_hash,
                    timeout=60,  # Increase timeout to 60 seconds
                    poll_latency=1
                )
                
                if tx_receipt['status'] != 1:
                    error_msg = "Blockchain transaction failed"
                    logger.error(error_msg)
                    # Try to get more details about the failure
                    try:
                        # Try to get transaction details
                        tx = self.web3.eth.get_transaction(tx_hash)
                        logger.error(f"Failed transaction details: {tx}")
                        # Try to get revert reason
                        result = self.web3.eth.call(tx, tx_receipt.blockNumber)
                        logger.error(f"Revert reason: {result}")
                    except Exception as e:
                        logger.error(f"Could not get detailed error info: {e}")
                    logger.warning("Continuing with API-only unregistration due to blockchain error")
                else:
                    logger.info(f"Agent unregistered on blockchain - Agent ID: {agent_id}, Transaction hash: {tx_hash.hex()}, Block: {tx_receipt['blockNumber']}")
                
            except Exception as e:
                logger.error(f"Blockchain interaction failed: {str(e)}")
                logger.warning("Continuing with API-only unregistration due to blockchain error")
        
        # Make API request to unregister agent
        try:
            response = self._make_request("POST", f"api/sdk/delete/agent/{agent_id}")
            
            # Clear agent info if it matches
            if self._agent_info and self._agent_info.get("id") == agent_id:
                self._agent_info = None
                
            logger.info(f"Agent unregistered via API: {agent_id}")
            return response
        except ResourceNotFoundError as e:
            logger.error(f"Agent not found: {agent_id}")
            # Still clear agent info if it matches
            if self._agent_info and self._agent_info.get("id") == agent_id:
                self._agent_info = None
            raise
    
    def _poll_messages(self):
        """
        Internal method for polling messages
        """
        if not self._agent_info or "id" not in self._agent_info:
            raise ValueError("No registered agent found. Call register_agent() first.")
        
        agent_id = self._agent_info["id"]
        
        # Initialize timestamp for first poll if not set
        if not self._last_poll_timestamp:
            # Use current time for first poll
            self._last_poll_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        backoff_time = 1.0
        max_backoff_time = 60.0  # Maximum backoff time in seconds
        
        while not self.stop_polling:
            try:
                # Prepare poll request data
                data = {
                    "agent_id": agent_id,
                    "since_timestamp": self._last_poll_timestamp,
                    "sender": "user"
                }
                
                # Get new messages
                response = self._make_request("POST", "api/sdk/poll_messages", data=data)
                
                # Process each message if there are any and callback is set
                if response and isinstance(response, list) and self.message_callback:
                    for message in response:
                        # Update last poll timestamp to latest message timestamp
                        if message.get("created_at") and (not self._last_poll_timestamp or message["created_at"] > self._last_poll_timestamp):
                            self._last_poll_timestamp = message["created_at"]
                            
                        # update session_id
                        if message.get("session_id"):
                            self._session_id = message.get("session_id")
                            
                        # Call message handler callback
                        self.message_callback(message)
                
                # Reset error count and backoff on successful poll
                consecutive_errors = 0
                backoff_time = self.polling_interval
                
            except AuthenticationError as e:
                logger.error(f"Authentication error while polling messages: {e}")
                # Exit polling loop on authentication errors as they're unlikely to resolve
                logger.critical("Authentication error detected. Stopping polling.")
                self.stop_polling = True
                break
                
            except (ValidationError, ResourceNotFoundError, ResourceConflictError) as e:
                # These are client errors that should be addressed
                logger.error(f"Client error while polling messages: {e}")
                consecutive_errors += 1
                
            except ServerError as e:
                # Server errors may be temporary
                logger.error(f"Server error while polling messages: {e}")
                consecutive_errors += 1
                # Implement exponential backoff for server errors
                backoff_time = min(backoff_time * 2, max_backoff_time)
                
            except NetworkError as e:
                # Network errors may be temporary
                logger.error(f"Network error while polling messages: {e}")
                consecutive_errors += 1
                # Implement exponential backoff for network errors
                backoff_time = min(backoff_time * 2, max_backoff_time)
                
            except Exception as e:
                # Catch any unexpected exceptions
                logger.error(f"Unexpected error while polling messages: {e}")
                consecutive_errors += 1
                
            # Check if we've hit max consecutive errors
            if consecutive_errors >= max_consecutive_errors:
                logger.warning(f"Reached {max_consecutive_errors} consecutive errors while polling. Stopping.")
                self.stop_polling = True
                break
                
            # Wait specified interval (or backoff time) before polling again
            logger.debug(f"Waiting {backoff_time} seconds before next poll")
            time.sleep(backoff_time)
    
    def _start(self, on_message_callback: Callable[[Dict], None], agent_id: int = None, blocking: bool = False) -> None:
        """
        Start listening for new messages

        Args:
            on_message_callback (Callable[[Dict], None]): Callback function for new messages
            agent_id (int, optional): If provided, uses this agent ID instead of registering a new one.
            blocking (bool, optional): If True, the method will block and not return until stop() is called.
                                       If False, polling runs in background thread. Defaults to False.
        """
        # If agent_id is provided, use it directly instead of registering a new agent
        if agent_id is not None:
            # Create agent_info data structure
            self._agent_info = {"id": agent_id}
            logger.info(f"Using provided agent ID: {agent_id}")
        elif not self._agent_info or "id" not in self._agent_info:
            raise ValueError("No agent ID provided and no registered agent found. Either call register_agent() first or provide agent_id.")
        
        # Save message callback
        self.message_callback = on_message_callback
        
        # Start polling thread
        self.stop_polling = False
        self.polling_thread = threading.Thread(target=self._poll_messages)
        self.polling_thread.daemon = True
        self.polling_thread.start()
        
        logger.info("Started listening for messages")
        
        # If blocking is True, keep the main thread alive until stopped
        if blocking:
            try:
                while not self.stop_polling and self.polling_thread.is_alive():
                    time.sleep(0.1)  # Small sleep to prevent high CPU usage
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, stopping...")
                self.stop()
        
    def start_and_run(self, on_message_callback: Callable[[Dict], None], agent_id: int = None) -> None:
        """
        Start message listening and keep running until user interruption.
        This is a convenience combination method of _start() and run_forever().

        Args:
            on_message_callback (Callable[[Dict], None]): Callback function for new messages
            agent_id (int, optional): If provided, uses this agent ID instead of registering a new one
        """
        # First start message listening (non-blocking mode)
        self._start(on_message_callback=on_message_callback, agent_id=agent_id, blocking=False)
        
        # Then run until interrupted
        try:
            logger.info("Running. Press Ctrl+C to stop.")
            while not self.stop_polling and self.polling_thread.is_alive():
                time.sleep(0.1)  # Small sleep to prevent high CPU usage
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping...")
            self.stop()
        
    def run_forever(self) -> None:
        """
        Convenience method to keep the application running until interrupted by user.
        Only call this after _start() has been called.
        """
        if not self.polling_thread or not self.polling_thread.is_alive():
            raise RuntimeError("No active polling thread. Call _start() first.")
            
        try:
            logger.info("Running forever. Press Ctrl+C to stop.")
            while not self.stop_polling and self.polling_thread.is_alive():
                time.sleep(0.1)  # Small sleep to prevent high CPU usage
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping...")
            self.stop()
        
    def stop(self) -> None:
        """
        Stop listening for new messages
        """
        if self.polling_thread and self.polling_thread.is_alive():
            self.stop_polling = True
            self.polling_thread.join(timeout=2.0)
            logger.info("Stopped listening for messages")
        else:
            logger.warning("No active polling thread to stop")
                
    def send_message(self, content: str, session_id: str = None, media_type: str = "none", media_url: str = None, meta_data: Dict = None) -> Dict:
        """
        Send a message in response to a user message

        Args:
            content (str): Message content
            session_id (str, optional): Session ID. If not provided, uses the current session ID.
            media_type (str, optional): Media type, one of "none", "image", "video", "audio", "file". Defaults to "none".
            media_url (str, optional): Media URL, required if media_type is not "none". Defaults to None.
            meta_data (Dict, optional): Additional metadata. Defaults to None.

        Returns:
            Dict: Send response
            
        Raises:
            ValidationError: When content is empty or media configuration is invalid
            AuthenticationError: When API Key is invalid (401)
            ResourceNotFoundError: When session or persona doesn't exist (404)
            ServerError: When server returns 5xx errors
            NetworkError: When network connection issues occur
        """
        if not self._agent_info or "id" not in self._agent_info:
            raise ValidationError("No registered agent found. Call register_agent() first or provide agent_id.")
        
        if not content or not isinstance(content, str):
            raise ValidationError("Message content is required and must be a string")
            
        if media_type != "none" and not media_url:
            raise ValidationError(f"Media URL is required when media_type is '{media_type}'")
            
        valid_media_types = ["none", "image", "video", "audio", "file"]
        if media_type not in valid_media_types:
            raise ValidationError(f"Invalid media_type '{media_type}'. Must be one of: {', '.join(valid_media_types)}")
        
        # Use provided session ID or current session ID
        if session_id is None:
            # If no session ID is available, raise error
            if not self._session_id:
                raise ValidationError("No session ID available. Either provide session_id or make sure a session is active.")
            else:
                session_id = self._session_id
        else:
            logger.info(f"Using provided session ID: {session_id}")
            
        # Get persona information, use cache if available
        try:
            if session_id in self._personas_cache:
                persona_info = self._personas_cache[session_id]
            else:
                try:
                    persona_info = self.get_persona(session_id)
                    self._personas_cache[session_id] = persona_info
                except ResourceNotFoundError:
                    logger.error(f"Persona not found for session {session_id}")
                    raise ValidationError(f"Could not find persona for session {session_id}. The session may have expired or does not exist.")
                except Exception as e:
                    logger.error(f"Error getting persona info: {e}")
                    raise ValidationError(f"Could not get persona info for session {session_id}: {str(e)}")
            
            persona_id = persona_info.get("id")
            
            if not persona_id:
                raise ValidationError(f"Could not determine persona ID for session {session_id}")
                
            data = {
                "agent_id": self._agent_info["id"],
                "persona_id": persona_id,
                "content": content,
                "media_type": media_type,
                "media_url": media_url,
                "meta_data": meta_data or {}
            }
            
            max_retries = 2
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    response = self._make_request("POST", f"api/sdk/reply_message?session_id={session_id}", data=data)
                    logger.info(f"Message sent: {content[:50]}...")
                    return response
                except ServerError as e:
                    # Only retry on server errors (5xx)
                    retry_count += 1
                    if retry_count <= max_retries:
                        wait_time = retry_count * 2  # Simple backoff strategy
                        logger.warning(f"Server error when sending message, retrying in {wait_time}s... ({retry_count}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Failed to send message after {max_retries} retries")
                        raise
                except Exception:
                    # Don't retry on other errors
                    raise
                    
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error sending message: {e}")
            raise
    
    def get_persona(self, session_id: str = None) -> Dict:
        """
        Get persona information by session ID

        Args:
            session_id (str, optional): Session ID. If not provided, uses the current session ID.

        Returns:
            Dict: Persona information
            
        Raises:
            ValidationError: When session_id is missing
            ResourceNotFoundError: When persona doesn't exist for the session (404)
            AuthenticationError: When API Key is invalid (401)
            ServerError: When server returns 5xx errors
            NetworkError: When network connection issues occur
        """
        # Use provided session ID or current session ID
        if session_id is None:
            if not self._session_id:
                raise ValidationError("No session ID available. Either provide session_id or make sure a session is active.")
            session_id = self._session_id
            
        # Use cache if available
        if session_id in self._personas_cache:
            return self._personas_cache[session_id]
            
        try:
            response = self._make_request("GET", f"api/sdk/get_persona_by_session?session_id={session_id}")
            logger.info(f"Retrieved persona for session {session_id}")
            
            # Cache result
            self._personas_cache[session_id] = response
            
            return response
        except ResourceNotFoundError:
            logger.error(f"Persona not found for session {session_id}")
            # Remove from cache if it exists
            if session_id in self._personas_cache:
                del self._personas_cache[session_id]
            raise
    
    def upload_media(self, file_path: str, media_type: str) -> Dict:
        """
        Upload a media file

        Args:
            file_path (str): Path to the file to upload
            media_type (str): Media type, one of "image", "video", "audio", "file"

        Returns:
            Dict: Upload response with media URL
            
        Raises:
            ValidationError: When file_path is invalid or media_type is unsupported
            FileNotFoundError: When file doesn't exist
            AuthenticationError: When API Key is invalid (401)
            ServerError: When server returns 5xx errors
            NetworkError: When network connection issues occur
        """
        valid_media_types = ["image", "video", "audio", "file"]
        if media_type not in valid_media_types:
            raise ValidationError(f"Invalid media_type '{media_type}'. Must be one of: {', '.join(valid_media_types)}")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Media size limits based on documentation
        size_limits = {
            "image": 10 * 1024 * 1024,  # 10MB
            "video": 100 * 1024 * 1024,  # 100MB
            "audio": 50 * 1024 * 1024,   # 50MB
            "file": 20 * 1024 * 1024     # 20MB
        }
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > size_limits[media_type]:
            max_size_mb = size_limits[media_type] / (1024 * 1024)
            raise ValidationError(f"File is too large. Maximum size for {media_type} is {max_size_mb} MB, but file is {file_size / (1024 * 1024):.2f} MB")
            
        # Validate file extension based on media type
        file_ext = os.path.splitext(file_path)[1].lower()
        valid_extensions = {
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
            "video": [".mp4", ".webm", ".mov"],
            "audio": [".mp3", ".wav", ".ogg"],
            "file": [".pdf", ".txt", ".zip", ".docx"]
        }
        
        if file_ext not in valid_extensions[media_type]:
            raise ValidationError(f"Invalid file extension for {media_type}: {file_ext}. Supported extensions: {', '.join(valid_extensions[media_type])}")
        
        # MIME类型映射
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".mov": "video/quicktime",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".zip": "application/zip",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
            
        try:
            filename = os.path.basename(file_path)
            mime_type = mime_types.get(file_ext, "application/octet-stream")
            
            with open(file_path, 'rb') as f:
                # 按照curl命令的格式设置文件上传参数
                files = {
                    'file': (filename, f, mime_type)
                }
                data = {'media_type': media_type}
                
                response = self._make_request(
                    "POST",
                    "api/sdk/upload_media",
                    data=data,
                    files=files
                )
                
            logger.info(f"Media uploaded: {filename} as {media_type}")
            return response
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            raise
    
    def get_valid_categories(self) -> List[str]:
        """
        Get the list of valid agent categories
        
        Returns:
            List[str]: List of valid agent categories
        """
        return list(CATEGORY_DISPLAY_NAMES.keys())
        
    def get_category_display_name(self, category: str) -> str:
        """
        Get the display name for a category
        
        Args:
            category (str): Category code (one of the AGENT_CATEGORY_* constants)
            
        Returns:
            str: Display name for the category
            
        Raises:
            ValidationError: When category is invalid
        """
        if category not in CATEGORY_DISPLAY_NAMES:
            categories_str = ", ".join([f"{k} ({v})" for k, v in CATEGORY_DISPLAY_NAMES.items()])
            raise ValidationError(f"Invalid category. Must be one of: {categories_str}")
            
        return CATEGORY_DISPLAY_NAMES[category]
    
    def __del__(self):
        """
        Destructor to ensure polling is stopped when object is destroyed
        """
        self.stop()
