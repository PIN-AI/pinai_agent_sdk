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
    
    # Get the message content
    content = message.get("content", "")
    
    # Simple echo response
    response = f"You said: {content}"
    
    # 使用新的发送消息方法 - 不需要提供session_id
    client.send_message(content=response)
    logger.info(f"Response sent: {response}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run a simple PINAI Agent")
    parser.add_argument("--api-key", default=os.environ.get("PINAI_API_KEY"), help="PINAI API Key (or set PINAI_API_KEY environment variable)")
    parser.add_argument("--base-url", default="https://emute3dbtc.us-east-1.awsapprunner.com", help="API base URL")
    parser.add_argument("--agent-name", default="Simple-Echo-Agent", help="Name for the agent")
    parser.add_argument("--agent-ticker", default="ECHO", help="Ticker for the agent (usually 4 uppercase letters)")
    parser.add_argument("--agent-id", default=9, type=int, help="Existing agent ID to use (if provided, will not register a new agent)")
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
        # 如果提供了agent_id，则使用现有的agent
        if args.agent_id:
            logger.info(f"Using existing agent with ID: {args.agent_id}")
            agent_id = args.agent_id
        else:
            logger.info(f"")
            # 否则注册新的agent
            # logger.info(f"Registering new agent: {args.agent_name}")
            # response = client.register_agent(
            #     name=args.agent_name,
            #     ticker=args.agent_ticker,
            #     description="A simple echo agent that repeats user messages",
            #     cover="https://example.com/cover.jpg"  # Optional
            # )
            # agent_id = response.get("id")
            # logger.info(f"Agent registered successfully with ID: {agent_id}")
        
        # 启动监听，使用agent_id参数
        logger.info("Starting to listen for messages...")
        # 使用新的组合方法，简化代码
        client.start_and_run(on_message_callback=handle_message, agent_id=agent_id)
        
        # 注意：start_and_run会阻塞直到用户中断，所以下面的代码不会立即执行
        
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
            if not args.agent_id:  # 只有当我们自己注册了agent时才注销它
                logger.info("Unregistering agent...")
                client.unregister_agent()
                logger.info("Agent unregistered")
        except Exception as e:
            logger.error(f"Error unregistering agent: {e}")
        
        print("Agent stopped.")

if __name__ == "__main__":
    main()
