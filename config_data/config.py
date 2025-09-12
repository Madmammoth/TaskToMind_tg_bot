from environs import Env
from pydantic import BaseModel, SecretStr


class BotSettings(BaseModel):
    token: SecretStr
    owner_id: SecretStr


class Config(BaseModel):
    bot_settings: BotSettings


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot_settings=BotSettings(
            token=env("BOT_TOKEN"),
            owner_id=env("OWNER_ID")
        )
    )
