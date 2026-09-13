from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import Depends, FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session



DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
# postgresql+psycopg  — PostgreSQL через драйвер psycopg
# postgres            — пользователь (создаётся по умолчанию в PostgreSQL)
# admin               — пароль (ты задал его через -e POSTGRES_PASSWORD=admin)
# 127.0.0.1           — хост (localhost — твой компьютер)
# 15432               — порт (тот что пробросил в docker run -p 15432:5432)
# postgres            — имя базы данных (создаётся по умолчанию)
engine = create_engine(DATABASE_URL)
# engine — это "соединитель" между Python и PostgreSQL. 
# Он не открывает соединение сразу — он только описывает как подключаться. 
# Реальное соединение открывается когда нужно выполнить запрос.
Sessionlocal = sessionmaker(bind=engine)
# sessionmaker — фабрика сессий, то есть функция которая создаёт новые сессии:
# sessionmaker(bind=engine)
#               ↑
#     привязываем к нашему engine
#     чтобы каждая новая сессия знала к какой БД подключаться

# Использование:
# db = SessionLocal()   # создать новую сессию
# db.close()            # закрыть сессию после работы


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda: str(uuid4()))
# Base — это общий родитель для всех ORM-моделей.
# SQLAlchemy требует чтобы все классы-таблицы были связаны через одного общего предка — именно через него SQLAlchemy знает о существовании всех таблиц.
# Без Base SQLAlchemy просто не увидит классы и не создаст таблицы.

# default=lambda: str(uuid4()) — почему не default=str(uuid4())?
# Без lambda:  uuid4() → "f47a..." — вычислилось один раз при старте
#              Все записи: id = "f47a..."  ❌

# С lambda:    lambda: str(uuid4()) — это функция
#              Запись 1: id = "f47a..."
#              Запись 2: id = "a12b..."   ✅
#              Запись 3: id = "c99d..."


class TaskORM(Base):
    __tablename__ = "tasks"
    
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False, server_default="false")

class CategoryORM(Base):
    __tablename__ = "categories"

    name: Mapped[str]


@asynccontextmanager
async def lifespan (_: FastAPI):
#                   ↑
# FastAPI передаёт сюда объект "app", но мы его не используем внутри функции
# IDE ругается на "app" потому что видит конфликт с глобальной переменной app = FastAPI()
# _ — общепринятое соглашение для "игнорируемого параметра"
    Base.metadata.create_all(bind=engine) # Создать все таблицы для БД наследованные из класса Base (создает таблицы при запуске приложения)
#           ↑
#       metadata — это реестр всех таблиц наследованных от Base
#       create_all — пройти по всем и создать в БД
    yield

# lifespan — функция которая управляет жизненным циклом приложения:
# Запуск приложения
#       ↓
# [ код до yield ]    ← create_all — создаём таблицы
#       ↓
#    yield            ← приложение работает, обрабатывает запросы
#       ↓
# [ код после yield ] ← здесь можно закрыть соединения, очистить ресурсы
#       ↓
# Остановка приложения


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

#-----------Вспомогательные функции------------
def get_db():
    db = Sessionlocal() # создаём новую сессию (соединение с БД)

    try:
        yield db # Передаём сессию в эндпоинт. Здесь выполняется весь код эндпоинта.
    finally:
        db.close() # ВСЕГДА закрываем сессию после запроса. finally — выполнится даже если была ошибка.

# Работа функции get_db():

# Запрос пришёл
#       ↓
# get_db() создаёт сессию
#       ↓
# yield db — сессия передана в эндпоинт
#       ↓
# эндпоинт работает с БД
#       ↓
# finally: db.close() — сессия закрыта
#       ↓
# Ответ отправлен клиенту

# Если не закрывать сессии — соединения накапливаются и БД перестаёт принимать новые подключения.

def task_orm_to_model(task_orm: TaskORM) -> Task:
    return Task(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)
# TaskORM  — SQLAlchemy объект, "понимает" БД, умеет делать запросы
# Task     — Pydantic объект, "понимает" JSON, умеет сериализоваться для ответа клиенту

# FastAPI не умеет автоматически конвертировать TaskORM в JSON — нужно сначала превратить его в Pydantic-модель Task. Эта функция и делает такое преобразование.

def category_orm_to_model(category_orm: CategoryORM) -> Category:
    return Category(id=category_orm.id, name=category_orm.name)


