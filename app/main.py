# Точка входа
from contextlib import asynccontextmanager
# asynccontextmanager — декоратор для создания async контекстных менеджеров
# Нужен для функции lifespan которая управляет жизнью приложения
from fastapi import FastAPI
# FastAPI — основной класс фреймворка
# Depends — механизм зависимостей (используется в некоторых эндпоинтах)
from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware — промежуточный слой для настройки CORS
# CORS — политика браузера, запрещающая запросы с других доменов
# Без этого фронтенд на localhost:3000 не сможет обращаться к бэкенду на localhost:8080

from app.models.base import Base
# Base — общий родитель всех ORM моделей
# Нужен для Base.metadata.create_all() — создания таблиц
from app.db.session import engine
# engine — движок подключения к БД
# Передаём в create_all чтобы знал в какую БД создавать таблицы
from app.api.routers.task import task_router, category_router
# Импортируем роутер задач из файла routers/task.py
# as task_router — даём псевдоним чтобы не путать с другими роутерами


@asynccontextmanager
# Декоратор превращает функцию в асинхронный контекстный менеджер
# FastAPI использует его как lifecycle hook (хук жизненного цикла)
async def lifespan (_: FastAPI):
# lifespan — функция управляющая жизненным циклом приложения
# _: FastAPI — параметр который FastAPI передаёт (объект app)
# _ — соглашение "параметр есть но не используется"
# Почему _ вместо app? Потому что app уже занято переменной ниже
    Base.metadata.create_all(bind=engine)
    # Создаёт все таблицы в БД которые унаследованы от Base
    # metadata — реестр всех ORM моделей зарегистрированных в Base
    # create_all — проходит по всем моделям и выполняет CREATE TABLE IF NOT EXISTS
    # bind=engine — в какую БД создавать таблицы
    # Выполняется ОДИН РАЗ при старте приложения
    yield
    # Здесь приложение запускается и начинает обрабатывать запросы
    # Код до yield = "при старте"
    # Код после yield = "при остановке" (здесь его нет)

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
# Создаём экземпляр FastAPI приложения
# title="Мой мини-проект" — название в Swagger документации (http://localhost:8080/docs)
# lifespan=lifespan — передаём функцию жизненного цикла
#                     FastAPI вызовет её при старте и остановке
app.include_router(router=task_router)
# Подключаем роутер задач к приложению
# Все маршруты из task_router (/tasks GET, POST, PATCH, DELETE)
# становятся доступны в приложении
app.include_router(router=category_router)

app.add_middleware(
    CORSMiddleware,
    # Добавляем CORS промежуточный слой
    allow_origins=[
        "http://localhost:3000",
    # Разрешаем запросы только с этого адреса (фронтенд)
    # ["*"] разрешило бы запросы со ВСЕХ адресов (небезопасно для продакшена)
    ],
    allow_methods=["*"],
    # Разрешаем все HTTP методы: GET, POST, PATCH, DELETE и т.д.
    allow_headers=["*"],
    # Разрешаем все заголовки запроса
    allow_credentials=True,
    # Разрешаем передачу куки и заголовков авторизации
)
    