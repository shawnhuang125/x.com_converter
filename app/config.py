import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# 取得專案根目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # --- 伺服器配置 ---
    APP_NAME: str = "Comma-Media-Converter"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8011

    # --- 路徑配置 ---
    # 這裡讓你可以透過 .env 指定 ffmpeg 絕對路徑，若沒給則預設由系統尋找
    FFMPEG_BINARY_PATH: str = "ffmpeg" 
    
    # 目錄配置
    STATIC_DIR: str = str(BASE_DIR / "app" / "source")
    TEMPLATE_DIR: str = str(BASE_DIR / "app" / "templates")
    DOWNLOAD_DIR: str = str(BASE_DIR / "downloads")

    # 讀取 .env 檔案
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# 實例化設定物件
settings = Settings()

# 確保下載目錄存在
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)