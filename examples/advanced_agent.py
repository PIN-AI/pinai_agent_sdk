"""
Advanced example of PINAI Agent SDK
Demonstrates more complex usage including error handling and image responses
"""

import os
import logging
import argparse
import uuid
import sys
from datetime import datetime
from pinai_agent_sdk import PINAIAgentSDK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger("AdvancedAgent")

class AdvancedAgent:
    """An advanced agent implementation using the PINAI Agent SDK"""
    
    def __init__(self, api_key, agent_id=None, base_url="https://dev-agent.api.pinai.tech", polling_interval=1.0):
        """Initialize the advanced agent"""
        self.api_key = api_key
        self.base_url = base_url
        self.polling_interval = polling_interval
        self.client = None
        self.agent_id = agent_id
        self.agent_config = {
            "name": f"Advanced-Agent-{uuid.uuid4().hex[:8]}",
            "ticker": "ADVA",
            "description": "An advanced demonstration agent with enhanced features",
            "cover": "https://example.com/sample-cover.jpg",
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "capabilities": ["text_response", "image_response"]
            }
        }
        self.conversation_history = {}  # Dictionary to store conversation history by session
        
    def start(self):
        """Start the agent"""
        try:
            # Initialize SDK
            logger.info(f"Initializing SDK with base URL: {self.base_url}")
            self.client = PINAIAgentSDK(
                api_key=self.api_key,
                base_url=self.base_url,
                polling_interval=self.polling_interval
            )
            
            # If no agent_id is provided, register a new agent
            if self.agent_id is None:
                # Register agent
                logger.info(f"Registering agent: {self.agent_config['name']}")
                response = self.client.register_agent(
                    name=self.agent_config["name"],
                    ticker=self.agent_config["ticker"],
                    description=self.agent_config["description"],
                    cover=self.agent_config["cover"],
                    metadata=self.agent_config["metadata"]
                )
                self.agent_id = response.get("id")
                logger.info(f"Agent registered successfully with ID: {self.agent_id}")
            else:
                logger.info(f"Using existing agent with ID: {self.agent_id}")
            
            # Use the combined method to simplify code
            self.client.start_and_run(on_message_callback=self.handle_message, agent_id=self.agent_id)
            
            # Note: start_and_run will block until user interruption, so the code below won't execute immediately
            
        except Exception as e:
            logger.error(f"Error starting agent: {e}")
            self.cleanup()
            return False
            
        return True
    
    def handle_message(self, message):
        """Handle incoming messages"""
        try:
            # Log the received message
            logger.info(f"Message received: {message}")
            
            # Extract important information
            content = message.get("content", "")
            session_id = message.get("session_id", "")
            message_id = message.get("id")
            created_at = message.get("created_at")
            
            if not session_id:
                logger.error("Message missing session_id, cannot respond")
                return
                
            # Initialize conversation history for this session if not exists
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            # Add to conversation history
            self.conversation_history[session_id].append({
                "role": "user",
                "content": content,
                "id": message_id,
                "timestamp": created_at
            })
            
            # Get persona information for this session
            try:
                persona = self.client.get_persona(session_id)
                logger.info(f"Persona for session {session_id}: {persona.get('name', 'Unknown')}")
            except Exception as e:
                logger.warning(f"Could not retrieve persona info: {e}")
                persona = {"name": "Unknown"}
            
            # Process the message
            content_lower = content.lower()
            
            # Prepare response based on message content
            if "image" in content_lower or "picture" in content_lower:
                # Example: Respond with an image (using example URL)
                response_text = "Here's an image you requested"
                logger.info(f"Sending image response to {session_id}")
                
                # In a real implementation, you'd upload a real image here
                # media_result = self.client.upload_media("/path/to/real/image.jpg", "image")
                # image_url = media_result["media_url"]
                
                # Using a placeholder URL for example purposes
                image_url = "https://example.com/sample-image.jpg"
                
                # SDK自动使用当前的session_id
                self.client.send_message(
                    content=response_text,
                    media_type="image",
                    media_url=image_url
                )
                
                # Add response to history
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": response_text,
                    "media_type": "image",
                    "media_url": image_url,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif "help" in content_lower:
                # Send a help message
                help_text = (
                    f"Hello, {persona.get('name', 'User')}! I am an advanced PINAI Agent example. I can:\n"
                    "- Respond to your messages\n"
                    "- Send images (try asking for an image)\n"
                    "- Remember our conversation history\n"
                    "Type 'history' to see a summary of our conversation."
                )
                logger.info(f"Sending help information to {session_id}")
                self.client.send_message(
                    content=help_text
                )
                
                # Add response to history
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": help_text,
                    "timestamp": datetime.now().isoformat()
                })
                
            elif "history" in content_lower:
                # Send conversation history
                history = self.conversation_history[session_id]
                if len(history) <= 1:
                    history_text = "We don't have much conversation history yet."
                else:
                    history_text = "Here's a summary of our conversation:\n"
                    for i, entry in enumerate(history[:-1], 1):
                        sender = "You" if entry["role"] == "user" else "Me"
                        history_text += f"{i}. {sender}: {entry['content'][:50]}...\n"
                
                logger.info(f"Sending conversation history to {session_id}")
                self.client.send_message(
                    content=history_text
                )
                
                # Add response to history
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": history_text,
                    "timestamp": datetime.now().isoformat()
                })
                
            else:
                # Default response
                session_messages_count = len(self.conversation_history[session_id])
                response_text = f"You said: '{content}'. This is message #{session_messages_count} in our conversation."
                logger.info(f"Sending regular response to {session_id}")
                self.client.send_message(
                    content=response_text
                )
                
                # Add response to history
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            # Try to send an error message to the user
            try:
                self.client.send_message(
                    content="Sorry, I encountered an error while processing your request."
                )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
    
    def cleanup(self):
        """Clean up resources and unregister agent"""
        if self.client:
            try:
                # Stop the client
                logger.info("Stopping client...")
                self.client.stop()
                
                # Unregister the agent
                if self.agent_id and not getattr(self, 'use_existing_agent', False):
                    logger.info(f"Unregistering agent ID: {self.agent_id}")
                    self.client.unregister_agent(self.agent_id)
                    logger.info("Agent unregistered")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run an advanced PINAI Agent")
    parser.add_argument("--api-key", default=os.environ.get("PINAI_API_KEY"), help="PINAI API Key (or set PINAI_API_KEY environment variable)")
    parser.add_argument("--base-url", default="https://dev-agent.api.pinai.tech", help="API base URL")
    parser.add_argument("--polling-interval", type=float, default=1.0, help="Polling interval in seconds")
    parser.add_argument("--agent-id", type=int, help="Existing agent ID to use instead of creating a new one")
    args = parser.parse_args()
    
    # Check if API key is provided
    if not args.api_key:
        print("Error: No API key provided. Use --api-key argument or set PINAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Create and start agent
    agent = AdvancedAgent(
        api_key=args.api_key,
        agent_id=args.agent_id,
        base_url=args.base_url,
        polling_interval=args.polling_interval
    )
    
    # If using an existing agent, set a flag to prevent unregistration
    if args.agent_id:
        agent.use_existing_agent = True
    
    try:
        agent.start()
    except KeyboardInterrupt:
        print("\nUser interrupt received")
    finally:
        agent.cleanup()
        print("Agent stopped.")
    
if __name__ == "__main__":
    main()
