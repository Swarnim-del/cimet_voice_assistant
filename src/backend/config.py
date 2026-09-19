from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    vapi_api_key: str = ""
    openai_api_key: str = ""
    database_url: str = "postgresql+asyncpg://cimet_user:cimet_password@db:5432/cimet_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
