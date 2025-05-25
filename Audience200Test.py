from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# 設定多開選項
edge_options = Options()
edge_options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36")
edge_options.add_argument("--window-size=390,844")
edge_options.add_argument("--incognito") # 開啟無痕模式
prefs = {
    "profile.managed_default_content_settings.images": 2,  # 禁止圖片加載
    "profile.default_content_setting_values.notifications": 2,  # 禁止通知
}
edge_options.add_experimental_option("prefs", prefs)

drivers = []  # 存放所有 WebDriver

# 初始視窗位置
# start_x = -1000  # 初始 X 座標
# start_y = -1920  # 初始 Y 座標
# offset_x = 50    # 每個新視窗向右偏移的距離

# 讀取帳號列表
with open('accounts.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)

    # 計數器
    index = 0
    
    for row in csv_reader:
        account = row['account']
        print(f"帳號: {account}")

        # 啟動瀏覽器
        driver = webdriver.Edge(service=Service(r"C:\Users\Eric\Downloads\edgedriver_win64\msedgedriver.exe"), options=edge_options)
        driver.get("https://www.client8.me/home/")

        # 設定視窗位置，每次往右偏移 offset_x
        # driver.set_window_position(start_x + (index * offset_x), start_y)
        # index += 1  # 增加索引，讓下一個視窗往右偏移

        time.sleep(3)
        
        # 找到同意按鈕

        wait = WebDriverWait(driver,10)
        play_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.btn-accept")))
        play_button.click()

        time.sleep(1)
        
        # 找到遊戲開始按鈕
        play_button = driver.find_element(By.CLASS_NAME, "btn-white")  
        play_button.click()

        time.sleep(1)

        # 找到password切換
        play_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Password')]").click()

        time.sleep(1)

        # 輸入帳號
        phone_input = driver.find_element(By.XPATH, "(//input[@placeholder='Enter Phone Number'])[last()]")
        if phone_input.is_displayed():
            phone_input.send_keys(account)
            print(f"帳號: {account}")
        else:
            print("元素未顯示，可能需要滾動或等待")

        time.sleep(1)

        driver.find_element(By.XPATH, "//input[@placeholder='Enter Password']").send_keys("888888")

        time.sleep(1)

        # 同意書點擊
        btn = driver.find_element(By.XPATH, "//span[contains(@class, 'rmb-btn') and contains(@class, 'no-absolute')]")
        driver.execute_script("arguments[0].click();", btn)

        time.sleep(1)

        # 按登入
        # 等待並找到目標的 button 元素
        btn = WebDriverWait(driver, 10).until(
              EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'r-btn btn-big btn-color-2 no-margin-top')]"))
            )
        # 滾動到元素可見位置
        driver.execute_script("arguments[0].scrollIntoView();", btn)

        # 點擊按鈕
        btn.click()
        print(f"帳號 {account} 已登入")

        time.sleep(3)
    
        try:
            # 等待 close-btn 出現並可點擊
            close_button = WebDriverWait(driver, 10).until(
                           EC.element_to_be_clickable((By.XPATH, "//button[text()='Accept']"))
                           )
            # 點擊關閉按鈕
            close_button.click()
            print("已成功點擊 close-btn")

            time.sleep(1)
            # 等待 close-btn 出現並可點擊2
            close_button2 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "close-btn"))
                )
            # 點擊關閉按鈕
            close_button2.click()
            print("已成功點擊 close-btn")
            time.sleep(1)
        except Exception as e:
            # 如果 5 秒內找不到 close-btn，直接忽略並繼續執行
            print("未找到 close-btn，繼續執行其他操作")
    
        # 等待目標元素可點擊
        element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(@style, 'background-image: url(\"https://cp-images.client88.me/images/cp/h5nav/1307-1/games.svg\")')]")))
        # 點擊元素
        element.click()

        time.sleep(3)

        liveSlots = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/ul/li[3]')))
        liveSlots.click()

        time.sleep(3)

        # 等待該元素可點擊
        element1 = WebDriverWait(driver, 10).until(
           EC.element_to_be_clickable((By.XPATH, "//div[@data-v-125568d0]"))
        )
    
        # 點擊元素
        element1.click()
        print("已進入OSM")

        time.sleep(5)

        # 切換到 iframe
        WebDriverWait(driver, 10).until(
          EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe_id"))
        )
    
        # 找到所有 `grid_gm_item`
        items = WebDriverWait(driver, 10).until(
          EC.presence_of_all_elements_located((By.ID, "grid_gm_item"))
        )
    
        # 遍歷並點擊 "873-JJBXGOLD-1001"
        for item in items:
             if "873-JJBXGOLD-1001" in item.get_attribute("title"):
                   driver.execute_script("arguments[0].scrollIntoView();", item)  # 滾動到可視範圍
                   driver.execute_script("arguments[0].click();", item)  # 強制點擊
                   break  # 點擊後跳出迴圈

        time.sleep(3)

        # 存入 WebDriver 陣列
        drivers.append(driver)
        time.sleep(3)
        driver.quit()
        print(f"帳號 {account} 已完成")
    
    