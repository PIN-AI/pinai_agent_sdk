from pinai_agent_sdk import PINAIAgentSDK, AGENT_CATEGORY_SOCIAL
client = PINAIAgentSDK(api_key="pin_MTI0MDAwMTM6NTI5Mzg_Toouz5tmIo2WzCp8")
client.start_and_run(
    on_message_callback=lambda message: print(message),
    agent_id=28
)