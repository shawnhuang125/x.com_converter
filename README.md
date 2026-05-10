# Universal Media Downloader (多平台影音下載器)

一款基於 **Python + Tkinter + yt_dlp + FFmpeg** 的全能桌面下載工具。
不僅支援 X（前身為 Twitter），還能下載 YouTube 等多種影音平台的影片，並自動合併為高品質 MP4 檔案。
具備現代化的 GUI 介面、即時進度顯示，以及智慧型檔案管理功能。

---

## 功能特色

* **多平台支援**：不只 X.com (Twitter)，也能下載 **YouTube**、Instagram、Twitch 等 `yt-dlp` 支援的數千個網站。
* **高品質影音**：自動抓取最佳畫質與音質，並透過內建的 FFmpeg 自動合併轉換為 MP4。
* **智慧檔案處理**：
    * 遇到重複檔名時，會跳出對話框詢問（可選擇 **重新命名**、**覆寫** 或 **取消**）。
    * 支援自定義檔案後綴（Suffix），輕鬆管理同名影片。
* **可攜式設計**：
    * **內建 FFmpeg**：使用者無需手動安裝或設定環境變數，下載即用。
    * **單一 EXE 檔**：打包成單一執行檔，隨身攜帶，離線可用。
* **現代化介面**：
    * 支援淺色/深色主題切換 (Dark Mode)。
    * 即時顯示下載進度條、速度與剩餘時間。
    * 下載前自動預覽影片縮圖與資訊。

---

## 安裝與使用方式

### 1. 下載程式
- 請至 Releases 頁面下載最新版本的docker：https://github.com/shawnhuang125/Comma/releases/tag/v1.0.6


### 2. 安裝ffmpeg
- Mac用戶
```
# 開啟終端機執行
brew install ffmpeg
```
- 驗證安裝
```
which ffmpeg
```
- Windows用戶
- Windows 沒有內建的套件管理，建議手動下載並手動指定路徑。

- 下載：前往 `Gyan.dev` 下載 `ffmpeg-git-full.7z`。

- 解壓縮：將裡面的 bin 資料夾內容（`ffmpeg.exe`, `ffplay.exe`, `ffprobe.exe`）解壓到你的專案根目錄，或是配置如下:

```
C:\ffmpeg\bin 
```

- 設定環境變數：

- 將 bin 的路徑加入系統的 Path。

- 或者直接在你的 `.env` 裡面寫死路徑：

- 程式碼片段
```
FFMPEG_BINARY_PATH=C:\ffmpeg\bin\ffmpeg.exe
```
### 3. 配置.env
- 將以下寫入`.env`
- 各項參數均可調整

```
# --- 伺服器配置 (Server Settings) ---
APP_NAME="Comma-Media-Converter"
DEBUG=True
HOST=0.0.0.0
PORT=8011

# --- FFmpeg 配置 (Media Tools) ---
# 在 Mac mini 本機開發時，請取消下面這行的註解並指向你的 Homebrew 路徑
FFMPEG_BINARY_PATH=/opt/homebrew/bin/ffmpeg

# 如果是在 Docker 容器中執行，請註解掉上方路徑，或是改為容器內的標準路徑
# FFMPEG_BINARY_PATH=/usr/bin/ffmpeg

# --- 日誌配置 (Logging) ---
LOG_LEVEL=INFO
```

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.