#可以运行但会记录两次
import pandas as pd
import time
import threading
from datetime import datetime
datetime.now().strftime("%H:%M")
import pandas as pd
import os
# 定义数据格式

data_columns = ["meter_id", "time", "reading"]


current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前Python文件的目录
LOCAL_DB_FILE = os.path.join(current_dir, "local_db.csv")
DAILY_USAGE_FILE = os.path.join(current_dir, "daily_usage.csv")

# 加载 `local_db.csv`
def load_data_store():
    try:
        return pd.read_csv(LOCAL_DB_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=data_columns)

# 计算当天总用电量
def calculate_daily_usage(data_store):
    if data_store.empty:
        print("No data available for daily usage calculation.")
        return

    data_store["time"] = pd.to_datetime(data_store["time"])
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 获取今天的最新一条数据
    today_data = data_store[data_store["time"].dt.strftime("%Y-%m-%d") == today_str]
    if today_data.empty:
        print("No records found for today.")
        return
    latest_today = today_data.sort_values("time").groupby("meter_id").last().reset_index()

    # 仅保留 `meter_id`、`date`、`reading`
    latest_today = latest_today[["meter_id", "time", "reading"]]
    latest_today.rename(columns={"time": "date"}, inplace=True)

    try:
        daily_db = pd.read_csv(DAILY_USAGE_FILE)
    except FileNotFoundError:
        daily_db = pd.DataFrame(columns=["meter_id", "date", "reading"])

    # 先删除今天的旧记录，再追加新记录
    daily_db = daily_db[daily_db["date"] != today_str]
    daily_db = pd.concat([daily_db, latest_today], ignore_index=True)
    daily_db.to_csv(DAILY_USAGE_FILE, index=False)

    print(f" Daily latest reading saved for {today_str}")


# 归档 `data_store` 数据
def archive_data():
    data_store = load_data_store()
    if data_store.empty:
        print(" No unarchived data found.")
        return

    try:
        # 计算日用电量
        calculate_daily_usage(data_store)

        # 仅清空 data_store，不清空 local_db.csv
        print(" Data store cleared after archiving.")

    except Exception as e:
        print(f" Error archiving data: {e}")

# 开机时检查是否有未归档数据，并执行归档
def check_and_archive_on_startup():
    data_store = load_data_store()
    
    if not data_store.empty:
        print(" Startup check: Unarchived data found. Archiving now...")
        archive_data()
    else:
        print(" Startup check: No unarchived data found.")

# 每天 00:00 - 00:59 进行数据归档
def maintenance_scheduler():
    while True:
        #current_time = "01:00"
        current_time = datetime.now().strftime("%H:%M")
        if "00:00" <= current_time <= "00:59":
            print(" Midnight maintenance started...")
            archive_data()
            time.sleep(60)

        time.sleep(10)

# 启动线程
def start_maintenance_thread():
    maintenance_thread = threading.Thread(target=maintenance_scheduler, daemon=True)
    maintenance_thread.start()
    print(" Data maintenance thread started.")

#  系统维护时间+开机后可检查并归档
if __name__ == "__main__":
    print(" System startup: Checking for unarchived data...")
    check_and_archive_on_startup()  
    
    start_maintenance_thread()

    while True:
        time.sleep(3600)