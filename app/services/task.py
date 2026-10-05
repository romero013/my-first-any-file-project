# Бизнес-логика
from sqlalchemy.orm import Session
# Импортируем тип сессии для аннотации
from app.repositories.task import TaskRepository, CategoryRepository
# Импортируем репозиторий — через него работаем с БД
from app.schemas.task import TaskSchema, TaskCreateSchema, TaskUpdateSchema, \
                             CategorySchema, CategoryCreateSchema, CategoryUpdateSchema
# Импортируем схемы — для валидации входных данных и формирования ответа


class TaskNotFound(Exception):
      """Задача не найдена в БД"""
# Кастомное исключение — создаём свой тип ошибки
#
# Зачем создавать пустой класс?
# 1. Именованное исключение — можно поймать именно эту ошибку:
#    except TaskNotFound: (а не все Exception подряд)
# 2. Читаемость кода — сразу понятно что пошло не так
# 3. Разные обработчики для разных ошибок:
#    except TaskNotFound → 404
#    except DatabaseError → 500
#
# Наследуемся от Exception — Python требует этого для raise/except

class TaskService:
# Service (Сервис) — паттерн проектирования
# Класс который содержит БИЗНЕС-ЛОГИКУ приложения
# Знает ЧТО делать с данными, но не знает КАК хранить их в БД
#
    """          Цепочка вызовов:
        Router → Service → Repository → БД """
    def __init__(self, db: Session) -> None:
    # Конструктор — принимает сессию БД
        self.db = db
        # Сохраняем сессию
        self.task_repository = TaskRepository(db)
        # Создаём репозиторий передавая ему сессию
        # Теперь self.task_repository — наш инструмент для работы с БД

    def list_task(self) -> list[TaskSchema]:
    # Получить список всех задач
    # -> list[TaskSchema] — вернёт список Pydantic объектов
        tasks_orm = self.task_repository.get_all()
        # Просим репозиторий достать все задачи из БД
        # task_orm — список объектов TaskORM (SQLAlchemy объекты)
        return [TaskSchema.model_validate(task_orm) for task_orm in tasks_orm]
        # Конвертируем каждый TaskORM → TaskSchema (Pydantic)
        # model_validate — читает атрибуты ORM объекта и создаёт Pydantic объект
        # from_attributes=True в TaskSchema позволяет это делать
        # List comprehension — проходим по списку и конвертируем каждый элемент

    def create_task(self, task_create: TaskCreateSchema) -> TaskSchema:
    # Создать новую задачу
    # task_create: TaskCreateSchema — данные от клиента (только title)
        task_orm = self.task_repository.create(title=task_create.title)
        # Просим репозиторий создать задачу в БД
        # Передаём только title — id и completed генерируются автоматически
        self.db.commit()
        # Применяем изменения в БД (фиксируем транзакцию)
        # Без commit() — INSERT не сохранится
        return TaskSchema.model_validate(task_orm)
        # Конвертируем TaskORM → TaskSchema и возвращаем клиенту

    def update_task(self, task_id: str, task_update: TaskUpdateSchema) -> TaskSchema:
    # Обновить задачу
    # task_id: str — id задачи которую обновляем
    # task_update: TaskUpdateSchema — новые данные (title и/или completed)
        task_for_update = self.task_repository.get_by_id(task_id=task_id)
        # Ищем задачу в БД по id
        # Вернёт TaskORM объект или None
        if not task_for_update:
        # Если задача не найдена (None — это False в Python)
            raise TaskNotFound(f"Задача с id {task_id} не найдена")
            # Бросаем наше кастомное исключение
            # Router поймает его и вернёт клиенту 404
        
        if task_update.title is not None:
        # Обновляем title только если клиент его передал
            task_for_update.title = task_update.title
            # Меняем атрибут объекта — SQLAlchemy отслеживает изменения
            # автоматически пометит запись для UPDATE при commit()
        if task_update.completed is not None:
        # Обновляем completed только если клиент его передал
            task_for_update.completed = task_update.completed
        
        self.db.commit()
        # Фиксируем изменения в БД
        # SQLAlchemy выполнит: UPDATE tasks SET ... WHERE id = task_id
        self.db.refresh(task_for_update)
        return TaskSchema.model_validate(task_for_update)
        # Возвращаем обновлённую задачу клиенту

    def delete_task(self, task_id: str) -> None:
    # Удалить задачу
    # -> None — ничего не возвращаем (204 No Content)
        task_for_delete = self.task_repository.get_by_id(task_id=task_id)
        # Ищем задачу по id
        if not task_for_delete:
        # Если не найдена — бросаем исключение
            raise TaskNotFound(f"Задача с id {task_id} не найдена")
        
        self.task_repository.delete(task_for_delete)
        # Удаляем через репозиторий

class CategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.category_repository = CategoryRepository(db)

    def list_category(self) -> list[CategorySchema]:
        categories_orm = self.category_repository.get_all()
        return [CategorySchema.model_validate(category_orm) for category_orm in categories_orm]

    def create_category(self, category_create: CategoryCreateSchema) -> CategorySchema:
        category_orm = self.category_repository.create(name=category_create.name)
        self.db.commit()
        return CategorySchema.model_validate(category_orm)

    def update_category(self, category_id: str, category_update: CategoryUpdateSchema) -> CategorySchema:
        category_for_update = self.category_repository.get_by_id(category_id=category_id)

        if not category_for_update:
            raise TaskNotFound(f"Задача с id {category_id} не найдена")

        if category_update.name is not None:
            category_for_update.name = category_update.name

        self.db.commit()
        self.db.refresh(category_for_update)
        return CategorySchema.model_validate(category_for_update)

    def delete_category(self, category_id: str) -> None:
        category_for_delete = self.category_repository.get_by_id(category_id=category_id)

        if not category_for_delete:
            raise TaskNotFound(F"Задача с id {category_id} не найдена")

        self.category_repository.delete(category_for_delete)