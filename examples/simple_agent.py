"""
Simple example of PINAI Agent SDK
Demonstrates basic usage of the SDK
"""

import os
import logging
import argparse
import sys
from pinai_agent_sdk import PINAIAgentSDK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_agent.log')
    ]
)
logger = logging.getLogger("SimpleAgent")

def handle_message(message):
    """
    Handle messages received from the server
    
    Message format:
    {
        "session_id": "session-id",
        "id": 12345,  # Message ID
        "content": "message content",
        "created_at": "2025-03-05T12:30:00"  # ISO 8601 timestamp
    }
    """
    logger.info(f"Message received: {message}")
    
    # Extract session_id from the message
    session_id = message.get("session_id")
    if not session_id:
        logger.error("Message missing session_id, cannot respond")
        return
    
    # Get the message content
    content = message.get("content", "")
    
    # Simple echo response
    response = f"You said: {content}"
    
    # Send the response
    client.send_message(
        content=response,
        session_id=session_id
    )
    logger.info(f"Response sent: {response}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run a simple PINAI Agent")
    parser.add_argument("--api-key", default=os.environ.get("PINAI_API_KEY"), help="PINAI API Key (or set PINAI_API_KEY environment variable)")
    parser.add_argument("--base-url", default="https://emute3dbtc.us-east-1.awsapprunner.com", help="API base URL")
    parser.add_argument("--agent-name", default="Simple-Echo-Agent", help="Name for the agent")
    parser.add_argument("--agent-ticker", default="ECHO", help="Ticker for the agent (usually 4 uppercase letters)")
    args = parser.parse_args()
    
    # Check if API key is provided
    if not args.api_key:
        print("Error: No API key provided. Use --api-key argument or set PINAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Initialize SDK
    global client
    client = PINAIAgentSDK(
        api_key=args.api_key,
        base_url=args.base_url
    )
    
    try:
        # Register agent
        logger.info(f"Registering agent: {args.agent_name}")
        response = client.register_agent(
            name=args.agent_name,
            ticker=args.agent_ticker,
            description="A simple echo agent that repeats user messages",
            cover="https://example.com/cover.jpg"  # Optional
        )
        agent_id = response.get("id")
        logger.info(f"Agent registered successfully with ID: {agent_id}")
        
        # Start listening for messages
        logger.info("Starting to listen for messages...")
        client.start(on_message_callback=handle_message)
        
        # Keep the application running until interrupted
        logger.info(f"Agent {args.agent_name} is running. Press Ctrl+C to stop.")
        client.run_forever()
        
    except KeyboardInterrupt:
        print("\nUser interrupt received")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Stop the client
        logger.info("Stopping client...")
        client.stop()
        
        # Unregister agent (if we have a client)
        try:
            logger.info("Unregistering agent...")
            client.unregister_agent()
            logger.info("Agent unregistered")
        except Exception as e:
            logger.error(f"Error unregistering agent: {e}")
        
        print("Agent stopped.")

if __name__ == "__main__":
    main()
