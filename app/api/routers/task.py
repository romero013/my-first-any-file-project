# Маршруты
from fastapi import APIRouter, Depends, HTTPException, status
# APIRouter     — роутер для группировки маршрутов
# Depends       — механизм внедрения зависимостей
# HTTPException — класс для возврата HTTP-ошибок (404, 422 и т.д.)
# status        — константы HTTP-статусов (HTTP_200_OK = 200 и т.д.)
from app.schemas.task import TaskSchema, TaskUpdateSchema, TaskCreateSchema, \
                             CategorySchema, CategoryCreateSchema, CategoryUpdateSchema
# Импортируем Pydantic схемы для валидации данных
from app.services.task import TaskNotFound, TaskService, CategoryService
# TaskNotFound  — наше кастомное исключение (для обработки 404)
# TaskService   — сервис с бизнес-логикой
from app.api.dependencies import get_task_service, get_category_service
# Функция-фабрика для создания TaskService

task_router = APIRouter(prefix="/tasks")
# Создаём роутер — объект который хранит все маршруты этого файла
# В main.py подключим его к приложению: app.include_router(task_router=task_router)
# Это позволяет разделить маршруты по файлам для удобства
category_router = APIRouter(prefix="/categories")

#-----------------Ручки задач-----------------
@task_router.get("", status_code=status.HTTP_200_OK)
# @router.get — регистрируем GET-маршрут
# "/tasks"    — URL: http://localhost:8080/tasks
# status_code=200 — при успехе вернём статус 200 OK
def read_tasks(task_service: TaskService = Depends(get_task_service)) -> list[TaskSchema]:
# task_service: TaskService = Depends(get_task_service)
#    ↑                           ↑
# параметр                    FastAPI автоматически вызовет get_task_service()
#                             и передаст результат (TaskService объект) в task_service
#
# -> list[TaskSchema] — функция вернёт список Pydantic объектов
    return task_service.list_task()
    # Вызываем метод сервиса — он вернёт список задач из БД


@task_router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateSchema,
    # payload — тело запроса от клиента: {"title": "Купить хлеб"}
    # FastAPI автоматически:
    # 1. Читает JSON из тела запроса
    # 2. Валидирует через TaskCreateSchema (есть ли поле title?)
    # 3. Создаёт объект TaskCreateSchema
    # 4. Передаёт в payload
    task_service: TaskService = Depends(get_task_service)
    # task_service   — имя параметра (любое)
    # TaskService    — тип параметра (аннотация)
    # =              — значение по умолчанию
    # Depends(...)   — говорит FastAPI: "создай это автоматически"
    # get_task_service — функция которую вызовет FastAPI
    #
    # Полная цепочка что происходит:
    # 1. FastAPI видит Depends(get_task_service)
    # 2. Вызывает get_task_service(db=Depends(get_db))
    # 3. Внутри get_task_service — вызывает get_db()
    # 4. get_db() создаёт сессию БД и делает yield db
    # 5. get_task_service получает db и создаёт TaskService(db)
    # 6. TaskService передаётся в task_service параметр функции
    # 7. После выполнения функции — get_db() закрывает сессию
) -> TaskSchema:
    return task_service.create_task(task_create=payload)
    # Передаём payload (данные от клиента) в сервис
    # Сервис создаст задачу в БД и вернёт TaskSchema


@task_router.patch("/{task_id}", status_code=status.HTTP_200_OK)
# {task_id} — path-параметр, берётся из URL
def update_task(
    task_id: str,
    # task_id — автоматически извлекается из URL
    # FastAPI видит {task_id} в пути и передаёт значение сюда
    payload: TaskUpdateSchema,
    # Тело запроса: {"title": "новое название"} или {"completed": true}
    # Все поля опциональные — можно передать одно или оба
    task_service: TaskService = Depends(get_task_service)
    # комментарий выше
) -> TaskSchema:
    try:
        return task_service.update_task(task_id=task_id, task_update=payload)
        # Передаём id и новые данные в сервис
        # Если всё хорошо — вернём обновлённую задачу
    except TaskNotFound:
        # Ловим наше кастомное исключение (TaskNotFound)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        # Бросаем HTTP-ошибку — FastAPI сформирует ответ:
        # {"detail": "Not Found"} со статусом 404


@task_router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
# 204 No Content — при удалении тело ответа отсутствует
def delete_task(
    task_id: str,
    # task_id — автоматически извлекается из URL
    # FastAPI видит {task_id} в пути и передаёт значение сюда
    task_service: TaskService = Depends(get_task_service)
    # комментарий выше
) -> None:
    try:
        task_service.delete_task(task_id=task_id)
        # Удаляем задачу через сервис
    except TaskNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        # Если задача не найдена — возвращаем 404

@category_router.get("", status_code=status.HTTP_200_OK)
def read_category(category_service: CategoryService = Depends(get_category_service)) -> list[CategorySchema]:
    return category_service.list_category()


@category_router.post("", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreateSchema,
    category_service: CategoryService = Depends(get_category_service)
) -> CategorySchema:
    return category_service.create_category(category_create=payload)


@category_router.patch("/{category_id}", status_code=status.HTTP_200_OK)
def update_category(
    category_id:str,
    payload: CategorySchema,
    category_service: CategoryService = Depends(get_category_service)
) -> CategorySchema:
    try:
        return category_service.update_category(category_id=category_id, category_update=payload)
    except TaskNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    category_service: CategoryService = Depends(get_category_service)
) -> None:
    try:
        category_service.delete_category(category_id=category_id)
    except TaskNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)