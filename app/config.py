from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_service_role_key: str
    openai_api_key: str
    eleven_labs_api_key: str = ""
    jwt_audience: str = "authenticated"
    jwt_issuer: str = ""
    cors_origins: str = "*"

    model_config = {"env_file": ".env"}


settings = Settings()
