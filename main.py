from uuid import uuid4
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

#-----------------Модели задач-----------------
class Task(BaseModel):
    """Модель задачи"""
    id: str
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title : str | None = None
    completed : bool | None = None

#---------------Модели категорий---------------
class Category(BaseModel):
    id: str
    name: str


tasks: list[Task] = []
categories: list[Category] = []

@app.get("/tasks", response_model=list[Task], status_code=status.HTTP_200_OK)
def read_root() -> list[Task]:
    """Получить список задач"""
    return tasks

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    """Создать новую задачу"""
    new_task = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(new_task)
    return new_task

@app.patch("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id, payload: TaskUpdate) -> Task:
    for task in tasks:
        if task_id == task.id:
            if payload.title is not None:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed

    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id) -> None:
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)

@app.get("/categories", status_code=status.HTTP_200_OK)
def get_categories() -> list[Category]:
    return categories