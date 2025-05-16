from pydantic_settings import BaseSettings
from typing import Optional

# evn dev live 
ENV = "dev"
class Settings(BaseSettings):
    if ENV == "dev":
        # API Configuration
        SEGMENTATION_API_URL: str = "http://27.152.58.86:51055/api/segmentation/base64"
        API_TIMEOUT: int = 60

        # File paths
        OUTPUT_DIR: str = "output-images"
        INPUT_DIR: str = "input-images"

    elif ENV == "live":
        SEGMENTATION_API_URL: str = "http://localhost:51055/api/segmentation/base64"
        API_TIMEOUT: int = 60

        # File paths
        OUTPUT_DIR: str = "x://sso/segment_images/output-images"
        INPUT_DIR: str = "x://sso/segment_images/input-images"
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()