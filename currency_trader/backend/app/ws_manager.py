"""WebSocket connection manager for broadcasting real-time updates."""
import asyncio
import json
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self._active:
            self._active.remove(websocket)

    async def broadcast(self, data: dict):
        dead = []
        for ws in list(self._active):
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)
