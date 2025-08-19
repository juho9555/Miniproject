from ultralytics import YOLO
import cv2
import os
import numpy as np

model = YOLO('yolo11s.pt')

# 영상 파일 가져오는 경로 지정
video_path = os.path.join(os.path.dirname(__file__), '../../assets/subway_cctv.mp4')

cap = cv2.VideoCapture(video_path)

# HTML 파일 경로
html_file = 'index.html'

def update_html(count, status):
    # HTML 콘텐츠를 파이썬 f-string 으로 생성
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>지하철 혼잡도 확인</title>
        <!-- 1초마다 페이지 자동 새로고침 -->
        <meta http-equiv="refresh" content="5">
        <style>
            /*
            전체 페이지 스타일:
            - Inter 폰트 사용
            - 여백 제거
            - 배경색 설정q
            - flexbox를 사용하여 모든 내용을 중앙에 정렬
            */
            body {{
                font-family: Arial, sans-serif; /* 전체 폰트 설정 */
                margin: 0;  /* 외부 여백*/
                padding: 0; /* 내부 여백*/
                background-color: #f0f0f0; /* 배경색 연한 회색*/
                display: flex; 
                flex-direction: column; /*세로방향 정렬*/
                align-items: center; /* 가로축 중앙 정렬*/
                justify-content: center /* 세로축 중앙 정렬*/
            }}
            /*
            주요 콘텐츠를 감싸는 컨테이너:
            - 너비, 최대 너비, 배경색, 패딩, 둥근 모서리, 그림자 설정
            - 모바일 및 데스크톱 환경 모두에 적합하도록 반응형으로 설계
            */
            .container {{
                width: 90%; /* 화면 너비의 90%를 차지 */
                max-width: 600px; /* 최대 너비를 600px로 제한하여 큰 화면에서 너무 넓어지는 것을 방지 */
                background-color: #fff; /* 배경색을 흰색으로 지정 */
                padding: 20px; /* 컨테이너 내부 여백: 테두리와 내용 사이의 공간 */
                border-radius: 12px; /* 둥근 모서리를 만들어 부드러운 느낌을 줌 */
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 그림자 효과를 추가하여 입체감을 줌 */
                margin-top: 20px; /* 컨테이너 외부 여백: 다른 요소와의 간격 */
            }}

            /*
            페이지 상단 헤더 (역 이름, 역 아이콘) 스타일
            */
            .header {{
                display: flex; /* 자식 요소들을 가로로 정렬 */
                align-items: center; /* 수직 중앙 정렬 */
                padding: 10px; /* 헤더 내부 여백 */
            }}
            
            /* 역 번호 아이콘 스타일 (예: 2호선) */
            .header-icon {{
                width: 24px; /* 너비 24px */
                height: 24px; /* 높이 24px */
                border-radius: 50%; /* 50%로 설정하여 원형으로 만듦 */
                background-color: #00c73c; /* 배경색을 네이버 녹색 계열로 지정 */
                color: white; /* 글자색을 흰색으로 지정 */
                display: flex; /* 자식 요소(숫자)를 유연하게 배치 */
                align-items: center; /* 수직 중앙 정렬 */
                justify-content: center; /* 수평 중앙 정렬 */
                font-weight: bold; /* 글자를 굵게 만듦 */
            }}

            /* 역 이름 제목 스타일 */
            h1 {{
                font-size: 24px; /* 글자 크기 24px */
                font-weight: bold; /* 글자를 굵게 만듦 */
                color: #333; /* 글자색을 진한 회색으로 지정 */
                margin: 0 0 0 10px; /* 위쪽 0, 오른쪽 0, 아래쪽 0, 왼쪽 10px의 외부 여백 */
            }}
            .tabs {{
                display: flex;        /* 가로로 정렬 */
                gap: 10px;           /* 탭 간격 */
                margin: 10px 0;      /* 상단 여백 */
            }}
            .tab {{
                padding: 5px 12px;    
                border-radius: 20px;  /* 둥근 모서리 */
                border: 1px solid #ccc; /* 테두리 */
                cursor: pointer;      /* 마우스 올리면 손가락 모양 */
            }}
            .active {{
                background: #00c73c;  /* 선택된 탭 색 (네이버 녹색 계열) */
                color: white;         /* 글자색 흰색 */
                font-weight: bold;    /* 굵은 글씨 */
                border: none;         /* 테두리 제거 */
            }}
            .content {{
                margin-top: 10px;     /* 위쪽 여백 */
                padding: 10px;        /* 안쪽 여백 */
                border: 1px solid #ddd; /* 회색 테두리 */
                border-radius: 8px;   /* 둥근 모서리 */
            }}
            .status {{
                font-weight: bold;    /* 굵은 글씨 */
                /* 혼잡도에 따라 색상 변경 */
                color: {"green" if status=="혼잡하지않음" else ("orange" if status=="보통" else "red")};
            }}
        </style>
    </head>
    <body>
        <h1>🚇 강남역 2호선</h1>

        <!-- 탭 메뉴 -->
        <div class="tabs">
            <div class="tab">실시간</div> <!-- 첫 번째 탭 -->
            <div class="tab">시간표</div> <!-- 두 번째 탭 -->
            <div class="tab active">혼잡도</div> <!-- 현재 선택된 탭 -->
        </div>

        <!-- 혼잡도 정보 출력 -->
        <div class="content">
            현재 혼잡도: <span class="status">{status}</span><br>
            대기 인원: {count}명
        </div>
    </body>
    </html>
    """
    
    # HTML 내용을 파일로 저장
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

# roi 설정
roi_corners = np.array([[
    (75, 720),
    (270, 119),
    (315, 130),
    (520, 720)
]], dtype=np.int32)

mask = None

while True:
    ret, frame = cap.read()
    if ret:
        
        CONF_THRESHOLD = 0.1

        # YOLO 감지
        results = model(frame, classes=[0], conf=CONF_THRESHOLD, verbose= False) # 사람(class=0)만 탐지, conf(정확도) 0.6 이상만 카운트
        annotated_frame = results[0].plot()

        # ROI 마스크 생성
        if mask is None:
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, roi_corners, 255)

        count = 0

        annotated_frame = frame.copy()

        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            if mask[cy, cx] == 255:
                count += 1
                cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(annotated_frame, f'person {box.conf[0]:.1f}', (int(x1), int(y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 사람 수 카운트하기
        people = [box for box in results[0].boxes if box.conf[0] >= CONF_THRESHOLD and mask[int((box.xyxy[0][1]+box.xyxy[0][3])/2), int((box.xyxy[0][0]+box.xyxy[0][2])/2)] == 255] # people 리스트를 ROI기준으로 필터링
        
        count = len(people)
        cv2.putText(annotated_frame, f'People: {count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 혼잡도 분류하기
        roi_area = cv2.contourArea(roi_corners) # 컨투어로 roi안의 픽셀 구하기

        if roi_area < 50000: # 작은 ROI -> count 기준
            
            if count <= 10:
                status_eng, status_kor, color = 'not crowded', '혼잡하지 않음', (0, 0, 255)

            elif count <= 20:
                status_eng, status_kor, color = 'moderate crowded', '보통', (0, 255, 0)

            else:
                status_eng, status_kor, color = 'crowded', '혼잡함', (255, 0, 0)

        else: # 큰 ROI -> density 기준
            density = count / roi_area
            if density <= 0.0001:
                status_eng, status_kor, color = 'not crowded', '혼잡하지 않음', (0, 0, 255)
            
            elif density <= 0.0005:
                status_eng, status_kor, color = 'moderate crowded', '보통', (0, 255, 0)
            
            else:
                status_eng, status_kor, color = 'crowded', '혼잡함', (255, 0, 0)

        cv2.putText(annotated_frame, status_eng, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
        update_html(count, status_kor)

        cv2.polylines(annotated_frame, roi_corners, isClosed=True, color=(0, 0, 255))

        # Roi 표시
        cv2.imshow('ROI detection', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
