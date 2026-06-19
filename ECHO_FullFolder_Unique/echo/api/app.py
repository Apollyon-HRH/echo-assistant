from __future__ import annotations

import json
from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import JSONResponse

from core.knowledge import KnowledgeBase

def create_app(runtime):
    app = FastAPI(title="ECHO API")
    kb = KnowledgeBase(runtime.config)

    @app.get("/")
    def index():
        return {"name": "ECHO", "status": "ok", "plugins": runtime.plugins.list()}

    @app.post("/chat/{session_id}")
    async def chat(session_id: str, payload: dict):
        prompt = payload.get("prompt", "")
        result = runtime.chat(session_id, prompt)
        return JSONResponse(result.__dict__)

    @app.get("/sessions")
    def sessions():
        return {"sessions": runtime.memory.list_sessions()}

    @app.get("/kb/search")
    def kb_search(q: str):
        return {
            "results": [
                {"source": r[1]["source"], "content": r[1]["content"][:400]}
                for r in kb.search(q)
            ]
        }

    @app.post("/kb/ingest")
    async def ingest(file: UploadFile = File(...)):
        content = (await file.read()).decode("utf-8", errors="ignore")
        kb.ingest_text(file.filename, content, {"filename": file.filename})
        return {"ok": True}

    @app.websocket("/ws/chat")
    async def ws_chat(ws: WebSocket):
        await ws.accept()
        session_id = "ws-session"
        while True:
            msg = await ws.receive_text()
            result = runtime.chat(session_id, msg)
            await ws.send_text(json.dumps(result.__dict__, ensure_ascii=False))

    return app
