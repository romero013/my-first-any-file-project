from dataclasses import dataclass

@dataclass
class Settings():
    DATABASE_URL: str
    cors_allowed_origin: list[str]

def get_settings() -> Settings:
    return Settings(
        DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres",
        cors_allowed_origin = ["http://localhost:3000"],
    )

# DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
# postgresql+psycopg  — PostgreSQL через драйвер psycopg
# postgres            — пользователь (создаётся по умолчанию в PostgreSQL)
# admin               — пароль (ты задал его через -e POSTGRES_PASSWORD=admin)
# 127.0.0.1           — хост (localhost — твой компьютер)
# 15432               — порт (тот что пробросил в docker run -p 15432:5432)
# postgres            — имя базы данных (создаётся по умолчанию)