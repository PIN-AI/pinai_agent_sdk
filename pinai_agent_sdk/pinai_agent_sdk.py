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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PINAIAgentSDK")

class PINAIAgentSDK:
    """
    SDK for PINAI Agent API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://emute3dbtc.us-east-1.awsapprunner.com", timeout: int = 30, polling_interval: float = 1.0):
        """
        Initialize PINAIAgentSDK

        Args:
            api_key (str): PINAI API Key
            base_url (str, optional): Base URL for API. Defaults to "https://emute3dbtc.us-east-1.awsapprunner.com/users/api-keys".
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            polling_interval (float, optional): Interval in seconds between message polls. Defaults to 1.0.
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
        self._session_id = None  # 存储当前会话ID
        self._personas_cache = {}  # 缓存已获取的persona信息
        
        # Check if base_url ends with a slash, add it if not
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        logger.info(f"PINAIAgentSDK initialized with base URL: {base_url}")
        
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
            
    def register_agent(self, name: str, ticker: str, description: str, cover: str = None, metadata: Dict = None) -> Dict:
        """
        Register a new agent

        Args:
            name (str): Agent name
            ticker (str): Agent ticker symbol (usually 4 capital letters)
            description (str): Agent description
            cover (str, optional): Agent cover image URL. Defaults to None.
            metadata (Dict, optional): Additional metadata. Defaults to None.

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
            
        response = self._make_request("POST", "api/sdk/register_agent", data=data)
        
        # Save agent info for later use
        self._agent_info = response
        
        logger.info(f"Agent registered: {name} (ID: {response.get('id')})")
        return response
        
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
            
        data = {"agent_id": agent_id}
        response = self._make_request("DELETE", "api/sdk/unregister_agent", data=data)
        
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
                            
                        # 更新会话ID
                        if message.get("session_id"):
                            self._session_id = message.get("session_id")
                            
                        # Call message handler callback
                        self.message_callback(message)
                
            except Exception as e:
                logger.error(f"Error polling messages: {e}")
                
            # Wait specified interval before polling again
            time.sleep(self.polling_interval)
    
    def start(self, on_message_callback: Callable[[Dict], None], agent_id: int = None, blocking: bool = False) -> None:
        """
        Start listening for new messages

        Args:
            on_message_callback (Callable[[Dict], None]): Callback function for new messages
            agent_id (int, optional): If provided, uses this agent ID instead of registering a new one.
            blocking (bool, optional): If True, the method will block and not return until stop() is called.
                                       If False, polling runs in background thread. Defaults to False.
        """
        # 如果提供了agent_id，则直接使用而不是注册新agent
        if agent_id is not None:
            # 创建agent_info数据结构
            self._agent_info = {"id": agent_id}
            logger.info(f"Using provided agent ID: {agent_id}")
        elif not self._agent_info or "id" not in self._agent_info:
            raise ValueError("No agent ID provided and no registered agent found. Either call register_agent() first or provide agent_id.")
        
        # 生成初始会话ID
        if not self._session_id:
            self._session_id = f"session_{uuid.uuid4().hex}"
            logger.info(f"Generated new session ID: {self._session_id}")
        
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
        启动消息监听并保持运行，直到用户中断。
        这是start()和run_forever()的便捷组合方法。

        Args:
            on_message_callback (Callable[[Dict], None]): 新消息的回调函数
            agent_id (int, optional): 如果提供，使用此代理ID而不是注册新代理
        """
        # 首先启动消息监听（非阻塞模式）
        self.start(on_message_callback=on_message_callback, agent_id=agent_id, blocking=False)
        
        # 然后运行直到中断
        try:
            logger.info("运行中。按Ctrl+C停止。")
            while not self.stop_polling and self.polling_thread.is_alive():
                time.sleep(0.1)  # 小睡眠以防止高CPU使用率
        except KeyboardInterrupt:
            logger.info("收到键盘中断，正在停止...")
            self.stop()
        
    def run_forever(self) -> None:
        """
        Convenience method to keep the application running until interrupted by user.
        Only call this after start() has been called.
        """
        if not self.polling_thread or not self.polling_thread.is_alive():
            raise RuntimeError("No active polling thread. Call start() first.")
            
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
        
        # 使用提供的会话ID或当前会话ID
        if session_id is None:
            # 如果没有会话ID，则生成新的
            if not self._session_id:
                self._session_id = f"session_{uuid.uuid4().hex}"
                logger.info(f"Generated new session ID: {self._session_id}")
            session_id = self._session_id
        else:
            logger.info(f"Using provided session ID: {session_id}")
            
        # 获取persona信息，如果已缓存则使用缓存
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
        # 使用提供的会话ID或当前会话ID
        if session_id is None:
            if not self._session_id:
                raise ValueError("No session ID available. Either provide session_id or make sure a session is active.")
            session_id = self._session_id
            
        # 如果已缓存，则使用缓存
        if session_id in self._personas_cache:
            return self._personas_cache[session_id]
            
        response = self._make_request("GET", f"api/sdk/get_persona_by_session?session_id={session_id}")
        logger.info(f"Retrieved persona for session {session_id}")
        
        # 缓存结果
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
