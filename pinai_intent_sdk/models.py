from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Union
from enum import Enum
from datetime import datetime

class AgentCategory(str, Enum):
    TRANSPORT = "TRANSPORT"
    FOOD_DELIVERY = "FOOD_DELIVERY"
    # 可以继续扩展其他类别

class CostLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    DEFAULT = "default"

class BaseIntentRequest(BaseModel):
    category: AgentCategory
    user_id: str
    preferences: Dict[str, float] = {
        "price": 0.5,
        "rating": 0.3,
        "response_time": 0.2
    }
    location: Optional[Dict[str, float]] = None

class TransportIntentRequest(BaseIntentRequest):
    category: Literal[AgentCategory.TRANSPORT]
    origin: str = "current"
    destination: str
    pickup_time: str = "99:99"  # 默认现在
    app_preference: str = "default"
    cost_level: CostLevel = CostLevel.DEFAULT

class FoodDeliveryIntentRequest(BaseIntentRequest):
    category: Literal[AgentCategory.FOOD_DELIVERY]
    restaurant: str = "any"
    app_preference: str = "default"
    food_type: str = "any"
    delivery_location: str = "current"
    cost_level: CostLevel = CostLevel.DEFAULT

# 用于API的联合类型
IntentRequest = Union[TransportIntentRequest, FoodDeliveryIntentRequest]

class Agent(BaseModel):
    id: str = Field(description="代理的唯一标识符")
    name: str = Field(description="代理名称")
    category: AgentCategory = Field(description="代理类别，如运输、外卖等")
    description: str = Field(description="代理的详细描述")
    api_endpoint: str = Field(description="代理服务的API接入点")
    capabilities: List[str] = Field(description="代理能力列表，描述其可以执行的任务")
    pricing_model: Dict[str, float] = Field(description="价格模型，key为服务类型，value为对应价格")
    average_rating: float = Field(
        default=5.0, 
        ge=0.0, 
        le=5.0, 
        description="平均评分，范围0-5"
    )
    response_time: float = Field(description="平均响应时间，单位为秒")
    availability: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0, 
        description="可用性百分比，范围0-1"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="代理创建时间"
    )
    metadata: Dict[str, str] = Field(
        default={},
        description="额外的元数据信息，用于存储自定义属性"
    )

class MatchResponse(BaseModel):
    agent_id: str
    agent_name: str
    score: float
    category: AgentCategory
    api_endpoint: str 