import uuid
from enum import Enum
from typing import Dict, Any

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResponse(BaseModel):
    task_id: uuid.UUID
    status: TaskStatus
    result: Any


class TaskStore:
    def __init__(self):
        self.store: Dict[uuid.UUID, TaskResponse] = {}

    def add_task(self) -> TaskResponse:
        task = TaskResponse(task_id=uuid.uuid4(), status=TaskStatus.PENDING, result=None)

        self.store[task.task_id] = task

        return task

    def get_task(self, task_id: uuid.UUID) -> TaskResponse:
        if task_id not in self.store:
            raise KeyError(f"Task store: {task_id=} not found.")
        return self.store[task_id]

    def update_task(self, task_id: uuid.UUID, status: TaskStatus, result: Any) -> TaskResponse:
        if task_id not in self.store:
            raise KeyError(f"Task store: {task_id=} not found.")
        task = self.store[task_id]
        task.status = status
        task.result = result
        self.store[task.task_id] = task
        return task


task_store = TaskStore()


async def process_task(task_func, **kwargs) -> TaskResponse:
    """백그라운드에서 작업 실행"""
    task = task_store.add_task()
    task_id = task.task_id
    try:
        result = await task_func(**kwargs)
        task = task_store.update_task(task_id, TaskStatus.COMPLETED, result)
    except Exception as e:
        task = task_store.update_task(task_id, TaskStatus.FAILED, f"오류 발생: {str(e)}")
    return task


def get_task(task_id: uuid.UUID) -> TaskResponse:
    return task_store.get_task(task_id)
