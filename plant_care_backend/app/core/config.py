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

    def cors_origins(self) -> list[str]:
        v = (self.cors_allow_origins or "").strip()
        if not v:
            return []
        if v == "*":
            return ["*"]
        return [p.strip() for p in v.split(",") if p.strip()]


settings = Settings()  # type: ignore[call-arg]
