"""
PINAIAgentSDK - Python SDK for PINAI Agent API
"""

import time
import threading
import logging
import requests
import json
from typing import Dict, List, Any, Optional, Callable, Union
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PINAIAgentSDK")

class PINAIAgentSDK:
    """
    SDK for PINAI Agent API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://dev-web.pinai.tech/", timeout: int = 30, polling_interval: float = 1.0):
        """
        Initialize PINAIAgentSDK

        Args:
            api_key (str): PINAI API Key
            base_url (str, optional): Base URL for API. Defaults to "https://dev-web.pinai.tech/".
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            polling_interval (float, optional): Interval in seconds between message polls. Defaults to 1.0.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.polling_interval = polling_interval
        self.session_id = None
        self.polling_thread = None
        self.stop_polling = False
        self.message_callback = None
        self._agent_info = None
        
        # Check if base_url ends with a slash, add it if not
        if not self.base_url.endswith('/'):
            self.base_url += '/'
            
        logger.info(f"PINAIAgentSDK initialized with base URL: {base_url}")
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """
        Send HTTP request

        Args:
            method (str): HTTP method (GET, POST, DELETE, etc.)
            endpoint (str): API endpoint
            data (Dict, optional): Request data. Defaults to None.
            headers (Dict, optional): Request headers. Defaults to None.

        Returns:
            Dict: API response
        """
        url = urljoin(self.base_url, endpoint)
        
        # Prepare headers
        default_headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        # Add session ID to headers if available
        if self.session_id:
            default_headers["X-Session-ID"] = self.session_id
            
        # Merge custom headers
        if headers:
            default_headers.update(headers)
            
        try:
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
            
    def register_agent(self, name: str, category: str, description: str, logo: str = None, metadata: Dict = None) -> Dict:
        """
        Register a new agent

        Args:
            name (str): Agent name
            category (str): Agent category
            description (str): Agent description
            logo (str, optional): Agent logo URL. Defaults to None.
            metadata (Dict, optional): Additional metadata. Defaults to None.

        Returns:
            Dict: Registration response
        """
        data = {
            "name": name,
            "category": category,
            "description": description,
        }
        
        if logo:
            data["logo"] = logo
            
        if metadata:
            data["metadata"] = metadata
            
        response = self._make_request("POST", "api/agents/register", data=data)
        
        # Save agent info for later use
        self._agent_info = {
            "name": name,
            "category": category,
            "description": description,
            "logo": logo,
            "metadata": metadata
        }
        
        logger.info(f"Agent registered: {name}")
        return response
        
    def unregister_agent(self, name: str) -> Dict:
        """
        Unregister an agent

        Args:
            name (str): Agent name

        Returns:
            Dict: Unregistration response
        """
        data = {"name": name}
        response = self._make_request("DELETE", "api/agents/unregister", data=data)
        
        # Clear agent info
        if self._agent_info and self._agent_info.get("name") == name:
            self._agent_info = None
            
        logger.info(f"Agent unregistered: {name}")
        return response
    
    def _poll_messages(self):
        """
        Internal method for polling messages
        """
        while not self.stop_polling:
            try:
                # Get new messages
                response = self._make_request("GET", "api/messages/poll")
                
                # Process each message if there are any and callback is set
                if response.get("messages") and self.message_callback:
                    for message in response.get("messages", []):
                        # Ensure message contains required fields
                        if all(key in message for key in ["sessionId", "timestamp", "content"]):
                            self.message_callback(message)
                        else:
                            logger.warning(f"Received message with missing fields: {message}")
                
            except Exception as e:
                logger.error(f"Error polling messages: {e}")
                
            # Wait specified interval before polling again
            time.sleep(self.polling_interval)
    
    def start(self, on_message_callback: Callable[[Dict], None], blocking: bool = False) -> None:
        """
        Start listening for new messages

        Args:
            on_message_callback (Callable[[Dict], None]): Callback function for new messages
            blocking (bool, optional): If True, the method will block and not return until stop() is called.
                                       If False, polling runs in background thread. Defaults to False.
        """
        # First create a new session
        response = self._make_request("POST", "api/sessions/create")
        self.session_id = response.get("sessionId")
        
        if not self.session_id:
            raise ValueError("Failed to create session: No sessionId returned")
        
        logger.info(f"Session created: {self.session_id}")
        
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
            
        # Close session if active
        if self.session_id:
            try:
                self._make_request("DELETE", f"api/sessions/{self.session_id}")
                logger.info(f"Session closed: {self.session_id}")
            except Exception as e:
                logger.error(f"Error closing session: {e}")
            finally:
                self.session_id = None
                
    def send_message(self, content: str, image_url: str = None) -> Dict:
        """
        Send a message

        Args:
            content (str): Message content
            image_url (str, optional): Image URL. Defaults to None.

        Returns:
            Dict: Send response
        """
        if not self.session_id:
            raise ValueError("No active session. Call start() first.")
            
        data = {"content": content}
        
        if image_url:
            data["imageUrl"] = image_url
            
        response = self._make_request("POST", "api/messages/send", data=data)
        
        logger.info(f"Message sent: {content[:50]}...")
        return response
    
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
        
    def __del__(self):
        """
        Destructor to ensure polling is stopped when object is destroyed
        """
        self.stop()
