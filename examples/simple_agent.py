"""
Simple example of PINAI Agent SDK
"""

import os
import logging
from pinai_agent_sdk import PINAIAgentSDK

# Set log level
logging.basicConfig(level=logging.INFO)

# Get API Key from environment variable or use example value
API_KEY = os.environ.get("PINAI_API_KEY", "your-api-key-here")

def main():
    # Initialize SDK
    client = PINAIAgentSDK(
        api_key=API_KEY
    )
    
    try:
        # Register agent
        print("Registering agent...")
        client.register_agent(
            name="Example Agent",
            category="demo",
            description="This is a demonstration agent to showcase the PINAI Agent SDK features",
            metadata={"version": "1.0", "purpose": "demonstration"}
        )
        
        # Define message handler callback
        def handle_message(message):
            """Handle received messages"""
            print(f"\nNew message received: {message}")
            
            # Extract message content
            content = message.get("content", "")
            
            # Generate reply
            reply = f"You sent: '{content}'. This is an automatic response from the Agent."
            
            # Send reply
            client.send_message(content=reply)
            print(f"Replied: {reply}")
        
        # Start listening for messages (non-blocking by default)
        print("Starting to listen for messages...")
        client.start(on_message_callback=handle_message)
        
        # Option 1: Use the built-in run_forever() method to keep the program running
        print("Agent is running. Press Ctrl+C to stop.")
        client.run_forever()
        
        # Option 2: Alternatively, you can make the start() method blocking:
        # client.start(on_message_callback=handle_message, blocking=True)
            
    except KeyboardInterrupt:
        print("\nUser interrupt, cleaning up resources...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Stop listening
        if hasattr(client, "stop"):
            client.stop()
        
        # Unregister agent
        try:
            print("Unregistering agent...")
            client.unregister_agent(name="Example Agent")
            print("Agent unregistered")
        except Exception as e:
            print(f"Error unregistering agent: {e}")
        
if __name__ == "__main__":
    main()
