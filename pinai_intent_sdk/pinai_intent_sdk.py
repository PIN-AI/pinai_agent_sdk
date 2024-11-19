from datetime import datetime
import requests
from typing import Dict, Optional, List, Union, Any
from urllib.parse import urljoin
from .models import AgentCategory
from .exceptions import IntentMatchError, ValidationError

class PINAIIntentSDK:
    """
    PINAI Intent SDK for managing AI agents.
    
    This SDK provides interfaces to register, manage and monitor AI agents.
    
    Args:
        base_url (str): The base URL for the PINAI Intent API
        api_key (Optional[str]): API authentication key
        timeout (int): Request timeout in seconds (default: 30)
    
    Raises:
        ValueError: If base_url is invalid
    """
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
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
        metadata: Optional[Dict[str, Any]] = None
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