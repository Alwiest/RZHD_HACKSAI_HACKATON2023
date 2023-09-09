import asyncio
from typing import Any, Dict, Optional

import aiohttp


class Client:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_recommendations(self, train_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/get_recommendations/"
        data = {"train_id": train_id}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                result = await response.json()
                return result


if __name__ == "__main__":
    base_url = "http://127.0.0.1:8000"
    client = Client(base_url)

    train_id = "853"

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(client.get_recommendations(train_id))

    print(result)
