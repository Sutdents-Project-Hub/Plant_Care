from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 30

    cors_allow_origins: str = "*"

    ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    app_name: str = "Plant Care"
    email_backend: str = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_from_name: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_timeout_seconds: int = 10

    expose_api_docs: bool = False
    public_rate_limit_enabled: bool = True
    public_rate_limit_requests: int = 30
    public_rate_limit_window_seconds: int = 60
    public_rate_limit_paths: str = (
        "/api/v1/auth/register,"
        "/api/v1/auth/login,"
        "/api/v1/auth/refresh,"
        "/api/v1/auth/found_psw,"
        "/api/v1/ai/generate_tasks,"
        "/api/v1/homepage/search_announcements"
    )

    def cors_origins(self) -> list[str]:
        v = (self.cors_allow_origins or "").strip()
        if not v:
            return []
        if v == "*":
            return ["*"]
        return [p.strip() for p in v.split(",") if p.strip()]

    def rate_limit_paths_list(self) -> list[str]:
        v = (self.public_rate_limit_paths or "").strip()
        if not v:
            return []
        return [p.strip() for p in v.split(",") if p.strip()]


settings = Settings()  # type: ignore[call-arg]
