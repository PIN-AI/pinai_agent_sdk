"""
PINAI Agent SDK
"""

from .pinai_agent_sdk import (
    PINAIAgentSDK, 
    PINAIAgentSDKError,
    ValidationError,
    AuthenticationError,
    PermissionError,
    ResourceNotFoundError,
    ResourceConflictError,
    ServerError,
    NetworkError
)

from .constants import (
    AGENT_CATEGORY_SOCIAL,
    AGENT_CATEGORY_DAILY,
    AGENT_CATEGORY_PRODUCTIVITY,
    AGENT_CATEGORY_WEB3,
    AGENT_CATEGORY_SHOPPING,
    AGENT_CATEGORY_FINANCE,
    AGENT_CATEGORY_AI_CHAT,
    AGENT_CATEGORY_OTHER
)

__version__ = "0.1.11"
__all__ = [
    "PINAIAgentSDK",
    "PINAIAgentSDKError",
    "ValidationError",
    "AuthenticationError", 
    "PermissionError",
    "ResourceNotFoundError",
    "ResourceConflictError",
    "ServerError",
    "NetworkError",
    "AGENT_CATEGORY_SOCIAL",
    "AGENT_CATEGORY_DAILY",
    "AGENT_CATEGORY_PRODUCTIVITY",
    "AGENT_CATEGORY_WEB3",
    "AGENT_CATEGORY_SHOPPING",
    "AGENT_CATEGORY_FINANCE",
    "AGENT_CATEGORY_AI_CHAT",
    "AGENT_CATEGORY_OTHER"
]