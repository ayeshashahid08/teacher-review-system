from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra ="ignore" )
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    GEMINI_API_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()
