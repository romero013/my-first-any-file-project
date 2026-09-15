from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
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

def get_db():
    """Функция для инъекции сессии Базы Данных"""
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