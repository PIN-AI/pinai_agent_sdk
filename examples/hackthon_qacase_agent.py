"""
PINAI Agent SDK - Basic QA Agent
gitp uUsing README.md as knowledge source with conversation history
pip install pinai-agent-sdk langchain langchain-community langchain-text-splitters langchain-openai faiss-cpu
"""

import os
from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Import FAISS with logging suppressed for the GPU warning
import logging
logging.getLogger('faiss').setLevel(logging.ERROR)
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# Your API keys
PINAI_API_KEY = os.environ.get("PINAI_API_KEY", "your-pinai-api-key")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
AGENT_ID = os.environ.get("AGENT_ID", 42)

# Initialize the PINAI SDK client
client = PINAIAgentSDK(api_key=PINAI_API_KEY)

# Initialize knowledge base from README.md
def initialize_knowledge_base():
    """Create and return a QA chain based on README.md knowledge source"""
    # Load the document
    loader = TextLoader("../README.md")
    documents = loader.load()
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Create a retrieval chain
    llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3})
    )
    
    return qa_chain

# Initialize vector store for reuse
vector_store = None

# Dictionary to store conversation memories for each user
user_memories = {}

def initialize_knowledge_base():
    """Create and return vector store based on README.md knowledge source"""
    global vector_store
    
    # Load the document
    loader = TextLoader("../README.md")
    documents = loader.load()
    
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(documents)
    
    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    return vector_store

# Initialize the vector store
vector_store = initialize_knowledge_base()

def get_conversation_chain(session_id):
    """Get or create a conversation chain with memory for a specific user"""
    global user_memories
    
    # Create a new memory if this user doesn't have one yet
    if session_id not in user_memories:
        user_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    # Create a conversational retrieval chain with the user's memory
    llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=user_memories[session_id],
        verbose=True
    )
    
    return conversation_chain

def handle_message(message):
    """
    Process incoming messages and respond with information from knowledge base,
    maintaining conversation history per user
    
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
    
    try:
        # Get the conversation chain for this specific user
        conversation_chain = get_conversation_chain(session_id)
        
        # Query the knowledge base with conversation history
        result = conversation_chain({"question": user_message})
        answer = result.get("answer", "")
        
        # If no answer is found, provide a fallback response
        if not answer or answer.strip() == "":
            response = "I don't have enough information to answer that question based on my knowledge source."
        else:
            response = answer
            
    except Exception as e:
        print(f"Error processing query: {e}")
        response = "I encountered an error while trying to answer your question. Please try again or rephrase your question."

    # Send response back to user
    client.send_message(content=response, session_id=session_id)
    print(f"Sent: {response}")

def main():
    """Main function to run the QA agent"""
    try:
        # Option 1: Register a new agent (first time)
        # Uncomment and modify this section to register a new agent
        """
        agent_info = client.register_agent(
            name="ReadMe QA Agent with Memory",
            description="A QA agent that answers questions based on ReadMe.md with conversation history",
            category=AGENT_CATEGORY_SOCIAL,
            # Optional: wallet="your_wallet_address"
        )
        agent_id = agent_info.get("id")
        print(f"Agent registered with ID: {agent_id}")
        """

        # Option 2: Use existing agent (after registration)
        # Replace 42 with your actual agent ID from registration
        agent_id = AGENT_ID

        print("Starting QA agent with conversation history... Press Ctrl+C to stop")
        print("Knowledge base initialized from ReadMe.md")
        print("Conversation memories will be maintained per user session")

        # Start listening for messages and responding
        client.start_and_run(
            on_message_callback=handle_message,
            agent_id=agent_id
        )

    except KeyboardInterrupt:
        print("\nStopping agent...")
    except Exception as e:
        print(f"Error running agent: {e}")
    finally:
        # Clean up
        client.stop()
        print("Agent stopped")

if __name__ == "__main__":
    main()