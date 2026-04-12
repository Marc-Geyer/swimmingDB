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


class CalendarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'calendar_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Optional: Handle client-side requests (e.g., "fetch more data")
        pass

    # Receive message from group (triggered by signals or manual broadcast)
    async def session_update(self, event):
        session_id = event['session_id']
        action = event['action']  # 'created', 'updated', 'deleted', 'cancelled'
        data = event['data']

        await self.send(text_data=json.dumps({
            'type': 'session_change',
            'session_id': session_id,
            'action': action,
            'payload': data
        }))


# Helper to broadcast updates (call this in signals or views)
async def broadcast_session_change(session, action):
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()

    # Serialize minimal data needed for the frontend
    payload = {
        'id': session.id,
        'start': str(session.start),
        'end': str(session.end),
        'is_cancelled': session.is_cancelled,
        'notes': session.notes,
        'location': session.location,
        'plan_id': session.plan.id if session.plan else None
    }

    await channel_layer.group_send(
        'calendar_updates',
        {
            'type': 'session_update',
            'session_id': session.id,
            'action': action,
            'data': payload
        }
    )