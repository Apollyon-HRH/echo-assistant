from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio
import uuid

@dataclass
class Task:
    id: str
    name: str
    payload: dict
    status: str = "queued"
    result: Any = None

class TaskQueue:
    def __init__(self):
        self.queue: asyncio.Queue[Task] = asyncio.Queue()
        self.history: dict[str, Task] = {}

    async def submit(self, name: str, payload: dict) -> Task:
        task = Task(id=str(uuid.uuid4()), name=name, payload=payload)
        self.history[task.id] = task
        await self.queue.put(task)
        return task

    async def worker(self, handler):
        while True:
            task = await self.queue.get()
            try:
                task.status = "running"
                task.result = await handler(task)
                task.status = "done"
            except Exception as e:
                task.status = "failed"
                task.result = str(e)
            finally:
                self.queue.task_done()
