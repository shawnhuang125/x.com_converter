from fastapi import APIRouter
from .page import router as page_router
from .downloader import downloader_router

# 建立總路由實例
api_router = APIRouter()

# 註冊頁面路由 (可以根據需求加上 prefix)
api_router.include_router(page_router, tags=["Pages"])
api_router.include_router(downloader_router, tags=["downloader_router"])

# 未來如果你有下載影片的 API，可以這樣加：
# from .downloader import router as download_router
# api_router.include_router(download_router, prefix="/api/v1", tags=["API"])