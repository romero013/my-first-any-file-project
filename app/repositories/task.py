# Работа с БД
from sqlalchemy import select
# select — функция для построения SELECT-запросов
# select(TaskORM) → SELECT * FROM tasks
from sqlalchemy.orm import Session
# Session — тип сессии SQLAlchemy
# Используется как аннотация типа
from app.models.task import TaskORM, CategoryORM
# Импортируем ORM модель задачи


class TaskRepository:
# Repository (Репозиторий) — паттерн проектирования
# Класс который отвечает ТОЛЬКО за работу с базой данных
# Вся логика запросов к БД — здесь
# Сервисы не знают как работает БД — они просто вызывают методы репозитория
#
# Разделение ответственности:
# Repository  → работа с БД (SELECT, INSERT, UPDATE, DELETE)
# Service     → бизнес-логика (что делать с данными)
# Router      → HTTP-запросы (принять запрос, вернуть ответ)
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[TaskORM]:
    # Получить все задачи из БД
    # -> list[TaskORM] — вернёт список объектов TaskORM
        return self.db.scalars(select(TaskORM)).all()
        # select(TaskORM)     → строим SQL: SELECT * FROM tasks
        # self.db.scalars(...) → выполняем запрос, получаем итератор объектов
        # .all()              → превращаем итератор в список Python

    def get_by_id(self, task_id: str) -> TaskORM:
    # Найти одну задачу по её id
    # task_id: str — принимаем id как строку
        return self.db.get(TaskORM, task_id)
        # db.get(Класс, id) — поиск по PRIMARY KEY
        # Эквивалент: SELECT * FROM tasks WHERE id = task_id LIMIT 1
        # Вернёт объект TaskORM или None если не найдено

    def create(self, title: str) -> TaskORM:
    # Создать новую задачу в БД
    # title: str — название задачи
        new_task = TaskORM(title=title, completed=False)
        # Создаём Python-объект TaskORM
        # id генерируется автоматически через lambda: str(uuid4()) из Base
        # В БД ещё ничего не записано — это пока просто Python объект
        self.db.add(new_task)
        # Добавляем объект в сессию — "планируем" INSERT
        # В БД ещё не записано — ждём commit()
        return new_task
        # Возвращаем объект — Service использует его для ответа клиенту

    def delete(self, TaskORM) -> None:
    # Удалить задачу из БД
    # TaskORM — объект задачи которую нужно удалить
        self.db.delete(TaskORM)
        # Помечаем объект для удаления — "планируем" DELETE
        # В БД ещё не удалено — ждём commit()
        self.db.commit()
        # Применяем все запланированные операции в БД
        # DELETE выполняется только здесь

class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[CategoryORM]:
        return self.db.scalars(select(CategoryORM)).all()

    def get_by_id(self, category_id: str) -> CategoryORM:
        return self.db.get(CategoryORM, category_id)

    def create(self, name: str) -> CategoryORM:
        new_category = CategoryORM(name=name)
        self.db.add(new_category)

        return new_category

    def delete(self, CategoryORM) -> None:
        self.db.delete(CategoryORM)
        self.db.commit()