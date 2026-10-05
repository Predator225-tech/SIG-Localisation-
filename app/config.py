from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sig_madagascar"
    db_user: str = "postgres"
    db_password: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        from urllib.parse import quote
        return f"postgresql://{quote(self.db_user)}:{quote(self.db_password)}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
