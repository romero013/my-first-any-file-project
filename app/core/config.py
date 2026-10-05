# Настройки
from dataclasses import dataclass
# dataclass — декоратор из стандартной библиотеки Python
# Он автоматически создаёт __init__, __repr__ и другие методы для класса
# Без него пришлось бы вручную писать def __init__(self, DATABASE_URL, cors_allowed_origin)
from dotenv import load_dotenv
import os


load_dotenv()

@dataclass(frozen=True)
# Этот декоратор превращает обычный класс в "класс данных"
# После него Python сам понимает что DATABASE_URL и cors_allowed_origin
# это параметры конструктора — не нужно писать __init__ вручную
# frozen=True — чтобы случайно не поменять настройки данных из вне

class Settings:
# Settings — класс для хранения настроек приложения
# Это как коробка с настройками — всё в одном месте
# Хорошая практика: все настройки в одном месте, а не раскиданы по коду

    DATABASE_URL: str
    # Строка подключения к базе данных
    # Тип str — аннотация, говорит что значение должно быть строкой

    cors_allowed_origin: list[str]
    # Список разрешённых источников для CORS
    # list[str] — список строк (адресов фронтенда)


def get_settings() -> Settings:
# Функция-фабрика — создаёт и возвращает объект Settings
# -> Settings — аннотация возвращаемого типа, функция вернёт объект Settings
# Зачем функция, а не просто объект?
# Так удобнее тестировать и подменять настройки в тестах

    return Settings(
        DATABASE_URL=os.getenv('DATABASE_URL'),
        cors_allowed_origin=os.getenv('cors_allowed_origin', '').split(','),
    )