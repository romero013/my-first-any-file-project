# ORM модель задачи
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
# Импортируем Base из соседнего файла base.py
# Точка перед base означает "из текущей папки" (относительный импорт)
# Base уже содержит колонку id — она автоматически появится в TaskORM


class TaskORM(Base):
# TaskORM — ORM класс, представляет таблицу "tasks" в PostgreSQL
# ORM (Object-Relational Mapping) — технология которая связывает
# Python-классы с таблицами в базе данных
#
# Каждый объект TaskORM = одна строка в таблице tasks
# TaskORM(title="Купить хлеб") → INSERT INTO tasks VALUES (...)
    __tablename__ = "tasks"
    # Имя таблицы в PostgreSQL
    # SQLAlchemy создаст таблицу с именно таким именем
    # Без этого атрибута SQLAlchemy не знает как назвать таблицу

    # id не указываем — он унаследован от Base
    
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False, server_default="false")
    # server_default — значение по умолчанию на уровне POSTGRESQL
    # PostgreSQL сам подставит false если INSERT пришёл без этого поля
    
    # Зачем оба параметра?
    # default        — защита на уровне Python (когда создаём объект)
    # server_default — защита на уровне БД (когда INSERT доходит до PostgreSQL)        
    # Вместе они гарантируют что completed никогда не будет NULL


class CategoryORM(Base):
    __tablename__ = "categories"

    name: Mapped[str]
