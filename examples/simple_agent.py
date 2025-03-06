"""
PINAI Agent SDK - Minimal Example
Perfect for hackathons and quick prototyping
"""

import os
from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL

# Your API key - get it from PINAI platform
API_KEY = os.environ.get("PINAI_API_KEY", "")

# Initialize the SDK client
client = PINAIAgentSDK(api_key=API_KEY)

def handle_message(message):
    """
    Process incoming messages and respond
    
    Args:
        message (dict): Message object with format:
            {
                "session_id": "unique-session-id",
                "id": 12345,  # Message ID
                "content": "user message text",
                "created_at": "2023-01-01T12:00:00"
            }
    """
    print(f"Received: {message['content']}")

    session_id = message.get("session_id")
    if not session_id:
        print("Message missing session_id, cannot respond")
        return
    
    # Get user's message
    user_message = message.get("content", "")

    # Get persona info
    persona_info = client.get_persona(session_id)
    
    # Create your response (this is where your agent logic goes)
    response = f"Echo: {user_message}"
    
    # Send response back to user
    client.send_message(content=response)
    print(f"Sent: {response}")

def main():
    """Main function to run the agent"""
    try:
        # Option 1: Register a new agent (first time)
        # Uncomment and modify this section to register a new agent
        """
        agent_info = client.register_agent(
            name="My Hackathon Agent",
            description="A simple agent built during the hackathon",
            category=AGENT_CATEGORY_SOCIAL,  # Choose from available categories
            # Optional: wallet="your_wallet_address"
        )
        agent_id = agent_info.get("id")
        print(f"Agent registered with ID: {agent_id}")
        """
        
        # Option 2: Use existing agent (after registration)
        # Replace 123 with your actual agent ID from registration
        agent_id = 28
        
        print("Starting agent... Press Ctrl+C to stop")
        
        # Start listening for messages and responding
        client.start_and_run(
            on_message_callback=handle_message,
            agent_id=agent_id
        )
        
    except KeyboardInterrupt:
        print("\nStopping agent...")
    finally:
        # Clean up
        client.stop()
        print("Agent stopped")

if __name__ == "__main__":
    main()
