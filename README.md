# X.com Audio Converter

一款基於 **Python + Tkinter + yt_dlp + FFmpeg** 的桌面應用程式，  
可將 X（前身為 Twitter）影片自動下載並轉換為MP4檔案。  
支援自定義輸出資料夾、即時下載進度顯示與錯誤提示。

---

## 功能特色
- 支援 X.com / Twitter 影片連結下載  
- 自動擷取最高音質音訊流  
- 可選輸出資料夾與檔案命名  
- 內建 GUI 介面（Tkinter）  
- 下載進度條與速度顯示  
- 打包成單一 EXE 檔（可離線執行）

---

## 安裝方式

### 下載專案
- 請至以下網址下載最新版本的壓縮檔
```bash
https://github.com/shawnhuang125/x.com_converter/releases/tag/V1.0.0
```


## 授權條款
本專案採用 MIT License。  

---

>  **作者註記：**
> 若要包成 EXE 發佈，可將 `cookies.json` 與 `ffmpeg.exe` 一併放入執行檔同層資料夾中，  
> 以確保下載功能正常運作。
