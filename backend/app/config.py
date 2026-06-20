from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "DataInsight AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./data/datainsight.db"

    # 文件上传
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Moonshot AI API
    MOONSHOT_API_KEY: str = ""
    MOONSHOT_BASE_URL: str = "https://api.moonshot.cn/v1"
    MOONSHOT_MODEL: str = "moonshot-v1-8k"

    class Config:
        env_file = ".env"


settings = Settings()
