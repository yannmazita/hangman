from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    origins: list[str]
    app_host: str
    app_port: int | str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str | int
    postgres_echo: bool
    postgres_pool_size: int


settings = Settings()  # type: ignore
