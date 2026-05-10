from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes import api_router
from .app_logger import logger

app = FastAPI(title="Comma Media Downloader")

# 取得 app 目錄絕對路徑 (即截圖中顯示的 app 資料夾位置)
APP_DIR = Path(__file__).resolve().parent

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Comma 服務啟動中...")
    logger.info(f"📁 靜態資源目錄: {APP_DIR / 'source'}")
    logger.info(f"📁 模板目錄: {APP_DIR / 'templates'}")


app.mount(
    "/app/templates/partials", 
    StaticFiles(directory=str(APP_DIR / "templates" / "partials")), 
    name="partials"
)
# 掛載靜態檔案：對應 app/source
# 這樣你在 HTML 中引用路徑為 /app/source/css/global.css
app.mount(
    "/app/source", 
    StaticFiles(directory=str(APP_DIR / "source")), 
    name="source"
)

app.include_router(api_router)