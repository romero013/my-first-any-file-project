from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session



DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker[Session](bind=engine)


class Base(DeclarativeBase): # для чего создаем класс Base и далее наследуемся от него? Почему нельзя создать последующие классы без него.
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda: str(uuid4()))


class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False, server_default="false")


@asynccontextmanager
async def lifespan (_: FastAPI): # почему использовали "_" вместо "app" (на app ругался IDE)?
    Base.metadata.create_all(bind=engine) # создать все таблицы для БД наследованные из класса Base (при запуске приложения)
    yield


app = FastAPI(title="Мой мини-проект", lifespan=lifespan)

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

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str | None = None

categories: list[Category] = []

def get_db():
    db = Sessionlocal()

    try:
        yield db
    finally:
        db.close()


def task_orm_to_model(task_orm: TaskORM) -> Task:
    return Task(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)


#-----------------Ручки задач-----------------
@app.get("/tasks", status_code=status.HTTP_200_OK)
def read_tasks(db: Session = Depends(get_db)) -> list[Task]:
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(task) for task in tasks_from_db]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()
    return task_orm_to_model(new_task)

@app.patch("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task_for_update = db.get(TaskORM, task_id)
    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
            task_for_update.completed = payload.completed

    db.commit()
    db.refresh(task_for_update)
    return task_for_update

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id, db: Session = Depends(get_db)) -> None:
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()


#---------------Ручки категорий---------------
@app.get("/categories", response_model=list[Category], status_code=status.HTTP_200_OK)
def get_categories() -> list[Category]:
    return categories

@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate) -> Category:
    new_category = Category(id=str(uuid4()), name=payload.name)
    categories.append(new_category)
    return new_category

@app.patch("/categories/{category_id}", response_model=CategoryCreate, status_code=status.HTTP_200_OK)
def update_category(category_id, payload: CategoryUpdate) -> Category:
    for category in categories:
        if category.id == category_id:
            if category.name is not None:
                category.name = payload.name
            return category
    # Если цикл прошёл все категории и не нашёл нужную — бросаем ошибку
    raise HTTPException(status_code=404, detail="Category not found")

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id) -> None:
    for category in categories:
        if category.id == category_id:
            categories.remove(category)
            return None
    # Если цикл прошёл все категории и не нашёл нужную — бросаем ошибку
    raise HTTPException(status_code=404, detail="Category not found")