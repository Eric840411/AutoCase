# OCR 模組：從多個影片中擷取每一幀畫面並辨識錯誤畫面（不依賴 pandas）
import cv2
import pytesseract
import numpy as np
import os
import re

# 設定 Tesseract 執行檔路徑（視系統調整）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 錯誤類型關鍵字定義
ERROR_TYPES = {
    "SAS Error": ["Broadcast", "SAS"],
    "Jackpot Handpay": ["Handpay", "Call", "Attendant", "Jack", "pot"],
    "Amount Notice": ["₱"],
}

def classify_text(text):
    for label, keywords in ERROR_TYPES.items():
        if any(k in text for k in keywords):
            return label
    return "Unknown"

def process_frame(frame):
    img = frame.copy()
    h, w = img.shape[:2]
    y1 = int(h * 0.60); y2 = int(h * 0.85)
    x1 = int(w * 0.30); x2 = int(w * 0.70)
    roi = frame[y1:y2, x1:x2].copy()

    roi = cv2.resize(roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # binary = cv2.bitwise_not(binary)

    # 裁掉上部干擾，保留下半區文字
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

    h2, w2 = binary.shape
    start = int(h2 * 0.25)
    binary = binary[start:, :]    
    return binary

def extract_info_from_frame(binary):
    text = pytesseract.image_to_string(binary, config='--oem 3 --psm 6')
    text_clean = text.strip()
    amounts = re.findall(r"[₱$]?[0-9,]+(?:\.[0-9]{2})?", text_clean)
    category = classify_text(text_clean)
    return text_clean, amounts, category

def process_video(video_path, output_dir, interval_frames=20):
    cap = cv2.VideoCapture(video_path)
    os.makedirs(output_dir, exist_ok=True)

    frame_idx = 0
    results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 只處理每1幀一次
        if frame_idx % interval_frames == 0:
            binary = process_frame(frame)
            text, amounts, category = extract_info_from_frame(binary)

            base_name = os.path.splitext(os.path.basename(video_path))[0]
            img_filename = f"{base_name}_frame_{frame_idx}.png"
            txt_filename = f"{base_name}_frame_{frame_idx}.txt"
            # 儲存圖片
            cv2.imwrite(os.path.join(output_dir, img_filename), binary)
            # 儲存文字結果
            with open(os.path.join(output_dir, txt_filename), 'w', encoding='utf-8') as f:
                f.write(text)
            results.append({
                "video": os.path.basename(video_path),
                "frame": frame_idx,
                "text": text,
                "amounts": ";".join(amounts),
                "category": category,
                "image": img_filename,
                "text_file": txt_filename
            })

        frame_idx += 1

    cap.release()
    return results

def process_multiple_videos(video_folder, output_dir):
    all_results = []
    for fname in os.listdir(video_folder):
        if fname.lower().endswith(('.mp4', '.avi', '.mov')):
            video_path = os.path.join(video_folder, fname)
            print(f"\n▶ 處理影片：{fname}")
            video_results = process_video(video_path, output_dir)
            all_results.extend(video_results)
    return all_results

# 主程式：批次處理資料夾中的多個影片
if __name__ == "__main__":
    video_folder = r"C:\\Users\\Eric\\Desktop\\videos"
    output_dir = r"C:\\Users\\Eric\\Desktop\\output_frames"
    results = process_multiple_videos(video_folder, output_dir)
    print(f"\n✅ 總共處理畫格： {len(results)}")
    # 計算成功辨識(非 Unknown)的結果數量
    success_count = sum(1 for r in results if r['category'] != "Unknown")
    print(f"✅ 成功辨識數量： {success_count}")