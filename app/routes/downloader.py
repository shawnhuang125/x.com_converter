import os
import tempfile
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
import yt_dlp

from app.services.downloader_service import DownloaderService

downloader_router = APIRouter()
TEMP_DIR = os.path.join(tempfile.gettempdir(), "comma_web_downloads")
os.makedirs(TEMP_DIR, exist_ok=True)

@downloader_router.get("/fetch/{filename}")
async def fetch_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    return {"error": "File not found"}

@downloader_router.websocket("/ws/download")
async def websocket_downloader(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action") 
            raw_url = data.get("url", "")
            # 統一清理網址
            url = raw_url.split('&list=')[0] if raw_url else ""

            if action == "get_meta":
                def fetch_meta():
                    try:
                        resolutions = DownloaderService.get_resolutions(url)
                        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                            info = ydl.extract_info(url, download=False)
                            thumb = info.get("thumbnail") or (info.get("thumbnails")[-1]["url"] if info.get("thumbnails") else "")
                            
                            asyncio.run_coroutine_threadsafe(
                                websocket.send_json({
                                    "type": "meta_and_res",
                                    "title": info.get("title"),
                                    "uploader": info.get("uploader"),
                                    "thumb": thumb,
                                    "duration": info.get("duration"),
                                    "resolutions": resolutions 
                                }), loop
                            )
                    except Exception as e:
                        asyncio.run_coroutine_threadsafe(websocket.send_json({"type": "error", "msg": str(e)}), loop)

                await run_in_threadpool(fetch_meta)

            elif action == "start_download":
                # 關鍵修正：將變數鎖定在當前 action 作用域
                selected_res = data.get("resolution")
                as_mp3 = data.get("as_mp3", False)

                # 使用預設參數值來鎖定閉包變數，解決截圖中的 UnboundLocalError
                def start_task(res=selected_res, is_mp3=as_mp3, target_url=url):
                    try:
                        hook = DownloaderService.create_progress_hook(websocket, loop)
                        # 確保傳入 Service 的是清理過的網址與正確的模式
                        ydl_opts = DownloaderService.get_ydl_opts(target_url, is_mp3, TEMP_DIR, hook, res)

                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(target_url, download=True)
                            full_path = ydl.prepare_filename(info)
                            
                            if is_mp3:
                                full_path = os.path.splitext(full_path)[0] + ".mp3"
                            
                            pure_filename = os.path.basename(full_path)
                            asyncio.run_coroutine_threadsafe(
                                websocket.send_json({
                                    "type": "done",
                                    "filename": pure_filename,
                                    "download_url": f"/fetch/{pure_filename}"
                                }), loop
                            )
                    except Exception as e:
                        asyncio.run_coroutine_threadsafe(
                            websocket.send_json({"type": "error", "msg": str(e)}), loop
                        )

                # 確保 start_task 的執行是在 elif 區塊內觸發
                await run_in_threadpool(start_task)

    except WebSocketDisconnect:
        pass