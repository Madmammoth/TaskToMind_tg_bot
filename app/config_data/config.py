from environs import Env
from pydantic import BaseModel, SecretStr
from sqlalchemy import URL


class BotSettings(BaseModel):
    token: SecretStr
    owner_id: SecretStr


class PostgresSettings(BaseModel):
    db_schema: str
    db_driver: str
    db_name: str
    host: str
    port: int
    user: SecretStr
    password: SecretStr
    is_echo: bool

    def get_dsn(self) -> URL:
        dsn = URL.create(
            drivername=f"{self.db_schema}+{self.db_driver}",
            username=self.user.get_secret_value(),
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.db_name,
        )
        return dsn


class RedisSettings(BaseModel):
    db: int
    host: str
    port: int
    password: SecretStr
    username: str


class LogSettings(BaseModel):
    level: str
    format: str


class Config(BaseModel):
    bot_settings: BotSettings
    pg_settings: PostgresSettings
    redis_settings: RedisSettings
    log_settings: LogSettings


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot_settings=BotSettings(
            token=env("BOT_TOKEN"),
            owner_id=env("OWNER_ID")
        ),
        pg_settings=PostgresSettings(
            db_schema=env("POSTGRES_SCHEMA"),
            db_driver=env("POSTGRES_DRIVER"),
            db_name=env("POSTGRES_DB"),
            host=env("POSTGRES_HOST"),
            port=env.int("POSTGRES_PORT"),
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            is_echo=env.bool("POSTGRES_IS_ECHO"),
        ),
        redis_settings=RedisSettings(
            db=env.int("REDIS_DATABASE"),
            host=env("REDIS_HOST"),
            port=env.int("REDIS_PORT"),
            password=env("REDIS_PASSWORD"),
            username=env("REDIS_USERNAME"),
        ),
        log_settings=LogSettings(
            level=env("LOG_LEVEL"),
            format=env("LOG_FORMAT")
        ),
    )
