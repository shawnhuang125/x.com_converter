import os
import re
import yt_dlp
import asyncio
from app.utils.config_manager import load_config

config_data = load_config()

class DownloaderService:
    @staticmethod
    def create_progress_hook(websocket, loop):
        def hook(d):
            if d['status'] == 'downloading':
                # 強力過濾 ANSI 顏色代碼與非數字字元
                p_raw = d.get("_percent_str", "0%")
                p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw)
                p_numeric = re.sub(r'[^0-9.]', '', p_clean)
                try:
                    percent = float(p_numeric) if p_numeric else 0.0
                    if percent > 100: percent = 100.0
                except:
                    percent = 0.0
                
                speed = re.sub(r'\x1b\[[0-9;]*m', '', d.get("_speed_str", "N/A")).strip()
                eta = re.sub(r'\x1b\[[0-9;]*m', '', d.get("_eta_str", "N/A")).strip()
                
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "progress",
                        "percent": percent,
                        "speed": speed,
                        "eta": eta
                    }), loop
                )
        return hook
    
    @staticmethod
    def get_resolutions(url):
        """抓取 YouTube 影片高於 720p 的解析度清單"""
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'nocheckcertificate': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # 過濾出有影片流的格式，並提取解析度 (高度)
            # 使用 set 確保不重複，且只保留 >= 720 的數值
            res_set = set()
            for f in formats:
                height = f.get('height')
                if height and height >= 720:
                    res_set.add(height)
            
            # 由高到低排序輸出，例如 [2160, 1440, 1080, 720]
            return sorted(list(res_set), reverse=True)

    @staticmethod
    def get_ydl_opts(url, as_mp3, temp_dir, progress_hook, selected_res=None):
        ffmpeg_dir = config_data.get("ffmpeg_bin_dir")
        
        if ffmpeg_dir:
            base_opts["ffmpeg_location"] = ffmpeg_dir

        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

        # 基礎配置
        base_opts = {
            "ffmpeg_location": ffmpeg_dir,
            "progress_hooks": [progress_hook],
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
            "concurrent_fragment_downloads": 8,
            "nocheckcertificate": True,
            "headers": browser_headers,
        }

        is_youtube = "youtube.com" in url or "youtu.be" in url
        
        if as_mp3:
            return {**base_opts, **{
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }, {"key": "FFmpegMetadata"}],
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}} if is_youtube else {},
            }}
        elif is_youtube:
            if selected_res:
                # 這裡最關鍵：指定使用者選擇的解析度，並確保合併音軌
                format_str = f"bestvideo[height={selected_res}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height={selected_res}]+bestaudio/best"
            else:
                # 預設最佳
                format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

            return {**base_opts, **{
                "format": format_str,
                "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
                "postprocessor_args": {"video_convertor": ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac"]},
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            }}
        else:
            return {**base_opts, **{
                "format": "bestvideo+bestaudio/best",
                "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
                "postprocessor_args": {"video_convertor": ["-c", "copy", "-map", "0", "-movflags", "faststart"]},
            }}