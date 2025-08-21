import cv2
import os
import numpy as np
import time

# 영상 파일 경로 지정
video_path = os.path.join(os.path.dirname(__file__), '../../assets/subway_cctv.mp4')

cap = cv2.VideoCapture(video_path)

# HTML 파일 경로
html_file = 'index.html'

def update_html(count, status, color_rgb):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>지하철 혼잡도 확인</title>
        <meta http-equiv="refresh" content="1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f0f0f0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center
            }}
            .container {{
                width: 90%;
                max-width: 600px;
                background-color: #fff;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-top: 20px;
            }}
            .header {{
                display: flex;
                align-items: center;
                padding: 10px;
            }}
            .header-icon {{
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background-color: #00c73c;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }}
            h1 {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin: 0 0 0 10px;
            }}
            .tabs {{
                display: flex;
                gap: 10px;
                margin: 10px 0;
            }}
            .tab {{
                padding: 5px 12px;
                border-radius: 20px;
                border: 1px solid #ccc;
                cursor: pointer;
            }}
            .active {{
                background: #00c73c;
                color: white;
                font-weight: bold;
                border: none;
            }}
            .content {{
                margin-top: 10px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .status {{
                font-weight: bold;
                color: {("green" if status=="혼잡하지 않음" else ("orange" if status=="보통" else "red"))};
            }}
        </style>
    </head>
    <body>
        <h1>🚇 강남역 2호선</h1>
        <div class="tabs">
            <div class="tab">실시간</div>
            <div class="tab">시간표</div>
            <div class="tab active">혼잡도</div>
        </div>
        <div class="content">
            현재 혼잡도: <span class="status">{status}</span><br>
            대기 인원: {count}명
        </div>
    </body>
    </html>
    """
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)


# 영상의 FPS 가져오기
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 30  # FPS를 얻지 못할 경우 기본값 설정
ms_per_frame = int(1000 / fps)

# ROI 설정
roi_corners = np.array([[
    (75, 720),
    (270, 119),
    (315, 130),
    (520, 720)
]], dtype=np.int32)

mask = None
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start_time = time.time()

    # ROI 마스크 생성
    if mask is None:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, roi_corners, 255)
        roi_area = cv2.countNonZero(mask)

    # 배경 제거
    fgmask = fgbg.apply(frame)

    # 노이즈 제거
    kernel = np.ones((5, 5), np.uint8)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)

    # ROI 적용
    roi_fgmask = cv2.bitwise_and(fgmask, fgmask, mask=mask)

    # ROI 내의 흰색 픽셀 수 계산
    white_pixels = cv2.countNonZero(roi_fgmask)
    
    total_pixels = roi_area

    if total_pixels > 0:
        density = white_pixels / total_pixels
    else:
        density = 0

    status_eng, status_kor, color_bgr = '', '', (0, 0, 0)
    if density <= 0.01:
        status_eng, status_kor, color_bgr = 'not crowded', '혼잡하지 않음', (255, 0, 0)
    elif density <= 0.08:
        status_eng, status_kor, color_bgr = 'moderate crowded', '보통', (0, 255, 0)
    else:
        status_eng, status_kor, color_bgr = 'crowded', '혼잡함', (0, 0, 255)

    max_people = 500  # ROI에 최대 수용 가능 인원 (임의 값)
    estimated_count = int(density * max_people)

    cv2.putText(frame, f'Density: {density:.4f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, status_eng, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, color_bgr, 2)
    
    color_rgb = color_bgr[::-1]
    update_html(estimated_count, status_kor, color_rgb)

    cv2.polylines(frame, roi_corners, isClosed=True, color=(0, 0, 255), thickness=2)
    
    cv2.imshow('ROI detection', frame)

    # 딜레이 추가 
    elapsed_time = (time.time() - start_time) * 1000  # 밀리초 단위로 변환
    delay = max(1, int(ms_per_frame - elapsed_time))
    
    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()