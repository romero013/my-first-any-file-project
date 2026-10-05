# Базовая ORM модель
from uuid import uuid4
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# DeclarativeBase — базовый класс SQLAlchemy для ORM моделей
# Mapped        — аннотация типа для колонок таблицы
# mapped_column — функция описания колонки (primary key, default и т.д.)


class Base(DeclarativeBase):
# Создаём свой базовый класс наследуясь от DeclarativeBase
# Зачем? SQLAlchemy отслеживает все таблицы через Base.metadata
# Все классы которые наследуются от Base — автоматически регистрируются
# и SQLAlchemy знает о них при вызове Base.metadata.create_all()
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda: str(uuid4()))

# default=lambda: str(uuid4()) — почему не default=str(uuid4())?
# Без lambda:  uuid4() → "f47a..." — вычислилось один раз при старте
#              Все записи: id = "f47a..."  ❌

# С lambda:    lambda: str(uuid4()) — это функция
#              Запись 1: id = "f47a..."
#              Запись 2: id = "a12b..."   ✅
#              Запись 3: id = "c99d..."