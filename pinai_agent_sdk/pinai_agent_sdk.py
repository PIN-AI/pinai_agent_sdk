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

CONTRACT_ADDRESS = "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9"
# DEFAULT_RPC = "https://sepolia.base.org"
DEFAULT_RPC = "http://127.0.0.1:8545"
MIN_STAKE = 0
REGISTRATION_FEE = 0
MAX_STRING_LENGTH = 256

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PINAIAgentSDK")

class PINAIAgentSDK:
    """
    SDK for PINAI Agent API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://emute3dbtc.us-east-1.awsapprunner.com", timeout: int = 30, polling_interval: float = 1.0, privatekey: Optional[str] = None, blockchainRPC: Optional[str] = None):
        """
        Initialize PINAIAgentSDK

        Args:
            api_key (str): PINAI API Key
            base_url (str, optional): Base URL for API. Defaults to "https://emute3dbtc.us-east-1.awsapprunner.com/users/api-keys".
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
        
        # 初始化区块链组件
        self.web3 = None
        self.contract = None
        self.account = None
        
        if privatekey:
            try:
                # 初始化 Web3
                rpc_url = blockchainRPC or DEFAULT_RPC
                self.web3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # 初始化账户
                self.account = Account.from_key(privatekey)
                
                # 加载合约 ABI 并创建合约实例
                abi_path = os.path.join(os.path.dirname(__file__), 'AgentManage.abi.json')
                with open(abi_path) as f:
                    contract_abi = json.load(f)['abi']
                
                self.contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                    abi=contract_abi
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
            
            # Check response status
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise
            
    def register_agent(self, name: str, ticker: str, description: str, cover: str = None, metadata: Dict = None, agent_owner: Optional[str] = None) -> Dict:
        """
        Register a new agent

        Args:
            name (str): Agent name
            ticker (str): Agent ticker symbol (usually 4 capital letters)
            description (str): Agent description
            cover (str, optional): Agent cover image URL. Defaults to None.
            metadata (Dict, optional): Additional metadata. Defaults to None.
            agent_owner (str, optional): Ethereum address of the agent owner. If not provided, the current account address will be used.

        Returns:
            Dict: Registration response including agent ID
        """
        data = {
            "name": name,
            "ticker": ticker,
            "description": description,
        }
        
        if cover:
            data["cover"] = cover
            
        if metadata:
            data["metadata"] = metadata
        
        # First make the HTTP request to get an agent ID
        response = self._make_request("POST", "api/sdk/register_agent", data=data)
        
        # Save agent info for later use
        self._agent_info = response
        
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
                safe_endpoint = self._truncate_string(ticker)
                
                # Get nonce
                nonce = self.web3.eth.get_transaction_count(self.account.address)
                
                # Build contract transaction
                # Note: Contract requires sending MIN_STAKE + REGISTRATION_FEE
                min_stake = self.web3.to_wei(MIN_STAKE, 'ether')
                registration_fee = self.web3.to_wei(REGISTRATION_FEE, 'ether')
                total_value = min_stake + registration_fee
                
                # Set reasonable gas limit
                gas_limit = 500000
                
                # Use provided agent_owner or default to current account address
                owner_address = agent_owner if agent_owner else self.account.address
                # Convert to checksum address
                owner_address = Web3.to_checksum_address(owner_address)
                
                # Use ticker hash as category
                category = self.web3.keccak(text=ticker)
                
                # Build contract transaction
                contract_txn = self.contract.functions.create(
                    owner_address,
                    safe_name,
                    safe_endpoint,
                    safe_description,
                    agent_id,
                    category
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
                    timeout=30,
                    poll_latency=1
                )
                
                if tx_receipt['status'] != 1:
                    logger.error("Blockchain transaction failed")
                    raise Exception("Blockchain transaction failed")
                
                logger.info(f"Agent registered on blockchain with agent_id: {agent_id}")
                
            except Exception as e:
                logger.error(f"Blockchain interaction failed: {e}")
                # Don't raise the exception here, just log it
                # We already have the agent ID from the API, so we can continue
                logger.warning("Continuing with API-only registration due to blockchain error")
        
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
        """
        # Use saved agent_id if not provided
        if agent_id is None:
            if not self._agent_info or "id" not in self._agent_info:
                raise ValueError("No agent ID provided and no registered agent found")
            agent_id = self._agent_info["id"]
        
        # First make the HTTP request to unregister the agent
        response = self._make_request("POST", f"/sdk/delete/agent/{agent_id}")
        
        # If blockchain functionality is enabled, call the smart contract
        if self.web3 and self.contract and self.account:
            try:
                # Get nonce
                nonce = self.web3.eth.get_transaction_count(self.account.address)
                
                # Set reasonable gas limit
                gas_limit = 300000
                
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
                
                # Wait for transaction confirmation
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(
                    tx_hash,
                    timeout=30,
                    poll_latency=1
                )
                
                if tx_receipt['status'] != 1:
                    logger.error("Blockchain transaction failed")
                    logger.warning("Continuing with API-only unregistration due to blockchain error")
                else:
                    logger.info(f"Agent unregistered on blockchain with agent_id: {agent_id}")
                
            except Exception as e:
                logger.error(f"Blockchain interaction failed: {e}")
                logger.warning("Continuing with API-only unregistration due to blockchain error")
        
        # Clear agent info if it matches
        if self._agent_info and self._agent_info.get("id") == agent_id:
            self._agent_info = None
        
        logger.info(f"Agent unregistered: {agent_id}")
        return response
    
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
        
        while not self.stop_polling:
            try:
                # Prepare poll request data
                data = {
                    "agent_id": agent_id,
                    "since_timestamp": self._last_poll_timestamp
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
                
            except Exception as e:
                logger.error(f"Error polling messages: {e}")
                
            # Wait specified interval before polling again
            time.sleep(self.polling_interval)
    
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
        """
        if not self._agent_info or "id" not in self._agent_info:
            raise ValueError("No registered agent found. Call register_agent() first.")
        
        # Use provided session ID or current session ID
        if session_id is None:
            # If no session ID is available, raise error
            if not self._session_id:
                raise ValueError("No session ID available. Either provide session_id or make sure a session is active.")
            else:
                session_id = self._session_id
        else:
            logger.info(f"Using provided session ID: {session_id}")
            
        # Get persona information, use cache if available
        if session_id in self._personas_cache:
            persona_info = self._personas_cache[session_id]
        else:
            try:
                persona_info = self.get_persona(session_id)
                self._personas_cache[session_id] = persona_info
            except Exception as e:
                logger.error(f"Error getting persona info: {e}")
                raise ValueError(f"Could not get persona info for session {session_id}")
        
        persona_id = persona_info.get("id")
        
        if not persona_id:
            raise ValueError(f"Could not determine persona ID for session {session_id}")
            
        data = {
            "agent_id": self._agent_info["id"],
            "persona_id": persona_id,
            "content": content,
            "media_type": media_type,
            "media_url": media_url,
            "meta_data": meta_data or {}
        }
            
        response = self._make_request("POST", f"api/sdk/reply_message?session_id={session_id}", data=data)
        
        logger.info(f"Message sent: {content[:50]}...")
        return response
    
    def get_persona(self, session_id: str = None) -> Dict:
        """
        Get persona information by session ID

        Args:
            session_id (str, optional): Session ID. If not provided, uses the current session ID.

        Returns:
            Dict: Persona information
        """
        # Use provided session ID or current session ID
        if session_id is None:
            if not self._session_id:
                raise ValueError("No session ID available. Either provide session_id or make sure a session is active.")
            session_id = self._session_id
            
        # Use cache if available
        if session_id in self._personas_cache:
            return self._personas_cache[session_id]
            
        response = self._make_request("GET", f"api/sdk/get_persona_by_session?session_id={session_id}")
        logger.info(f"Retrieved persona for session {session_id}")
        
        # Cache result
        self._personas_cache[session_id] = response
        
        return response
    
    def upload_media(self, file_path: str, media_type: str) -> Dict:
        """
        Upload a media file

        Args:
            file_path (str): Path to the file to upload
            media_type (str): Media type, one of "image", "video", "audio", "file"

        Returns:
            Dict: Upload response with media URL
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'media_type': media_type}
            
            response = self._make_request(
                "POST",
                "api/sdk/upload_media",
                data=data,
                files=files
            )
            
        logger.info(f"Media uploaded: {os.path.basename(file_path)} as {media_type}")
        return response
    
    def __del__(self):
        """
        Destructor to ensure polling is stopped when object is destroyed
        """
        self.stop()
