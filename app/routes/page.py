import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# 取得 app 目錄絕對路徑 (從 app/routes/ 往上跳一級)
APP_DIR = Path(__file__).resolve().parent.parent

# 指向 app/templates
TEMPLATE_DIR = APP_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"title": "Comma - Media Downloader"}
    )

# partials/頁面路由

@router.get("/page/welcome", response_class=HTMLResponse)
async def welcome_page(request: Request):
    # 這裡會去 templates/partials/welcome.html 找檔案
    return templates.TemplateResponse(request=request, name="partials/welcome.html")

@router.get("/page/downloader", response_class=HTMLResponse)
async def downloader_page(request: Request):
    # 這裡會去 templates/partials/downloader.html 找檔案
    return templates.TemplateResponse(request=request, name="partials/downloader.html")