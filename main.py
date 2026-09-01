from uuid import uuid4
from fastapi import FastAPI, status
from pydantic import BaseModel


app = FastAPI()

class Task(BaseModel):
    """Модель задачи"""
    id: str
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str

tasks: list[Task] = []

@app.get("/tasks", response_model=list[Task], status_code=status.HTTP_200_OK)
def read_root():
    """Получить список задач"""
    return tasks

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    """Создать новую задачу"""
    task = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(task)
    return task
