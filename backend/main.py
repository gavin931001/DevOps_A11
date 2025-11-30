from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import time
import random
import logging

# 1. 初始化 App
app = FastAPI()

# 2. 設定 CORS (解決跨網域問題)
# 允許 GitHub Pages 的前端呼叫這個後端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 為了作業方便，我們先允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 設定 Logging (Task 1: Logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sre-demo")

# 4. 設定 Metrics (Task 1: Metrics)
# 這行會自動產生 /metrics 頁面，提供真實的 Request Rate, Latency, Error Rate
Instrumentator().instrument(app).expose(app)

# 模擬資料庫 (存在記憶體中)
db = []

# Chaos 開關 (Task 3: Chaos Engineering)
CHAOS_MODE = True

# 定義資料格式
class Registration(BaseModel):
    email: str
    version: str

@app.get("/")
def health_check():
    return {"status": "ok", "service": "registration-backend"}

@app.post("/register")
def register(data: Registration):
    global CHAOS_MODE
    
    # [Task 3] Chaos Engineering: 模擬隨機失敗或延遲
    if CHAOS_MODE:
        # 30% 機率直接報錯 (500 Internal Server Error)
        if random.random() < 0.3: 
            logger.error(f"Chaos Error triggered for {data.email}")
            raise HTTPException(status_code=500, detail="Chaos Monkey struck!")
        # 50% 機率延遲 2 秒 (模擬網路塞車)
        if random.random() < 0.5: 
            time.sleep(2)
            logger.warning(f"Chaos Latency triggered for {data.email}")
    
    # 正常邏輯
    logger.info(f"New registration: {data.email} using {data.version}")
    db.append(data)
    return {"message": "Success", "id": len(db), "chaos": CHAOS_MODE}

# [Task 3] 控制 Chaos 的開關 API
# 呼叫 /chaos/on 開啟破壞模式
# 呼叫 /chaos/off 關閉破壞模式
@app.post("/chaos/{state}")
def set_chaos(state: str):
    global CHAOS_MODE
    if state == "on":
        CHAOS_MODE = True
        logger.warning("!!! CHAOS MODE ENABLED !!!")
    else:
        CHAOS_MODE = False
        logger.info("Chaos mode disabled")
    return {"chaos_mode": CHAOS_MODE}

# [Task 1] 簡單的 Dashboard 資料介面
@app.get("/stats")
def get_stats():
    return {
        "total_registrations": len(db),
        "chaos_mode": CHAOS_MODE
    }
