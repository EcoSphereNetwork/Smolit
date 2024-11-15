import asyncio
from agents.core.multi_agent_system import MultiAgentSystem
import logging

logging.basicConfig(level=logging.DEBUG)

async def main():
    try:
        # Initialize with correct API base
        agent_system = MultiAgentSystem(
            api_base="http://localhost:8080/v1",
            api_key=""
        )
        
        # Process a test message
        response = await agent_system.process_input("hey")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

