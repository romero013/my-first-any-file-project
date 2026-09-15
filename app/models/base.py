from uuid import uuid4
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default= lambda: str(uuid4()))
# Base — это общий родитель для всех ORM-моделей.
# SQLAlchemy требует чтобы все классы-таблицы были связаны через одного общего предка — именно через него SQLAlchemy знает о существовании всех таблиц.
# Без Base SQLAlchemy просто не увидит классы и не создаст таблицы.

# default=lambda: str(uuid4()) — почему не default=str(uuid4())?
# Без lambda:  uuid4() → "f47a..." — вычислилось один раз при старте
#              Все записи: id = "f47a..."  ❌

# С lambda:    lambda: str(uuid4()) — это функция
#              Запись 1: id = "f47a..."
#              Запись 2: id = "a12b..."   ✅
#              Запись 3: id = "c99d..."