from typing import Dict, List, Optional, Callable
from datetime import datetime
import asyncio
import websockets
import json
from .models import DigitalCreator, ContentPost, ContentType

class LiveStream:
    def __init__(self, creator: DigitalCreator, title: str, description: str = ""):
        self.id = f"stream_{creator.id}_{datetime.now().timestamp()}"
        self.creator = creator
        self.title = title
        self.description = description
        self.is_live = False
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.viewers: List[str] = []
        self.chat_messages: List[Dict] = []
        self.tips: List[Dict] = []
        self.polls: List[Dict] = []
        self.websocket_connections: List[websockets.WebSocketServerProtocol] = []

    def start_stream(self):
        self.is_live = True
        self.started_at = datetime.now()

    def end_stream(self):
        self.is_live = False
        self.ended_at = datetime.now()

    def add_viewer(self, viewer_id: str):
        if viewer_id not in self.viewers:
            self.viewers.append(viewer_id)

    def remove_viewer(self, viewer_id: str):
        if viewer_id in self.viewers:
            self.viewers.remove(viewer_id)

    def add_chat_message(self, user_id: str, message: str):
        msg = {
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.chat_messages.append(msg)
        # Broadcast to all connected websockets
        asyncio.create_task(self._broadcast_message(msg))

    def add_tip(self, user_id: str, amount: float, message: str = ""):
        tip = {
            'user_id': user_id,
            'amount': amount,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.tips.append(tip)
        # Trigger tip goal check
        asyncio.create_task(self._broadcast_tip(tip))

    def create_poll(self, question: str, options: List[str]) -> str:
        poll_id = f"poll_{len(self.polls)}"
        poll = {
            'id': poll_id,
            'question': question,
            'options': {opt: 0 for opt in options},
            'votes': {},
            'created_at': datetime.now().isoformat()
        }
        self.polls.append(poll)
        return poll_id

    def vote_poll(self, poll_id: str, user_id: str, option: str):
        for poll in self.polls:
            if poll['id'] == poll_id and option in poll['options']:
                if user_id not in poll['votes']:
                    poll['options'][option] += 1
                    poll['votes'][user_id] = option
                    asyncio.create_task(self._broadcast_poll_update(poll))
                break

    async def _broadcast_message(self, message: Dict):
        for ws in self.websocket_connections:
            try:
                await ws.send(json.dumps({'type': 'chat', 'data': message}))
            except:
                pass

    async def _broadcast_tip(self, tip: Dict):
        for ws in self.websocket_connections:
            try:
                await ws.send(json.dumps({'type': 'tip', 'data': tip}))
            except:
                pass

    async def _broadcast_poll_update(self, poll: Dict):
        for ws in self.websocket_connections:
            try:
                await ws.send(json.dumps({'type': 'poll_update', 'data': poll}))
            except:
                pass

class StreamingManager:
    def __init__(self):
        self.active_streams: Dict[str, LiveStream] = {}
        self.stream_history: List[LiveStream] = []

    def start_stream(self, creator: DigitalCreator, title: str, description: str = "") -> LiveStream:
        """Start a new live stream for a creator"""
        stream = LiveStream(creator, title, description)
        stream.start_stream()
        self.active_streams[creator.id] = stream
        creator.is_online = True
        return stream

    def end_stream(self, creator_id: str):
        """End a creator's live stream"""
        if stream := self.active_streams.get(creator_id):
            stream.end_stream()
            self.stream_history.append(stream)
            del self.active_streams[creator_id]
            stream.creator.is_online = False

    def get_active_stream(self, creator_id: str) -> Optional[LiveStream]:
        """Get the active stream for a creator"""
        return self.active_streams.get(creator_id)

    def get_stream_stats(self, creator_id: str) -> Dict:
        """Get streaming statistics for a creator"""
        active_stream = self.get_active_stream(creator_id)
        if active_stream:
            return {
                'is_live': True,
                'viewer_count': len(active_stream.viewers),
                'duration': (datetime.now() - active_stream.started_at).total_seconds(),
                'tips_total': sum(tip['amount'] for tip in active_stream.tips),
                'chat_messages': len(active_stream.chat_messages)
            }

        # Return stats from last stream if no active stream
        last_stream = next((s for s in reversed(self.stream_history) if s.creator.id == creator_id), None)
        if last_stream:
            return {
                'is_live': False,
                'last_stream_viewers': len(last_stream.viewers),
                'last_stream_duration': (last_stream.ended_at - last_stream.started_at).total_seconds() if last_stream.ended_at else 0,
                'last_stream_tips': sum(tip['amount'] for tip in last_stream.tips)
            }

        return {'is_live': False}

    async def handle_websocket_connection(self, websocket, creator_id: str):
        """Handle WebSocket connections for live streaming"""
        stream = self.get_active_stream(creator_id)
        if not stream:
            await websocket.close()
            return

        stream.websocket_connections.append(websocket)

        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get('type')

                if msg_type == 'join':
                    stream.add_viewer(data['user_id'])
                elif msg_type == 'chat':
                    stream.add_chat_message(data['user_id'], data['message'])
                elif msg_type == 'tip':
                    stream.add_tip(data['user_id'], data['amount'], data.get('message', ''))
                elif msg_type == 'vote':
                    stream.vote_poll(data['poll_id'], data['user_id'], data['option'])

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if websocket in stream.websocket_connections:
                stream.websocket_connections.remove(websocket)

    def schedule_stream(self, creator: DigitalCreator, title: str, scheduled_time: datetime):
        """Schedule a future stream"""
        # In a real implementation, this would use a task scheduler like Celery
        print(f"Stream scheduled for {creator.name} at {scheduled_time}: {title}")

    def get_popular_streams(self) -> List[LiveStream]:
        """Get currently popular live streams"""
        return sorted(self.active_streams.values(),
                     key=lambda s: len(s.viewers), reverse=True)[:10]