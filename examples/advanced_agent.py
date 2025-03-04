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
    
    def __init__(self, api_key, base_url="https://dev-web.pinai.tech/", polling_interval=1.0):
        """Initialize the advanced agent"""
        self.api_key = api_key
        self.base_url = base_url
        self.polling_interval = polling_interval
        self.client = None
        self.agent_config = {
            "name": f"Advanced-Agent-{uuid.uuid4().hex[:8]}",
            "category": "demo",
            "description": "An advanced demonstration agent with enhanced features",
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "capabilities": ["text_response", "image_response"]
            }
        }
        self.conversation_history = []
        
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
            
            # Register agent
            logger.info(f"Registering agent: {self.agent_config['name']}")
            response = self.client.register_agent(
                name=self.agent_config["name"],
                category=self.agent_config["category"],
                description=self.agent_config["description"],
                metadata=self.agent_config["metadata"]
            )
            logger.info(f"Agent registered successfully: {response}")
            
            # Start listening for messages
            logger.info("Starting to listen for messages...")
            self.client.start(on_message_callback=self.handle_message)
            
            # Run the agent until interrupted
            logger.info(f"Agent {self.agent_config['name']} is running. Press Ctrl+C to stop.")
            self.client.run_forever()
            
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
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message.get("content", ""),
                "timestamp": message.get("timestamp", datetime.now().timestamp() * 1000)
            })
            
            # Process the message
            content = message.get("content", "").lower()
            
            # Prepare response based on message content
            if "image" in content or "picture" in content:
                # Example: respond with an image URL if requested
                response_text = "Here's an image you requested"
                image_url = "https://example.com/sample-image.jpg"  # Replace with actual image URL
                
                logger.info(f"Sending image response: {response_text} with image: {image_url}")
                self.client.send_message(
                    content=response_text,
                    image_url=image_url
                )
            elif "help" in content:
                # Send a help message
                help_text = (
                    "I am an advanced PINAI Agent example. I can:\n"
                    "- Respond to your messages\n"
                    "- Send images (try asking for an image)\n"
                    "- Remember our conversation history\n"
                    "Type 'history' to see our conversation summary."
                )
                logger.info(f"Sending help information")
                self.client.send_message(content=help_text)
            elif "history" in content:
                # Send conversation history
                if len(self.conversation_history) <= 1:
                    history_text = "We don't have much conversation history yet."
                else:
                    history_text = "Here's a summary of our conversation:\n"
                    for i, entry in enumerate(self.conversation_history[:-1], 1):
                        time_str = datetime.fromtimestamp(entry["timestamp"]/1000).strftime('%H:%M:%S')
                        history_text += f"{i}. [{time_str}] You: {entry['content'][:50]}...\n"
                
                logger.info(f"Sending conversation history")
                self.client.send_message(content=history_text)
            else:
                # Default response
                response_text = f"You said: '{content}'. This is message #{len(self.conversation_history)} in our conversation."
                logger.info(f"Sending regular response: {response_text}")
                self.client.send_message(content=response_text)
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text if 'response_text' in locals() else "Image response",
                "timestamp": datetime.now().timestamp() * 1000
            })
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            # Try to send an error message to the user
            try:
                self.client.send_message(content=f"Sorry, I encountered an error processing your request.")
            except:
                pass
    
    def cleanup(self):
        """Clean up resources and unregister agent"""
        if self.client:
            try:
                # Stop the client
                logger.info("Stopping client...")
                self.client.stop()
                
                # Unregister the agent
                logger.info(f"Unregistering agent: {self.agent_config['name']}")
                self.client.unregister_agent(name=self.agent_config["name"])
                logger.info("Agent unregistered")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run an advanced PINAI Agent")
    parser.add_argument("--api-key", default=os.environ.get("PINAI_API_KEY"), help="PINAI API Key (or set PINAI_API_KEY environment variable)")
    parser.add_argument("--base-url", default="https://dev-web.pinai.tech/", help="API base URL")
    parser.add_argument("--polling-interval", type=float, default=1.0, help="Polling interval in seconds")
    args = parser.parse_args()
    
    # Check if API key is provided
    if not args.api_key:
        print("Error: No API key provided. Use --api-key argument or set PINAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Create and start agent
    agent = AdvancedAgent(
        api_key=args.api_key,
        base_url=args.base_url,
        polling_interval=args.polling_interval
    )
    
    try:
        agent.start()
    except KeyboardInterrupt:
        print("\nUser interrupt received")
    finally:
        agent.cleanup()
        print("Agent stopped.")
    
if __name__ == "__main__":
    main()
