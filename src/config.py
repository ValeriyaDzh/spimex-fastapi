from dotenv import load_dotenv, find_dotenv
from logging.config import dictConfig

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())


class DatabaseSettings(BaseSettings):

    MODE: str

    PROTOCOL: str
    HOST: str
    PORT: str
    NAME: str
    USER: str
    PASSWORD: SecretStr

    model_config = SettingsConfigDict(
        extra="ignore", env_prefix="DB_", env_file=".dev.env"
    )

    @property
    def URL(self):
        return SecretStr(
            f"{self.PROTOCOL}://{self.USER}:{self.PASSWORD.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class RedisSettings(BaseSettings):

    HOST: str
    PORT: str
    EXPIRE: int

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", extra="ignore", env_file=".dev.env"
    )


class LoggingSettings(BaseSettings):

    def configure_logging(self):
        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                    },
                },
                "handlers": {
                    "file": {
                        "level": "DEBUG",
                        "formatter": "default",
                        "class": "logging.FileHandler",
                        "filename": "loger.log",
                    },
                },
                "loggers": {
                    "": {
                        "handlers": ["file"],
                        "level": "DEBUG",
                        "propagate": False,
                    },
                },
            }
        )


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    log: LoggingSettings = LoggingSettings()


settings = Settings()
