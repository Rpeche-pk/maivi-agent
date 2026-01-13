from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    OPEN_AI_KEY : str
    MODEL_NAME : str
    NAME_AGENT :str
    PORT : int = Field(default= 3003)
    LOG_NAME : str = Field(default= "ai_service")
    URL_WSP : str = Field(default= "ws://localhost:3003/ws")
    PHONE_NUMBER : str = Field(default= "+1234567890")
    IMAGEKIT_PRIVATE_KEY: str
    IMAGEKIT_PUBLIC_KEY: str
    URL_ENDPOINT_IMAGEKIT: str
    DATABASE_URL: str
    DATABASE_NAME :str
    COLLECTION_NAME:str

settings = Settings()