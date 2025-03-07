"""
Multimodal Agent Example
Demonstrates how to create an agent that can handle and send images
"""

import os
import logging
import argparse
import sys
import re
import base64
import requests
import uuid
from io import BytesIO
from PIL import Image
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
logger = logging.getLogger("MultiModalAgent")

class MultiModalAgent:
    """
    A multimodal agent that can handle images in conversations
    """
    
    def __init__(self, api_key, agent_id=None, base_url="https://dev-agent.api.pinai.tech", polling_interval=1.0):
        """Initialize the multimodal agent"""
        self.api_key = api_key
        self.base_url = base_url
        self.polling_interval = polling_interval
        self.client = None
        self.agent_id = agent_id
        self.temp_dir = "temp_images"
        self.ensure_temp_dir()
        
        # Agent configuration
        self.agent_config = {
            "name": f"MultiModal-Agent-{uuid.uuid4().hex[:8]}",
            "ticker": "MIMG",
            "description": "A multimodal agent that can process and send images",
            "cover": "https://example.com/multimodal-cover.jpg",
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "capabilities": ["text_response", "image_processing", "image_generation"]
            }
        }
    
    def ensure_temp_dir(self):
        """Ensure temp directory exists"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            logger.info(f"Created temp directory at {self.temp_dir}")
    
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
                logger.info(f"Agent registered with ID: {self.agent_id}")
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
            
            # Extract message data
            content = message.get("content", "")
            media_type = message.get("media_type", "none")
            media_url = message.get("media_url")
            
            # Handle different types of messages
            if media_type == "image" and media_url:
                # Handle image message
                self.process_image_message(content, media_url)
            else:
                # Handle text message
                self.process_text_message(content)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.client.send_message(
                content="Sorry, I encountered an error while processing your message."
            )
    
    def process_image_message(self, content, image_url):
        """Process a message containing an image"""
        try:
            # Download the image
            logger.info(f"Downloading image from: {image_url}")
            image_data = self.download_image(image_url)
            
            if not image_data:
                self.client.send_message(
                    content="I couldn't download the image you sent."
                )
                return
                
            # Generate a filename and save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{self.temp_dir}/user_image_{timestamp}.jpg"
            
            with open(image_filename, "wb") as f:
                f.write(image_data)
            
            logger.info(f"Saved image to: {image_filename}")
            
            # Get basic image info
            try:
                with Image.open(BytesIO(image_data)) as img:
                    width, height = img.size
                    format_name = img.format
                    mode = img.mode
            except Exception as e:
                logger.error(f"Error analyzing image: {e}")
                width, height, format_name, mode = "unknown", "unknown", "unknown", "unknown"
            
            # Prepare response
            response_text = (
                f"I received your image! Here's what I know about it:\n"
                f"- Dimensions: {width}x{height} pixels\n"
                f"- Format: {format_name}\n"
                f"- Color mode: {mode}\n\n"
                f"What would you like me to do with this image?"
            )
            
            # In a real implementation, you might perform image analysis, 
            # object detection, or other computer vision tasks here
            
            # Send response
            self.client.send_message(content=response_text)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.client.send_message(
                content="I had trouble processing the image. Could you try sending it again?"
            )
    
    def process_text_message(self, content):
        """Process a text message"""
        content_lower = content.lower()
        
        # Check if user is asking for an image generation
        if "generate" in content_lower and ("image" in content_lower or "picture" in content_lower):
            # Extract what to generate using regex
            match = re.search(r"generate\s+(?:an?|a)\s+(?:image|picture)\s+of\s+(.+)", content_lower)
            if match:
                subject = match.group(1).strip()
                self.generate_image(subject)
            else:
                self.client.send_message(
                    content="I'm not sure what kind of image you want me to generate. Could you be more specific? For example, 'Generate an image of a sunset'"
                )
        
        # Check if user wants help
        elif "help" in content_lower:
            help_text = (
                "I'm a multimodal agent that can handle images! Here's what I can do:\n\n"
                "1. Analyze images you send me\n"
                "2. Generate simple images based on your description (try 'Generate an image of [subject]')\n\n"
                "Just send me an image or ask me to generate one!"
            )
            self.client.send_message(content=help_text)
            
        # Default response
        else:
            response = (
                f"You said: {content}\n\n"
                f"If you'd like to interact with images, you can:\n"
                f"- Send me an image to analyze\n"
                f"- Ask me to 'generate an image of [subject]'"
            )
            self.client.send_message(content=response)
    
    def generate_image(self, subject):
        """Generate an image based on subject (placeholder implementation)"""
        logger.info(f"Generating image of: {subject}")
        
        # In a real implementation, you would call an image generation API
        # For this example, we'll just use a placeholder image
        
        # Notify user
        self.client.send_message(
            content=f"I'm generating an image of {subject} for you..."
        )
        
        # For demo purposes, we're using placeholder images
        placeholder_url = "https://example.com/generated-image.jpg"
        
        # In a real implementation, you would:
        # 1. Generate an image using an API or local model
        # 2. Save the image locally
        # 3. Upload the image using client.upload_media()
        # 4. Send the message with the uploaded image URL
        
        # Send the placeholder response
        self.client.send_message(
            content=f"Here's the image of {subject} I generated for you!",
            media_type="image",
            media_url=placeholder_url
        )
    
    def download_image(self, url):
        """Download an image from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.client:
            try:
                # Stop the client
                logger.info("Stopping client...")
                self.client.stop()
                
                # Unregister the agent only if we created it
                if self.agent_id and not getattr(self, 'use_existing_agent', False):
                    logger.info(f"Unregistering agent ID: {self.agent_id}")
                    self.client.unregister_agent(self.agent_id)
                    logger.info("Agent unregistered")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run a multimodal PINAI Agent")
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
    agent = MultiModalAgent(
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
