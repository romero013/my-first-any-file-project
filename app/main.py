from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.db.session import engine

from app.api.routers.task import router as task_router


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
app.include_router(router=task_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)



#---------------Модели категорий---------------
# class CategorySchema(BaseModel):
#     id: str
#     name: str

# class CategoryCreateSchema(BaseModel):
#     name: str

# class CategoryUpdateSchema(BaseModel):
#     name: str | None = None


#-----------Вспомогательные функции------------


# def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
#     return TaskSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)
# # TaskORM  — SQLAlchemy объект, "понимает" БД, умеет делать запросы
# # Task     — Pydantic объект, "понимает" JSON, умеет сериализоваться для ответа клиенту

# # FastAPI не умеет автоматически конвертировать TaskORM в JSON — нужно сначала превратить его в Pydantic-модель Task. Эта функция и делает такое преобразование.

# def category_orm_to_model(category_orm: CategoryORM) -> CategorySchema:
#     return CategorySchema(id=category_orm.id, name=category_orm.name)



#---------------Ручки категорий---------------
# @app.get("/categories", status_code=status.HTTP_200_OK)
# def get_categories(db: Session = Depends(get_db)) -> list[CategorySchema]:
#     categories_from_db = db.scalars(select(CategoryORM)).all()
#     return [category_orm_to_model(category) for category in categories_from_db]

# @app.post("/categories", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
# def create_category(payload: CategoryCreateSchema, db: Session = Depends(get_db)) -> CategorySchema:
#     new_category = CategoryORM(name=payload.name)
#     db.add(new_category)
#     db.commit()
#     return category_orm_to_model(new_category)

# @app.patch("/categories/{category_id}", response_model=CategoryCreateSchema, status_code=status.HTTP_200_OK)
# def update_category(category_id, payload: CategoryUpdateSchema, db: Session = Depends(get_db)) -> CategorySchema:
#     category_for_update = db.get(CategoryORM, category_id)
#     if category_for_update is None:
#         # Если цикл прошёл все категории и не нашёл нужную — бросаем ошибку
#         raise HTTPException(status_code=404, detail="Category not found")
#     if payload.name is not None:
#         category_for_update.name = payload.name
#     db.commit()
#     db.refresh(category_for_update)
#     return category_for_update
    
# @app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_category(category_id, db: Session = Depends(get_db)) -> None:
#     category_for_delete = db.get(CategoryORM, category_id)
#     if category_for_delete is None:
#         # Если цикл прошёл все категории и не нашёл нужную — бросаем ошибку
#         raise HTTPException(status_code=404, detail="Category not found")
#     db.delete(category_for_delete)
#     db.commit()
    