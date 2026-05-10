import uvicorn
import os
import sys
# 從你剛才定義的 app/__init__.py 導入 settings (或原本的路徑)
from app.config import settings 

# 確保根目錄在路徑中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # 關鍵修正：因為 app 就在 app/__init__.py 裡
    # 所以路徑是 "app:app" 而不是 "app.main:app"
    uvicorn.run(
        "app:app", 
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG 
    )