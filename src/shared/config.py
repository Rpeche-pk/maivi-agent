from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    OPEN_AI_KEY= str
    MODEL_NAME= str

settings = Settings()