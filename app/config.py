from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_service_role_key: str
    openai_api_key: str
    eleven_labs_api_key: str = ""
    openrouter_api_key: str = ""
    fish_audio_api_key: str = ""
    jwt_audience: str = "authenticated"
    jwt_issuer: str = ""
    cors_origins: str = "*"

    # Admin panel auth
    admin_username: str = "admin"
    admin_password_hash: str = ""
    admin_jwt_secret: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
