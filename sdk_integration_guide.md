# PIN Agent SDK 集成指南

本文档提供了如何集成和使用PIN Agent SDK API的详细说明。

## 目录

- [概述](#概述)
- [认证](#认证)
- [API端点](#api端点)
  - [注册Agent](#注册agent)
  - [轮询消息](#轮询消息)
  - [回复消息](#回复消息)
  - [获取人设信息](#获取人设信息)
  - [上传媒体文件](#上传媒体文件)
- [错误处理](#错误处理)
- [示例代码](#示例代码)

## 概述

PIN Agent SDK API允许开发者创建和管理自定义Agent，以及处理与用户的消息交互。API采用RESTful风格，所有数据都使用JSON格式。

## 认证

所有SDK API请求都需要通过API Key进行认证。API Key可以从用户控制台获取。

### 获取API Key

用户可以通过以下方式获取API Key：

1. 登录PIN Agent Platform
2. 访问"个人设置"页面
3. 在"API Keys"部分查看或复制API Key

每个用户账户自动生成一个唯一的API Key，与用户ID关联。

### 使用API Key

在所有API请求中，将API Key包含在`X-API-Key`头部中：

```
X-API-Key: pin_YOUR_API_KEY
```

## API端点

所有API端点都以`/api/sdk/`为前缀。

### 注册Agent

创建一个新的Agent。

**请求**

```
POST /api/sdk/register_agent
```

**请求头部**

```
X-API-Key: pin_YOUR_API_KEY
Content-Type: application/json
```

**请求参数**

```json
{
  "name": "Agent名称",
  "ticker": "TKRR",
  "cover": "https://example.com/cover.jpg",
  "description": "Agent描述"
}
```

| 参数 | 类型 | 描述 |
|------|------|------|
| name | string | Agent的名称（必须唯一） |
| ticker | string | Agent的股票代码（通常4个大写字母） |
| cover | string | Agent封面图片的URL |
| description | string | Agent的详细描述 |

**响应**

```json
{
  "id": 1,
  "name": "Agent名称",
  "ticker": "TKRR",
  "cover": "https://example.com/cover.jpg",
  "url": "https://placeholder.com",
  "description": "Agent描述",
  "created_at": "2025-03-04T16:50:18",
  "updated_at": "2025-03-04T16:50:18"
}
```

**可能的错误**

- `409 Conflict`: Agent名称已存在
- `401 Unauthorized`: 无效的API Key
- `500 Internal Server Error`: 服务器内部错误

### 轮询消息

获取发送给指定Agent的新消息。

**请求**

```
POST /api/sdk/poll_messages
```

**请求头部**

```
X-API-Key: pin_YOUR_API_KEY
Content-Type: application/json
```

**请求参数**

```json
{
  "agent_id": 1,
  "since_timestamp": "2025-03-01T00:00:00"
}
```

| 参数 | 类型 | 描述 |
|------|------|------|
| agent_id | number | 要轮询的Agent ID |
| since_timestamp | string | 获取此时间戳之后的消息（ISO 8601格式） |

**响应**

```json
[
  {
    "id": 123,
    "session_id": "session_12345",
    "message_type": "user",
    "content": "你好，我想了解更多关于你的信息",
    "meta_data": {},
    "created_at": "2025-03-04T16:30:00"
  },
  {
    "id": 124,
    "session_id": "session_12345",
    "message_type": "user",
    "content": "你能给我介绍一下你的功能吗？",
    "meta_data": {},
    "created_at": "2025-03-04T16:31:00"
  }
]
```

**可能的错误**

- `401 Unauthorized`: 无效的API Key
- `403 Forbidden`: 没有权限访问此Agent
- `500 Internal Server Error`: 服务器内部错误

### 回复消息

回复用户的消息，支持文本和媒体消息。

**请求**

```
POST /api/sdk/reply_message?session_id=session_12345
```

**请求头部**

```
X-API-Key: pin_YOUR_API_KEY
Content-Type: application/json
```

**请求参数**

```json
{
  "agent_id": 1,
  "persona_id": 2,
  "content": "你好！我是一个助手Agent，很高兴为你服务。",
  "media_type": "none",
  "media_url": null,
  "meta_data": {}
}
```

| 参数 | 类型 | 描述 |
|------|------|------|
| agent_id | number | Agent的ID |
| persona_id | number | 用户使用的人设ID |
| content | string | 消息内容 |
| media_type | string | 媒体类型，可以是 "none", "image", "video", "audio" 或 "file" |
| media_url | string | 媒体文件的URL，通过上传媒体文件API获取 |
| meta_data | object | 附加元数据（可选） |

**URL参数**

| 参数 | 类型 | 描述 |
|------|------|------|
| session_id | string | 会话ID，从用户消息的session_id字段获取 |

**响应**

```json
{
  "id": 125,
  "session_id": "session_12345",
  "message_type": "agent",
  "content": "你好！我是一个助手Agent，很高兴为你服务。",
  "media_type": "none",
  "media_url": null,
  "meta_data": {},
  "created_at": "2025-03-04T16:32:00"
}
```

**可能的错误**

- `401 Unauthorized`: 无效的API Key
- `403 Forbidden`: 没有权限访问此Agent
- `400 Bad Request`: 无效的session_id
- `500 Internal Server Error`: 服务器内部错误

### 获取人设信息

获取与会话关联的用户人设信息。

**请求**

```
GET /api/sdk/get_persona_by_session?session_id=session_12345
```

**请求头部**

```
X-API-Key: pin_YOUR_API_KEY
```

**URL参数**

| 参数 | 类型 | 描述 |
|------|------|------|
| session_id | string | 会话ID，从用户消息的session_id字段获取 |

**响应**

```json
{
  "id": 1,
  "name": "Custom Alice",
  "description": "My customized version of Alice",
  "is_system": true,
  "data": {
    "emails": [
      {
        "id": "email1",
        "to": "alice@example.com",
        "body": "Alice, we have a gathering this weekend...",
        "date": "2025-03-01T10:30:00Z",
        "from": "bob@example.com",
        "subject": "Weekend Gathering"
      }
    ],
    "calendar": [
      {
        "id": "event1",
        "end": "2025-03-05T15:30:00Z",
        "start": "2025-03-05T14:00:00Z",
        "title": "Team Meeting",
        "location": "Meeting Room A",
        "description": "Discuss quarterly goals and progress"
      }
    ],
    "interests": ["hiking", "photography"],
    "preferred_style": "casual"
  },
  "created_at": "2025-03-04T16:26:16"
}
```

**可能的错误**

- `401 Unauthorized`: 无效的API Key
- `400 Bad Request`: 无效的session_id
- `404 Not Found`: 人设未找到
- `500 Internal Server Error`: 服务器内部错误

### 上传媒体文件

上传图片、视频、音频或文件。

**请求**

```
POST /api/sdk/upload_media
```

**请求头部**

```
X-API-Key: pin_YOUR_API_KEY
```

**表单数据**

- `file`: 要上传的文件（multipart/form-data）
- `media_type`: 媒体类型，可以是 "image", "video", "audio" 或 "file"

**响应**

```json
{
  "media_url": "https://pin-agent-media.s3.us-east-1.amazonaws.com/media/image/12400000/550e8400-e29b-41d4-a716-446655440000.jpg",
  "media_type": "image"
}
```

**支持的媒体类型和限制**

| 媒体类型 | 支持的格式 | 大小限制 |
|---------|------------|---------|
| image | JPEG, PNG, GIF, WebP | 10MB |
| video | MP4, WebM, QuickTime | 100MB |
| audio | MP3, WAV, OGG | 50MB |
| file | PDF, TXT, ZIP, DOCX | 20MB |

**可能的错误**

- `400 Bad Request`: 无效的媒体类型或文件格式
- `401 Unauthorized`: 无效的API Key
- `500 Internal Server Error`: 文件上传失败

## 错误处理

API使用标准HTTP状态码表示请求的成功或失败。错误响应包含一个JSON对象，其中包含错误详细信息。

例如：

```json
{
  "detail": "Agent with name 'New Test Agent' already exists. Please choose a different name."
}
```

常见错误状态码：

- `400 Bad Request`: 请求参数无效
- `401 Unauthorized`: 认证失败，API Key无效
- `403 Forbidden`: 无权限执行请求的操作
- `404 Not Found`: 请求的资源不存在
- `409 Conflict`: 资源冲突（例如：Agent名称已存在）
- `500 Internal Server Error`: 服务器内部错误

## 示例代码

### Python

```python
import requests
import json

API_KEY = "pin_YOUR_API_KEY"
BASE_URL = "http://api.pinagent.com/api/sdk"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 注册新Agent
def register_agent():
    data = {
        "name": "My SDK Agent",
        "ticker": "MSDK",
        "cover": "https://example.com/cover.jpg",
        "description": "An agent created using the SDK API"
    }
    
    response = requests.post(
        f"{BASE_URL}/register_agent",
        headers=headers,
        data=json.dumps(data)
    )
    
    return response.json()

# 轮询消息
def poll_messages(agent_id, since_timestamp):
    data = {
        "agent_id": agent_id,
        "since_timestamp": since_timestamp
    }
    
    response = requests.post(
        f"{BASE_URL}/poll_messages",
        headers=headers,
        data=json.dumps(data)
    )
    
    return response.json()

# 回复消息 (支持媒体)
def reply_message(session_id, agent_id, persona_id, content, media_type="none", media_url=None):
    data = {
        "agent_id": agent_id,
        "persona_id": persona_id,
        "content": content,
        "media_type": media_type,
        "media_url": media_url,
        "meta_data": {}
    }
    
    response = requests.post(
        f"{BASE_URL}/reply_message?session_id={session_id}",
        headers=headers,
        data=json.dumps(data)
    )
    
    return response.json()

# 获取人设信息
def get_persona(session_id):
    response = requests.get(
        f"{BASE_URL}/get_persona_by_session?session_id={session_id}",
        headers=headers
    )
    
    return response.json()

# 上传媒体文件
def upload_media(file_path, media_type):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'media_type': media_type}
        
        response = requests.post(
            f"{BASE_URL}/upload_media",
            headers={"X-API-Key": API_KEY},  # 不包含Content-Type
            files=files,
            data=data
        )
        
        return response.json()

# 示例: 发送带图片的消息
def send_image_message(session_id, agent_id, persona_id):
    # 1. 上传图片
    media_result = upload_media("path/to/image.jpg", "image")
    
    # 2. 发送带图片的消息
    return reply_message(
        session_id=session_id,
        agent_id=agent_id,
        persona_id=persona_id,
        content="看看这张图片!",
        media_type=media_result["media_type"],
        media_url=media_result["media_url"]
    )
```

### Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_KEY = 'pin_YOUR_API_KEY';
const BASE_URL = 'http://api.pinagent.com/api/sdk';

const headers = {
  'X-API-Key': API_KEY,
  'Content-Type': 'application/json'
};

// 注册新Agent
async function registerAgent() {
  const data = {
    name: 'My SDK Agent',
    ticker: 'MSDK',
    cover: 'https://example.com/cover.jpg',
    description: 'An agent created using the SDK API'
  };
  
  try {
    const response = await axios.post(`${BASE_URL}/register_agent`, data, { headers });
    return response.data;
  } catch (error) {
    console.error('Error registering agent:', error.response?.data || error.message);
    throw error;
  }
}

// 轮询消息
async function pollMessages(agentId, sinceTimestamp) {
  const data = {
    agent_id: agentId,
    since_timestamp: sinceTimestamp
  };
  
  try {
    const response = await axios.post(`${BASE_URL}/poll_messages`, data, { headers });
    return response.data;
  } catch (error) {
    console.error('Error polling messages:', error.response?.data || error.message);
    throw error;
  }
}

// 回复消息 (支持媒体)
async function replyMessage(sessionId, agentId, personaId, content, mediaType = "none", mediaUrl = null) {
  const data = {
    agent_id: agentId,
    persona_id: personaId,
    content: content,
    media_type: mediaType,
    media_url: mediaUrl,
    meta_data: {}
  };
  
  try {
    const response = await axios.post(
      `${BASE_URL}/reply_message?session_id=${sessionId}`,
      data,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error replying to message:', error.response?.data || error.message);
    throw error;
  }
}

// 获取人设信息
async function getPersona(sessionId) {
  try {
    const response = await axios.get(
      `${BASE_URL}/get_persona_by_session?session_id=${sessionId}`,
      { headers }
    );
    return response.data;
  } catch (error) {
    console.error('Error getting persona:', error.response?.data || error.message);
    throw error;
  }
}

// 上传媒体文件
async function uploadMedia(filePath, mediaType) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('media_type', mediaType);
  
  try {
    const response = await axios.post(
      `${BASE_URL}/upload_media`,
      form,
      { 
        headers: {
          'X-API-Key': API_KEY,
          ...form.getHeaders()
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error uploading media:', error.response?.data || error.message);
    throw error;
  }
}

// 示例: 发送带图片的消息
async function sendImageMessage(sessionId, agentId, personaId) {
  try {
    // 1. 上传图片
    const mediaResult = await uploadMedia('path/to/image.jpg', 'image');
    
    // 2. 发送带图片的消息
    return await replyMessage(
      sessionId,
      agentId,
      personaId,
      '看看这张图片!',
      mediaResult.media_type,
      mediaResult.media_url
    );
  } catch (error) {
    console.error('Error sending image message:', error);
    throw error;
  }
}
