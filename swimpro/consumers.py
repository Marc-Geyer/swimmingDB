import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection
        await self.accept()
        # Log connection
        print(f"✅ WebSocket connected: {self.channel_name}")

        # Send a welcome message immediately
        await self.send(text_data=json.dumps({
            'message': 'Server connected! Waiting for your message...',
            'timestamp': 'Just now'
        }))

    async def disconnect(self, close_code):
        print(f"❌ WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        # 1. Receive data from client
        data = json.loads(text_data)
        user_message = data.get('message', '')

        print(f"📩 Received from client: {user_message}")

        # 2. Simulate a "server action" (e.g., saving to DB, logging)
        # We'll just wait 0.5s to simulate processing
        await asyncio.sleep(0.5)

        # 3. Prepare server response
        response_message = f"Server received: '{user_message}'. Time: {asyncio.get_event_loop().time()}"

        # 4. Send response back to client
        await self.send(text_data=json.dumps({
            'message': response_message,
            'type': 'server_response'
        }))