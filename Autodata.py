import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# === 自動產生「前一天」的時間區間 ===
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
start_time = f"{yesterday} 00:00:00"
end_time = f"{yesterday} 23:59:59"
filename_tag = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

# === 登入 ===
session = requests.Session()
login_url = "https://backendserver.osmplay.com/auth/login"
login_payload = {
    "username": "qa002",
    "password": "888888"
}
headers = {
    "Content-Type": "application/json",
    "Origin": "https://backend.osmplay.com",
    "Referer": "https://backend.osmplay.com/",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*"
}

res = session.post(login_url, json=login_payload, headers=headers)
token = res.json()["data"]["token"]
headers["Authorization"] = f"Bearer {token}"

# === 動態取得總頁數 ===
def get_total_pages():
    test_params = {
        "dateTime[]": [start_time, end_time],
        "page": 1,
        "pageSize": 1,
        "channelId": 0,
        "isall": "true",
        "dateTimeType": 0,
        "playerstudioid": "np,igo,cf,dhs,mdr,live,bpo,ncl,tbp,wf,tbr,cp"
    }
    res = session.post("https://backendserver.osmplay.com/egm/reports/gameRecordList", headers=headers, params=test_params)
    data = res.json()
    total = data.get("data", {}).get("total", 0)
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    return pages

PAGE_SIZE = 1000
TOTAL_PAGES = get_total_pages()
max_retries = 3
base_url = "https://backendserver.osmplay.com/egm/reports/gameRecordList"

def fetch_page(page):
    local_session = requests.Session()
    local_session.headers.update(headers)
    params = {
        "dateTime[]": [start_time, end_time],
        "clientMachineName": "",
        "playerId": "",
        "playerName": "",
        "orderId": "",
        "page": page,
        "pageSize": PAGE_SIZE,
        "dateTimeType": 0,
        "playerstudioid": "np,igo,cf,dhs,mdr,live,bpo,ncl,tbp,wf,tbr,cp",
        "isall": "true",
        "channelId": 0
    }

    for attempt in range(max_retries):
        try:
            response = local_session.post(base_url, headers=headers, params=params, timeout=20)
            if response.status_code == 504:
                time.sleep(2)
                continue
            elif response.status_code != 200:
                return []
            data = response.json()
            items = data.get("data", {}).get("items", [])
            print(f"✅ 第 {page} 頁完成，筆數：{len(items)}")
            return items
        except:
            time.sleep(2)
    return []

# === 多線程抓取所有頁面 ===
all_data = []
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(fetch_page, page) for page in range(1, TOTAL_PAGES + 1)]
    for future in as_completed(futures):
        all_data.extend(future.result())

# 匯出
if all_data:
    df = pd.DataFrame(all_data)
    print("📋 欄位清單：", df.columns.tolist())

    # 確保篩選欄位存在並處理格式
    if "bet" in df.columns:
        df["bet"] = pd.to_numeric(df["bet"], errors="coerce")
    else:
        df["bet"] = 0

    abnormal_df = df[(~df["bet"].isin([8, 16, 24])) & (df["gameid"] == "dfdcmini")]

    df.to_excel(f"gameRecord_{filename_tag}.xlsx", index=False)
    abnormal_df.to_excel(f"異常紀錄_{filename_tag}.xlsx", index=False)
    print(f"✅ 匯出完成：gameRecord_{filename_tag}.xlsx")
    print(f"✅ 異常紀錄已輸出：異常紀錄_{filename_tag}.xlsx")
else:
    print("⚠️ 沒有抓到任何資料，不產出報表")