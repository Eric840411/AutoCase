import cv2
import pytesseract
import numpy as np
import os
import re

# ✅ 設定 Tesseract 執行檔路徑（Windows 下需要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ 影片路徑
video_path = r"C:\Users\Eric\Desktop\TEST.mp4"

# ✅ 建立儲存資料夾
output_dir = r"C:\Users\Eric\Desktop\output_frames"
os.makedirs(output_dir, exist_ok=True)

# ✅ 讀取影片
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
interval = int(fps)  # 每秒擷取 1 幀

frame_idx = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    if frame_idx % interval == 0:
        # ----- 影像處理區 -----
        img = frame.copy()
        h, w = img.shape[:2]
        roi = img[int(h * 0.30):int(h * 0.90), :]
        roi = cv2.resize(roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(gray, 255, 
                               cv2.ADAPTIVE_THRESH_MEAN_C, 
                               cv2.THRESH_BINARY, 31, 10)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(binary)
        _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        h2, _ = binary.shape
        binary = binary[int(h2 * 0.4):, :]

        # ----- OCR -----
        text = pytesseract.image_to_string(binary, config='--oem 3 --psm 6')
        print(f"[Frame {frame_idx}] ---")
        print(text.strip())

        # 儲存畫面
        cv2.imwrite(os.path.join(output_dir, f"frame_{frame_idx}.png"), binary)
        print(f"已儲存畫面")

    frame_idx += 1

cap.release()
