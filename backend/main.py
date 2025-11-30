# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from prometheus_fastapi_instrumentator import Instrumentator
# import time
# import random
# import logging
# import psutil # <--- 新增這行
# import os     # <--- 新增這行
# import math

# # 1. 初始化 App
# app = FastAPI()

# # 2. 設定 CORS (解決跨網域問題)
# # 允許 GitHub Pages 的前端呼叫這個後端
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 為了作業方便，我們先允許所有來源
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 3. 設定 Logging (Task 1: Logs)
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("sre-demo")

# # 4. 設定 Metrics (Task 1: Metrics)
# # 這行會自動產生 /metrics 頁面，提供真實的 Request Rate, Latency, Error Rate
# Instrumentator().instrument(app).expose(app)

# # 模擬資料庫 (存在記憶體中)
# db = []

# # Chaos 開關 (Task 3: Chaos Engineering)
# CHAOS_MODE = False
# STRESS_MODE = False  # 新增這個：用來標記是否正在燒機

# # 定義資料格式
# class Registration(BaseModel):
#     email: str
#     version: str

# @app.get("/")
# def health_check():
#     return {"status": "ok", "service": "registration-backend"}

# @app.post("/register")
# def register(data: Registration):
#     global CHAOS_MODE
    
#     # [Task 3] Chaos Engineering: 模擬隨機失敗或延遲
#     if CHAOS_MODE:
#         # 30% 機率直接報錯 (500 Internal Server Error)
#         if random.random() < 0.3: 
#             logger.error(f"Chaos Error triggered for {data.email}")
#             raise HTTPException(status_code=500, detail="Chaos Monkey struck!")
#         # 50% 機率延遲 2 秒 (模擬網路塞車)
#         if random.random() < 0.5: 
#             time.sleep(2)
#             logger.warning(f"Chaos Latency triggered for {data.email}")
    
#     # 正常邏輯
#     logger.info(f"New registration: {data.email} using {data.version}")
#     db.append(data)
#     return {"message": "Success", "id": len(db), "chaos": CHAOS_MODE}

# # [Task 3] 控制 Chaos 的開關 API
# # 呼叫 /chaos/on 開啟破壞模式
# # 呼叫 /chaos/off 關閉破壞模式
# @app.post("/chaos/{state}")
# def set_chaos(state: str):
#     global CHAOS_MODE
#     if state == "on":
#         CHAOS_MODE = True
#         logger.warning("!!! CHAOS MODE ENABLED !!!")
#     else:
#         CHAOS_MODE = False
#         logger.info("Chaos mode disabled")
#     return {"chaos_mode": CHAOS_MODE}

# # # [Task 1] 簡單的 Dashboard 資料介面
# # @app.get("/stats")
# # def get_stats():
# #     return {
# #         "total_registrations": len(db),
# #         "chaos_mode": CHAOS_MODE
# #     }

# # [Task 1] 進階儀表板資料介面 (包含系統資源監控)
# @app.get("/stats")
# def get_stats():
#     # 1. 嘗試抓取真實數據
#     # interval=0.5 代表「現在立刻花 0.5 秒測量 CPU」。
#     # 這會讓 API 變慢一點點，但數據會準確非常多。
#     process = psutil.Process(os.getpid())
#     real_cpu = process.cpu_percent(interval=0.5)
    
#     memory_usage_mb = process.memory_info().rss / 1024 / 1024

#     # 2. [作業專用] 保底邏輯 (Simulation Logic)
#     # 如果系統正在燒機 (STRESS_MODE=True)，但抓到的數值卻很低 (<5%)，
#     # 代表 Render 環境把數值吃掉了。這時候我們手動修正為 80%~100%。
#     final_cpu = real_cpu
#     if STRESS_MODE and real_cpu < 50:
#         logger.warning("CPU metric drift detected, adjusting for dashboard...")
#         final_cpu = random.uniform(80, 100)  # 隨機產生 80~100 的數字
        
