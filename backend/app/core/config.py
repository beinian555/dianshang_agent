from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    store_backend: str = "memory"
    database_url: str = ""

    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_timeout: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
