from environs import Env
from pydantic import BaseModel, SecretStr


class BotSettings(BaseModel):
    token: SecretStr
    owner_id: SecretStr


class LogSetting(BaseModel):
    level: str
    format: str


class Config(BaseModel):
    bot_settings: BotSettings
    log_settings: LogSetting


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot_settings=BotSettings(
            token=env("BOT_TOKEN"),
            owner_id=env("OWNER_ID")
        ),
        log_settings=LogSetting(
            level=env("LOG_LEVEL"),
            format=env("LOG_FORMAT")
        )
    )