#-----------------Ручки задач-----------------
@app.get("/tasks", status_code=status.HTTP_200_OK)
def read_tasks(db: Session = Depends(get_db)) -> list[Task]:
# Depends — механизм внедрения зависимостей в FastAPI. 
# Говорит: "перед вызовом этой функции — сначала вызови get_db() и передай результат в параметр db"

# Запрос GET /tasks
#       ↓
# FastAPI видит Depends(get_db)
#       ↓
# Автоматически вызывает get_db()
#       ↓
# get_db() создаёт сессию и делает yield db
#       ↓
# db передаётся в read_tasks()
#       ↓
# После выполнения — get_db() закрывает сессию

# Без Depends тебе пришлось бы в каждом эндпоинте вручную писать:
# db = SessionLocal()
# try:
#     # работа с БД
# finally:
#     db.close()

# Depends делает это автоматически — один раз написал get_db(), используешь везде.

    tasks_from_db = db.scalars(select(TaskORM)).all()
    
# select(TaskORM)          # SQL: SELECT * FROM tasks
#                          # генерирует SQL-запрос (но ещё не выполняет)

# db.scalars(...)          # выполняет запрос и возвращает итератор объектов TaskORM
#                          # scalars() — берёт первый столбец результата (объекты TaskORM)

# .all()                   # преобразует итератор в список Python
#                          # [TaskORM(...), TaskORM(...), ...]
    
    return [task_orm_to_model(task) for task in tasks_from_db]

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    new_task = TaskORM(title=payload.title, completed=False) # payload — это объект класса TaskCreate
    
    # FastAPI читает тело запроса JSON, валидирует через TaskCreate и создаёт объект.
    # После этого payload.title — обычное обращение к атрибуту объекта.
    
    db.add(new_task)
    db.commit()
    return task_orm_to_model(new_task)

@app.patch("/tasks/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
def update_task(task_id, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
# task_id — строка из URL (/tasks/f47a...)
# payload — тело запроса, валидируется через TaskUpdate
# db — сессия БД, создаётся через Depends(get_db)
    task_for_update = db.get(TaskORM, task_id)
# db.get(TaskORM, task_id) — найти запись в таблице tasks по PRIMARY KEY
# эквивалент: SELECT * FROM tasks WHERE id = task_id LIMIT 1
# возвращает объект TaskORM или None если не найдено
    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
            task_for_update.completed = payload.completed

    db.commit()
    db.refresh(task_for_update)
# db.commit()                  — сохраняет изменения в БД
#                                но объект в памяти Python может быть устаревшим

# db.refresh(task_for_update)  — перечитывает объект из БД заново
#                                гарантирует что возвращаем актуальные данные
    return task_for_update

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id, db: Session = Depends(get_db)) -> None:
    task_for_delete = db.get(TaskORM, task_id) # найти задачу по id в БД — вернёт объект TaskORM или None
    db.delete(task_for_delete) # пометить объект для удаления
    # реальное удаление произойдёт после commit()
    # SQLAlchemy: DELETE FROM tasks WHERE id = task_id
    db.commit() # выполнить все ожидающие операции в БД
    # без commit() — удаление не сохранится, откатится назад


#---------------Ручки категорий---------------
@app.get("/categories", status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)) -> list[Category]:
    categories_from_db = db.scalars(select(CategoryORM)).all()
    return [category_orm_to_model(category) for category in categories_from_db]

@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    new_category = CategoryORM(name=payload.name)
    db.add(new_category)
    db.commit()
    return category_orm_to_model(new_category)

@app.patch("/categories/{category_id}", response_model=CategoryCreate, status_code=status.HTTP_200_OK)
def update_category(category_id, payload: CategoryUpdate, db: Session = Depends(get_db)) -> Category:
    category_for_update = db.get(CategoryORM, category_id)
    if category_for_update is None:
        # Если цикл прошёл все категории и не нашёл нужную — бросаем ошибку
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        category_for_update.name = payload.name
    db.commit()
    db.refresh(category_for_update)
    return category_for_update
    
@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id, db: Session = Depends(get_db)) -> None:
    category_for_delete = db.get(CategoryORM, category_id)
    if category_for_delete is None:
        # Если цикл прошёл все категории и не нашёл нужную — бросаем ошибку
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category_for_delete)
    db.commit()
    