from environs import Env
from pydantic import BaseModel, SecretStr
from sqlalchemy import URL


class BotSettings(BaseModel):
    token: SecretStr
    owner_id: SecretStr


class DbSettings(BaseModel):
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


class LogSetting(BaseModel):
    level: str
    format: str


class Config(BaseModel):
    bot_settings: BotSettings
    db_settings: DbSettings
    log_settings: LogSetting


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot_settings=BotSettings(
            token=env("BOT_TOKEN"),
            owner_id=env("OWNER_ID")
        ),
        db_settings=DbSettings(
            db_schema=env("POSTGRES_SCHEMA"),
            db_driver=env("POSTGRES_DRIVER"),
            db_name=env("POSTGRES_DB"),
            host=env("POSTGRES_HOST"),
            port=env.int("POSTGRES_PORT"),
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            is_echo=env.bool("POSTGRES_IS_ECHO"),
        ),
        log_settings=LogSetting(
            level=env("LOG_LEVEL"),
            format=env("LOG_FORMAT")
        ),
    )
