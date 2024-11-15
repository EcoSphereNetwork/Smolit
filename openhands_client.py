import aiohttp
import json
from typing import Dict, List, Optional

class OpenHandsClient:
    def __init__(self, supervisor_url: str = "http://localhost:8000", instance_urls: List[str] = None):
        self.supervisor_url = supervisor_url
        self.instance_urls = instance_urls or ["http://localhost:8001", "http://localhost:8002"]
        
    async def send_to_supervisor(self, message: str) -> Dict:
        """Send a message to the Supervisor Agent."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.supervisor_url}/v1/chat",
                json={"message": message}
            ) as response:
                return await response.json()

    async def send_to_instance(self, instance_id: int, message: str) -> Dict:
        """Send a message to a specific OpenHands instance."""
        if instance_id >= len(self.instance_urls):
            raise ValueError(f"Invalid instance ID: {instance_id}")
            
        url = self.instance_urls[instance_id]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{url}/v1/chat",
                json={"message": message}
            ) as response:
                return await response.json()

    async def upload_file(self, file_path: str) -> str:
        """Upload a file to the Supervisor Agent."""
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f)
                async with session.post(
                    f"{self.supervisor_url}/v1/upload",
                    data=data
                ) as response:
                    result = await response.json()
                    return result.get('file_id', '')
