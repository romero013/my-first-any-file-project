# Зависимости
from fastapi import Depends
# Depends — механизм внедрения зависимостей FastAPI
from sqlalchemy.orm import Session
# Session — тип сессии SQLAlchemy (для аннотации типа)
from app.services.task import TaskService, CategoryService
# Импортируем сервис задач
from app.db.session import get_db
# Импортируем функцию получения сессии БД


def get_task_service(db: Session = Depends(get_db)):
    """Функция для инъекции зависимости TaskService"""
    # Эта функция — фабрика TaskService
    # FastAPI вызывает её автоматически для каждого запроса
    #
    # db: Session = Depends(get_db)
    # ↑             ↑
    # параметр      FastAPI сам вызовет get_db() и передаст результат в db
    #
    # Цепочка зависимостей:
    # get_task_service → Depends(get_db) → создаёт сессию БД
    #                  → создаёт TaskService(db)
    #                  → передаёт в эндпоинт
    return TaskService(db)
    # Создаём сервис передавая ему сессию БД
    # TaskService получает сессию и создаёт TaskRepository

def get_category_service(db: Session = Depends(get_db)):
    return CategoryService(db)