#     return {
#         "total_registrations": len(db),
#         "chaos_mode": CHAOS_MODE,
#         "stress_mode": STRESS_MODE, # 讓前端也可以知道狀態
#         "system_metrics": {
#             "cpu_percent": round(final_cpu, 2),
#             "memory_mb": round(memory_usage_mb, 2)
#         }
#     }

# # 新增這個 API: 讓 CPU 故意運算 n 秒
# @app.post("/stress/{seconds}")
# def stress_cpu(seconds: int):
#     global STRESS_MODE
#     STRESS_MODE = True  # 🔴 開始燒機前，把旗標立起來
    
#     end_time = time.time() + seconds
    
#     # 進行大量的數學運算
#     try:
#         while time.time() < end_time:
#             math.sqrt(random.randint(1, 10000)) 
#     finally:
#         STRESS_MODE = False  # 🔴 時間到或報錯後，一定要把旗標降下來
        
#     return {"message": f"CPU burned for {seconds} seconds"}

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
import time
import random
import logging
import math
import threading  # 🟢 新增這個：多執行緒模組
import psutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sre-demo")

Instrumentator().instrument(app).expose(app)

db = []
CHAOS_MODE = False
STRESS_MODE = False # 標記是否正在燒機

class Registration(BaseModel):
    email: str
    version: str

# 🟢 定義一個專門在後台燒 CPU 的函式
def cpu_burner(duration: int):
    global STRESS_MODE
    STRESS_MODE = True
    logger.warning(f"🔥🔥🔥 CPU STRESS STARTED for {duration} seconds 🔥🔥🔥")
    
    end_time = time.time() + duration
    
    # 這裡用 while 迴圈死命算數學
    # 因為是在子執行緒跑，所以不會卡死主程式
    while time.time() < end_time:
        # 做一些無意義的複雜運算
        [math.sqrt(random.randint(1, 10000)) for _ in range(100)]
    
    STRESS_MODE = False
    logger.warning("✅ CPU STRESS FINISHED")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "registration-backend"}

@app.post("/register")
def register(data: Registration):
    global CHAOS_MODE
    if CHAOS_MODE:
        if random.random() < 0.3: 
            logger.error(f"Chaos Error triggered for {data.email}")
            raise HTTPException(status_code=500, detail="Chaos Monkey struck!")
        if random.random() < 0.5: 
            time.sleep(2)
    
    logger.info(f"New registration: {data.email}")
    db.append(data)
    return {"message": "Success", "id": len(db), "chaos": CHAOS_MODE}

@app.post("/chaos/{state}")
def set_chaos(state: str):
    global CHAOS_MODE
    if state == "on":
        CHAOS_MODE = True
    else:
        CHAOS_MODE = False
    return {"chaos_mode": CHAOS_MODE}

# 🟢 修改後的燒機 API：使用 BackgroundTasks 或 Threading
@app.post("/stress/{seconds}")
def stress_cpu(seconds: int):
    # 啟動一個新的執行緒去跑 cpu_burner
    # 這樣主程式就可以立刻回傳 Response，不會被卡住
    t = threading.Thread(target=cpu_burner, args=(seconds,))
    t.start()
    
    return {"message": f"CPU stress test started for {seconds} seconds (Background Thread)"}

@app.get("/stats")
def get_stats():
    # 1. 抓取真實數據
    process = psutil.Process(os.getpid())
    
    # interval=None (非阻塞) 或極短時間，避免 API 變慢
    # 因為現在真的有 Thread 在跑，隨便抓應該都有數字
    real_cpu = process.cpu_percent(interval=0.1)
    
    memory_usage_mb = process.memory_info().rss / 1024 / 1024

    
    return {
        "total_registrations": len(db),
        "chaos_mode": CHAOS_MODE,
        "stress_mode": STRESS_MODE,
        "system_metrics": {
            # 這裡回傳的，保證是 psutil 抓到的真實數據
            "cpu_percent": round(real_cpu, 2),
            "memory_mb": round(memory_usage_mb, 2)
        }
    }
