from datetime import datetime
import json
import requests
from typing import Dict, Optional, List, Union, Any
from urllib.parse import urljoin
from web3 import Web3
from eth_account import Account
from .models import AgentCategory
from .exceptions import IntentMatchError, ValidationError

# Contract configuration
CONTRACT_ADDRESS = "0x7D1C1255DF6BE34d1658e4EB1cB6962c06d451c5"
DEFAULT_RPC = "https://sepolia.base.org"
MIN_STAKE = 0
REGISTRATION_FEE = 0

class PINAIIntentSDK:
    """
    PINAI Intent SDK for managing AI agents.
    
    This SDK provides interfaces to register, manage and monitor AI agents.
    
    Args:
        base_url (str): The base URL for the PINAI Intent API
        api_key (Optional[str]): API authentication key
        timeout (int): Request timeout in seconds (default: 30)
        privatekey (Optional[str]): Private key for blockchain interaction
        blockchainRPC (Optional[str]): RPC endpoint for blockchain (default: sepolia.base)
    
    Raises:
        ValueError: If base_url is invalid
    """
    def __init__(
        self, 
        base_url: str, 
        api_key: Optional[str] = None, 
        timeout: int = 30,
        privatekey: Optional[str] = None,
        blockchainRPC: Optional[str] = None
    ):
        if not base_url:
            raise ValueError("base_url cannot be empty")
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
            
        # Initialize blockchain components if privatekey is provided
        self.web3 = None
        self.contract = None
        self.account = None
        
        if privatekey:
            # Initialize Web3
            rpc_url = blockchainRPC or DEFAULT_RPC
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Initialize account
            self.account = Account.from_key(privatekey)
            
            # Load contract ABI and create contract instance
            with open('pinai_intent_sdk/AgentManage.abi.json') as f:
                contract_abi = json.load(f)['abi']
            
            self.contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                abi=contract_abi
            )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Union[Dict, List]:
        """Internal method to handle API requests with error handling"""
        url = urljoin(self.base_url, endpoint)
        kwargs.setdefault('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise IntentMatchError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise IntentMatchError("Connection failed")
        except requests.exceptions.RequestException as e:
            raise IntentMatchError(f"API request failed: {str(e)}")
        except ValueError:
            raise IntentMatchError("Invalid JSON response from server")

    def register_agent(
        self,
        name: str,
        category: AgentCategory,
        description: str,
        api_endpoint: str,
        capabilities: List[str],
        pricing_model: Dict[str, float],
        response_time: float,
        availability: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        agent_owner: Optional[str] = None
    ) -> Dict:
        """
        Register a new agent in the system.
        
        Args:
            name (str): Agent name
            category (AgentCategory): Agent category enum
            description (str): Detailed description of agent capabilities
            api_endpoint (str): Agent API endpoint URL
            capabilities (List[str]): List of agent capabilities
            pricing_model (Dict[str, float]): Pricing details
            response_time (float): Expected response time in seconds
            availability (float): Agent availability percentage (0.0-1.0)
            metadata (Optional[Dict]): Additional agent metadata
            agent_owner (Optional[str]): Ethereum address of the agent owner
            
        Returns:
            Dict: Registered agent details
            
        Raises:
            ValidationError: If input parameters are invalid
            IntentMatchError: If API request fails
        """
        # Validate inputs
        if not name or not description or not api_endpoint:
            raise ValidationError("name, description and api_endpoint are required")
        if not isinstance(capabilities, list) or not capabilities:
            raise ValidationError("capabilities must be a non-empty list")
        if not isinstance(pricing_model, dict) or not pricing_model:
            raise ValidationError("pricing_model must be a non-empty dictionary")
        if not 0.0 <= availability <= 1.0:
            raise ValidationError("availability must be between 0.0 and 1.0")
        if response_time <= 0:
            raise ValidationError("response_time must be positive")

        # If blockchain interaction is enabled (privatekey provided)
        if self.web3 and self.contract and self.account:
            try:
                # Get valid component ID
                # For sdk, we assume component ID 1 exists
                # In production, this should be retrieved from ComponentRegistry
                component_id = 1
                dependencies = [component_id]
                dependencies_uint32 = [self.web3.to_int(x) for x in dependencies]
                
                nonce = self.web3.eth.get_transaction_count(self.account.address)
                
                # Build contract transaction
                # Note: Contract expects MIN_STAKE + REGISTRATION_FEE to be sent with the transaction
                min_stake = self.web3.to_wei(MIN_STAKE, 'ether')
                registration_fee = self.web3.to_wei(REGISTRATION_FEE, 'ether')
                total_value = min_stake + registration_fee
                
                # Add gas limit to avoid gas estimation issues
                gas_limit = 500000  # Set a reasonable gas limit
                
                # Use provided agent_owner or default to account address
                owner_address = agent_owner if agent_owner else self.account.address
                # Convert to checksum address
                owner_address = Web3.to_checksum_address(owner_address)
                
                contract_txn = self.contract.functions.create(
                    owner_address,
                    name,
                    api_endpoint,
                    dependencies_uint32
                ).build_transaction({
                    'from': self.account.address,
                    'nonce': nonce,
                    'value': total_value,  # Send required stake + fee
                    'gas': gas_limit,
                    'type': '0x2',  # EIP-1559
                    'maxFeePerGas': self.web3.eth.max_priority_fee + (2 * self.web3.eth.get_block('latest')['baseFeePerGas']),
                    'maxPriorityFeePerGas': self.web3.eth.max_priority_fee,
                })

                # Sign transaction
                signed_txn = self.account.sign_transaction(contract_txn)
                
                # Send transaction
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
                # Wait for 1 block confirmation
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(
                    tx_hash, 
                    timeout=30,  # 30 seconds timeout
                    poll_latency=1  # Check every 1 seconds
                )
                
                if tx_receipt['status'] != 1:
                    raise IntentMatchError("Blockchain transaction failed")
                    
            except Exception as e:
                raise IntentMatchError(f"Blockchain interaction failed: {str(e)}")

        # Prepare data for HTTP API
        agent_data = {
            "id": f"{category}_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": category,
            "description": description,
            "api_endpoint": api_endpoint,
            "capabilities": capabilities,
            "pricing_model": pricing_model,
            "response_time": response_time,
            "availability": availability,
            "metadata": metadata or {}
        }
        
        return self._make_request("POST", "/register_agent", json=agent_data)

    def unregister_agent(self, agent_id: str) -> Dict:
        """注销指定的 agent"""
        return self._make_request("DELETE", f"/agents/{agent_id}")

    def get_agent(self, agent_id: str) -> Dict:
        """获取单个 agent 信息"""
        return self._make_request("GET", f"/agents/{agent_id}")

    def list_agents(self, 
                   category: Optional[AgentCategory] = None,
                   capability: Optional[str] = None) -> List[Dict]:
        """获取 agent 列表，支持过滤"""
        params = {}
        if category:
            params['category'] = category
        if capability:
            params['capability'] = capability
        return self._make_request("GET", "/agents", params=params)

    def update_agent(self, agent_id: str, **updates) -> Dict:
        """更新 agent 信息"""
        return self._make_request("PATCH", f"/agents/{agent_id}", json=updates)

    def get_agent_metrics(self, agent_id: str, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict:
        """获取 agent 的性能指标"""
        params = {}
        if start_time:
            params['start_time'] = start_time.isoformat()
        if end_time:
            params['end_time'] = end_time.isoformat()
        return self._make_request("GET", f"/agents/{agent_id}/metrics", params=params)