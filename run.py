# ./run.py
import uvicorn
from app import app

if __name__ == "__main__":
    # 配置啟動參數
    # host: "0.0.0.0" 允許外部訪問
    # port: 8000 預設埠號
    # reload: True 偵測程式碼變動後自動重啟（開發環境建議開啟）
    uvicorn.run(
        "run:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True
    )