import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 載入並旋轉
img = cv2.imread(r"C:\Users\Eric\Desktop\Test\AutoCase\AutoCase\output.png")
img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

# 旋轉 & 擷取 ROI
h, w = img.shape[:2]
roi = img[int(h * 0.40):int(h * 0.90), :]

# 放大後灰階 + 自適應二值化（比 OTSU 更穩定）
roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
binary = cv2.adaptiveThreshold(gray, 255, 
                               cv2.ADAPTIVE_THRESH_MEAN_C, 
                               cv2.THRESH_BINARY, 31, 10)

# 僅保留最底部 50%
h2, _ = binary.shape
binary = binary[int(h2 * 0.4):, :]

# OCR
text = pytesseract.image_to_string(binary, config='--oem 3 --psm 6')
print(text)

# 儲存圖片觀察
cv2.imwrite("focused_roi_for_ocr.png", binary)