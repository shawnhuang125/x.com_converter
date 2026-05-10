import os
import json
import platform
import sys
import shutil
from app.app_logger import logger

# 1. 取得核心目錄的邏輯
def get_base_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包後的 .app 或 .exe，檔案會被解壓到這個暫存目錄
        return sys._MEIPASS
    # 開發環境下，回傳 app.py 所在的根目錄
    # 假設此檔案在 utils/ 內，所以要取兩次 dirname
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# 修正後的 load_config 邏輯
def load_config():
    # 1. 預設值，不要讓 key 消失
    config = {
        "language": "en",
        "ffmpeg_binary": None,
        "ffmpeg_path": ""
    }
    
    # 2. 讀取設定檔 (建議改到用戶家目錄，避免唯讀問題)
    # home_config = os.path.join(os.path.expanduser("~"), ".comma_config.json")
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception:
            pass

    # 3. 【最重要的修正】強制重新偵測暫存區的 FFmpeg
    # 不管 config.json 裡面寫什麼，這一步都要執行
    base = get_base_path()
    current_os = platform.system()
    ffmpeg_name = "ffmpeg" if current_os == "Darwin" else "ffmpeg.exe"
    full_path = os.path.join(base, ffmpeg_name)
    
    if os.path.exists(full_path):
        # 覆蓋掉那個空的 ffmpeg_path，確保主程式抓到絕對路徑
        config["ffmpeg_binary"] = full_path
        config["ffmpeg_path"] = base # 讓舊邏輯也能抓到資料夾
        if current_os == "Darwin":
            os.chmod(full_path, 0o755)

        logger.info(f"FFmpeg detected in project bundle: {full_path}")
    else:
        # 找不到的話，最後嘗試抓系統環境變數裡的
        system_ffmpeg = shutil.which("ffmpeg")
        config["ffmpeg_binary"] = system_ffmpeg
        
        if system_ffmpeg:
            logger.info(f"FFmpeg detected from system PATH: {system_ffmpeg}")
        else:
            logger.error("FFmpeg not found in project bundle or system PATH!")
        
    return config

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Configuration successfully saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save config to {CONFIG_FILE}: {str(e)}", exc_info=True)