from datetime import datetime
import requests
from typing import Dict, Optional, List
from urllib.parse import urljoin
from .models import AgentCategory
from .exceptions import IntentMatchError

class PINAIIntentSDK:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化 SDK
        :param base_url: API 基础 URL
        :param api_key: API 认证密钥
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
            
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """内部请求处理方法"""
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise IntentMatchError(f"API request failed: {str(e)}")

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
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict:
        """注册新的 agent"""
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