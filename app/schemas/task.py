# Pydantic схемы
from pydantic import BaseModel, ConfigDict
# BaseModel  — базовый класс Pydantic для валидации данных
# ConfigDict — класс для настройки поведения Pydantic модели


#-----------------Модели задач-----------------
class TaskSchema(BaseModel):
# TaskSchema — схема задачи для ответа клиенту (JSON)
# Используется когда нужно отдать данные о задаче фронтенду
# Pydantic автоматически конвертирует объект в JSON
    model_config = ConfigDict(from_attributes=True)
    # from_attributes=True — разрешаем читать данные из атрибутов объектов
    # Без этого Pydantic умеет читать только из словарей {"id": "...", "title": "..."}
    # С этим — умеет читать из ORM объектов task_orm.id, task_orm.title
    # Нужно чтобы TaskSchema.model_validate(task_orm) работало корректно
    
    id: str
    title: str
    completed: bool = False

class TaskCreateSchema(BaseModel):
# Схема для СОЗДАНИЯ задачи
# Клиент отправляет только title — id и completed генерируются на сервере
# Разделение схем — хорошая практика безопасности:
# клиент не может сам задать id или completed при создании
    title: str

class TaskUpdateSchema(BaseModel):
    title : str | None = None
    # str | None — может быть строкой или None
    # = None — по умолчанию None (поле не передано)
    # Если клиент не передал title — он останется прежним
    completed : bool | None = None
    # Аналогично — если не передан, останется прежним



# ---------------Модели категорий---------------
class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str

class CategoryCreateSchema(BaseModel):
    name: str

class CategoryUpdateSchema(BaseModel):
    name: str | None = None