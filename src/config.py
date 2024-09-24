from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseSettings(BaseSettings):

    PROTOCOL: str
    HOST: str
    PORT: str
    NAME: str
    USER: str
    PASSWORD: SecretStr

    model_config = SettingsConfigDict(extra="ignore", env_prefix="DB_")

    @property
    def URL(self):
        return SecretStr(
            f"{self.PROTOCOL}://{self.USER}:{self.PASSWORD.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()


settings = Settings()
