# PINAI Intent SDK

PINAI Intent SDK 是一个用于与 PINAI Intent Match API 交互的 Python 客户端库。

## 安装

```bash
pip install pinai-intent-sdk
```

## 快速开始

```python
from pinai_intent_sdk import PINAIIntentSDK

# 初始化 SDK
sdk = PINAIIntentSDK(base_url="https://api.pinai.io", api_key="your-api-key")

# 注册新的 agent
agent = sdk.register_agent(
    name="My Agent",
    category="general",
    description="A general purpose agent",
    api_endpoint="https://my-agent-endpoint.com",
    capabilities=["text", "image"],
    pricing_model={"per_request": 0.001},
    response_time=1.0
)
```

## 功能特性

- Agent 注册与管理
- Agent 性能指标监控
- 支持多种过滤条件的 Agent 查询

## 文档

详细文档请访问 [https://docs.pinai.io](https://docs.pinai.io)
```
