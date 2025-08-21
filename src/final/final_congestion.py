import cv2
import os
import numpy as np
import time

# 1. 영상 및 HTML 경로 설정
VIDEO_PATH = os.path.join(os.path.dirname(__file__), '../../assets/subway_cctv.mp4')
HTML_FILE = 'index.html'

# 2. HTML 업데이트 함수
def update_html(waiting_count, status_kor, color_rgb):
    """웹페이지에 혼잡도와 대기인원 수를 업데이트"""
    # color_rgb: (R,G,B) -> CSS용 rgb()
    css_color = f'rgb({color_rgb[0]},{color_rgb[1]},{color_rgb[2]})'

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="1">
        <style>
            body {{ font-family: Arial; text-align:center; background:#f0f0f0; }}
            .status {{ color: {css_color}; font-weight:bold; }}
        </style>
    </head>
    <body>
        <h1>🚇 강남역 2호선</h1>
        <div>현재 혼잡도: <span class="status">{status_kor}</span></div>
        <div>대기 인원: {waiting_count}명</div>
    </body>
    </html>
    """
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)

# 3. 영상 캡처 초기화
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
ms_per_frame = int(1000 / fps)

# 4. ROI 설정 (다각형 영역)
ROI_CORNERS = np.array([[
    (75, 720), (270, 119), (315, 130), (520, 720)
]], dtype=np.int32)

roi_mask = None
roi_total_pixels = None

# 5. 배경 제거 객체
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

# 6. 혼잡도 계산 및 영상 처리
SMOOTH_ALPHA = 0.2
smoothed_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start_time = time.time()

    # ROI 마스크 초기화
    if roi_mask is None:
        roi_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(roi_mask, ROI_CORNERS, 255)
        roi_total_pixels = cv2.countNonZero(roi_mask)

    # 배경 제거 및 노이즈 제거
    fgmask = fgbg.apply(frame)
    fgmask = cv2.GaussianBlur(fgmask, (5,5), 0)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))

    # ROI 적용
    roi_fgmask = cv2.bitwise_and(fgmask, fgmask, mask=roi_mask)

    # density 계산 (ROI 내 흰 픽셀 비율)
    white_pixels = cv2.countNonZero(roi_fgmask)
    density = white_pixels / roi_total_pixels if roi_total_pixels else 0

    # 혼잡도 및 대기인원 추정 (세분화)
    if density < 0.001:
        status_eng, status_kor, color_bgr = 'not crowded', '혼잡하지 않음', (255, 0, 0) 
        estimated_count = 0
    elif density <= 0.18:
        status_eng, status_kor, color_bgr = 'very low', '매우 한산', (0, 200, 0) 
        estimated_count = int(density * 15)
    elif density <= 0.25:
        status_eng, status_kor, color_bgr = 'low', '한산', (0, 180, 0) 
        estimated_count = int(density * 30 + 1)
    elif density <= 0.35:
        status_eng, status_kor, color_bgr = 'moderate', '보통', (0, 180, 180) 
        estimated_count = int(density * 80 + 4)
    elif density <= 0.45:
        status_eng, status_kor, color_bgr = 'slightly crowded', '약간 혼잡', (0, 0, 150) 
        estimated_count = int(density * 75 + 5)
    else:
        status_eng, status_kor, color_bgr = 'crowded', '매우 혼잡', (0, 0, 255)
        estimated_count = int(density * 75 + 5)

    #estimated_count = min(estimated_count, 50)

    # 인원수 스무딩
    smoothed_count = int(SMOOTH_ALPHA * estimated_count + (1 - SMOOTH_ALPHA) * smoothed_count)

    # 영상에 표시
    cv2.polylines(frame, ROI_CORNERS, isClosed=True, color=(0,0,255), thickness=2)
    cv2.putText(frame, f'Density: {density:.4f}', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame, status_eng, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, color_bgr, 2)

    # 웹페이지 업데이트
    color_rgb = color_bgr[::-1]  # BGR -> RGB
    update_html(smoothed_count, status_kor, color_rgb)

    # 영상 출력 및 FPS 조절
    cv2.imshow('Subway Congestion', frame)
    elapsed_time = (time.time() - start_time) * 1000
    delay = max(1, int(ms_per_frame - elapsed_time))
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
