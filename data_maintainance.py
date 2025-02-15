import pandas as pd
import time
import threading
from datetime import datetime

# 初始化数据列
data_columns = ["meter_id", "time", "reading"]

# 尝试读取 `local_db.csv`，如果不存在，则创建一个空的 DataFrame
try:
    local_db = pd.read_csv("local_db.csv")
except FileNotFoundError:
    local_db = pd.DataFrame(columns=data_columns)
    local_db.to_csv("local_db.csv", index=False)

# 临时存储 `data_store`，用于存放当天的 `meter_reading`
data_store = pd.DataFrame(columns=data_columns)

# **加载本地数据库数据**
def load_local_db():
    global data_store
    try:
        data_store = pd.read_csv("local_db.csv")
        print("Local DB loaded successfully.")
    except FileNotFoundError:
        print(" No existing local DB found, starting fresh.")
        data_store = pd.DataFrame(columns=data_columns)

# **将 `data_store` 数据存入 `local_db.csv`**
def save_data_to_csv():
    global data_store, local_db

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f" [{timestamp}] Saving data to local_db.csv...")

    try:
        # 读取 `local_db.csv`
        local_db = pd.read_csv("local_db.csv")

        # **合并 `data_store` 到 `local_db`**
        combined_db = pd.concat([local_db, data_store], ignore_index=True)

        # **写入 CSV**
        combined_db.to_csv("local_db.csv", index=False)
        print(f" Data saved successfully! Total records: {len(combined_db)}")

        # **清空 `data_store`**
        data_store = pd.DataFrame(columns=data_columns)
        print("Temporary data cleared.")

    except Exception as e:
        print(f"Error saving data: {e}")

# **定期检查是否到凌晨 00:00 - 00:59 进行数据维护**
def maintenance_scheduler():
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        # 检查是否在 00:00 - 00:59 之间
        if "00:00" <= current_time <= "00:59":
            print("Midnight maintenance started...")
            save_data_to_csv()
            time.sleep(60)  # 每分钟执行一次，确保在 00:59 前多次存储数据

        time.sleep(10)  # 每 10 秒检查一次当前时间

# **使用 `threading` 启动后台数据维护任务**
def start_maintenance_thread():
    maintenance_thread = threading.Thread(target=maintenance_scheduler, daemon=True)
    maintenance_thread.start()
    print("Data maintenance thread started.")

if __name__ == "__main__":
    load_local_db()
    start_maintenance_thread()

    # **让主线程保持运行**
    while True:
        time.sleep(3600)
