# 使用官方輕量版 Python
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數：防止 Python 產生 .pyc 檔，並讓輸出直接顯示在日誌中
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安裝系統依賴 (FFmpeg 是媒體轉換的核心)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 先複製 requirements.txt 以利用 Docker 快取機制
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製其餘專案內容
COPY . .

# 開放 FastAPI 預設通訊埠
EXPOSE 8011

# 啟動指令 (指向你的 app.main)
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8011"]