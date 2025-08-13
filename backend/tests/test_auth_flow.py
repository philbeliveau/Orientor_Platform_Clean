import os
import httpx
import asyncio
from datetime import datetime

async def test_authentication():
    # Get token from frontend context (simulated)
    token = os.getenv('TEST_TOKEN', 'your_test_token_here')
    if not token or token == 'your_test_token_here':
        print("Please set TEST_TOKEN environment variable with a valid Clerk JWT")
        return

    async with httpx.AsyncClient() as client:
        # Test our endpoint
        print(f"\nTesting authentication at {datetime.now().isoformat()}")
        response = await client.get(
            'http://localhost:8000/api/v1/test-token',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(test_authentication())
