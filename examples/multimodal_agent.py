"""
Multimodal PINAI Agent Example
Demonstrates how to create an agent that can process and send images
"""

import os
import logging
import argparse
import sys
import tempfile
import requests
from datetime import datetime
from pinai_agent_sdk import PINAIAgentSDK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('multimodal_agent.log')
    ]
)
logger = logging.getLogger("MultimodalAgent")

class MultimodalAgent:
    """A PINAI Agent implementation with multimodal capabilities"""
    
    def __init__(self, api_key, base_url="https://dev-web.pinai.tech/", polling_interval=1.0):
        """Initialize the multimodal agent"""
        self.api_key = api_key
        self.base_url = base_url
        self.polling_interval = polling_interval
        self.client = None
        self.agent_id = None
        
        # Define agent configuration
        self.agent_config = {
            "name": f"Multimodal Assistant",
            "ticker": "MULT",
            "description": "An agent that can process and send images",
            "cover": "https://images.unsplash.com/photo-1579547945413-497e1b99dac0",
            "metadata": {
                "version": "1.0",
                "capabilities": ["text", "image"]
            }
        }
        
        # Predefined image URLs (in a real application, you might use a more sophisticated image generation or retrieval system)
        self.image_collection = {
            "cat": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba",
            "dog": "https://images.unsplash.com/photo-1543466835-00a7907e9de1",
            "flower": "https://images.unsplash.com/photo-1490750967868-88aa4486c946",
            "mountain": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b",
            "beach": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
            "city": "https://images.unsplash.com/photo-1519501025264-65ba15a82390"
        }
        
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
                ticker=self.agent_config["ticker"],
                description=self.agent_config["description"],
                cover=self.agent_config["cover"],
                metadata=self.agent_config["metadata"]
            )
            self.agent_id = response.get("id")
            logger.info(f"Agent registered successfully with ID: {self.agent_id}")
            
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
            
            # Extract important information
            content = message.get("content", "")
            session_id = message.get("session_id", "")
            user_id = message.get("user_id", "")
            
            if not session_id:
                logger.error("Message missing session_id, cannot respond")
                return
                
            # Get persona information for this session
            try:
                persona = self.client.get_persona(session_id)
                logger.info(f"Persona for session {session_id}: {persona.get('name', 'Unknown')}")
                user_name = persona.get('name', 'User')
            except Exception as e:
                logger.warning(f"Could not retrieve persona info: {e}")
                user_name = "User"
            
            # Process the message content
            content_lower = content.lower()
            
            # Check if we need to send an image
            for keyword, image_url in self.image_collection.items():
                if keyword in content_lower:
                    # User requested an image matching the keyword
                    response_text = f"Here's a {keyword} image for you, {user_name}"
                    
                    # In a real application, you might need to download and upload the image to PINAI
                    # For demonstration, we'll use the predefined URL
                    self._send_image_response(session_id, response_text, image_url)
                    return
            
            # Check if the message contains an image URL
            if "http" in content_lower and any(ext in content_lower for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                # Try to extract URLs from the message
                urls = self._extract_urls(content)
                if urls:
                    # Try to download and process the first URL
                    image_url = urls[0]
                    try:
                        self._process_user_image(session_id, image_url)
                        return
                    except Exception as e:
                        logger.error(f"Error processing user image: {e}")
                        # Continue to default reply
            
            # Default replies
            if "help" in content_lower:
                help_text = (
                    f"Hello, {user_name}! I'm a multimodal agent that can process and send images.\n\n"
                    "You can try the following:\n"
                    "1. Ask for a specific image, e.g., 'Send me a cat image'. Currently supported keywords: " + 
                    ", ".join(self.image_collection.keys()) + "\n"
                    "2. Send me an image URL and I'll try to analyze it\n"
                    "3. Type 'help' anytime to see this message"
                )
                self.client.send_message(
                    content=help_text,
                    session_id=session_id
                )
            else:
                # Generic reply
                response_text = (
                    f"Thanks for your message, {user_name}! If you'd like to see an image, try saying 'send me a cat image'.\n"
                    f"Or type 'help' to see what I can do."
                )
                self.client.send_message(
                    content=response_text,
                    session_id=session_id
                )
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            # Try to send an error message to the user
            try:
                if session_id:
                    self.client.send_message(
                        content="Sorry, I encountered an error while processing your request.",
                        session_id=session_id
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
    
    def _extract_urls(self, text):
        """Extract URLs from text"""
        import re
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        return url_pattern.findall(text)
    
    def _process_user_image(self, session_id, image_url):
        """Process an image URL sent by the user"""
        try:
            # Download the image
            logger.info(f"Attempting to download user image: {image_url}")
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Create a temporary file to save the image
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            
            # Upload the image to PINAI
            logger.info("Uploading image to PINAI")
            media_result = self.client.upload_media(temp_path, "image")
            media_url = media_result.get("media_url")
            
            # Send analysis result and image
            response_text = "I received your image and here it is after processing."
            self.client.send_message(
                content=response_text,
                session_id=session_id,
                media_type="image",
                media_url=media_url
            )
            
            # Clean up temporary file
            os.remove(temp_path)
            logger.info("Image processing complete")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading image: {e}")
            self.client.send_message(
                content="Sorry, I couldn't download the image you provided. Please ensure the URL is valid and publicly accessible.",
                session_id=session_id
            )
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.client.send_message(
                content="Sorry, I encountered an issue while processing your image.",
                session_id=session_id
            )
    
    def _send_image_response(self, session_id, text, image_url):
        """Send a response with an image"""
        try:
            logger.info(f"Sending image response, URL: {image_url}")
            self.client.send_message(
                content=text,
                session_id=session_id,
                media_type="image",
                media_url=image_url
            )
        except Exception as e:
            logger.error(f"Error sending image response: {e}")
            # Try to send a text-only reply
            try:
                self.client.send_message(
                    content=f"{text} (Sorry, I couldn't send the image)",
                    session_id=session_id
                )
            except Exception:
                pass
    
    def cleanup(self):
        """Clean up resources and unregister agent"""
        if self.client:
            try:
                # Stop the client
                logger.info("Stopping client...")
                self.client.stop()
                
                # Unregister the agent
                if self.agent_id:
                    logger.info(f"Unregistering agent ID: {self.agent_id}")
                    self.client.unregister_agent(self.agent_id)
                    logger.info("Agent unregistered")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run a multimodal PINAI Agent")
    parser.add_argument("--api-key", default=os.environ.get("PINAI_API_KEY"), help="PINAI API Key (or set PINAI_API_KEY environment variable)")
    parser.add_argument("--base-url", default="https://dev-web.pinai.tech/", help="API base URL")
    parser.add_argument("--polling-interval", type=float, default=1.0, help="Polling interval in seconds")
    args = parser.parse_args()
    
    # Check if API key is provided
    if not args.api_key:
        print("Error: No API key provided. Use --api-key argument or set PINAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Create and start agent
    agent = MultimodalAgent(
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
