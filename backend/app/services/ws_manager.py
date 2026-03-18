import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per analysis job."""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self._connections[job_id].add(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket):
        self._connections[job_id].discard(websocket)
        if not self._connections[job_id]:
            del self._connections[job_id]

    async def broadcast(self, job_id: str, message: dict):
        dead: list[WebSocket] = []
        for ws in self._connections.get(job_id, set()):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections[job_id].discard(ws)


manager = ConnectionManager()
