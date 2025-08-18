from ultralytics import YOLO
import cv2

model = YOLO('yolo11n.pt')

cap = cv2.VideoCapture(0)

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
            body {{
                font-family: Arial, sans-serif; /* 전체 폰트 설정 */
            }}
            .tabs {{
                display: flex;        /* 가로로 정렬 */
                gap: 10px;           /* 탭 간격 */
                margin: 10px 0;      /* 상단 여백 */
            }}
            .tab {{
                padding: 5px 12px;    /* 안쪽 여백 */
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


while True:
    ret, frame = cap.read()
    if ret:
        results = model(frame, classes=[0], conf=0.8, verbose= False) # 사람(class=0)만 탐지, conf(정확도) 0.6 이상만 카운트
        annotated_frame = results[0].plot()

        # 사람 수 카운트하기
        people = [box for box in results[0].boxes if box.conf[0] >= 0.8] # people을 리스트 형식으로 만들어 후처리를 유연하게 만듦
        count = len(results[0].boxes)
        cv2.putText(annotated_frame, f'People: {count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 혼잡도 분류하기
        if count <= 2:
            status_eng = 'not crowded'
            status_kor = '혼잡하지않음' # html용 혼잡도 한글 지정
            cv2.putText(annotated_frame, status_eng, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        elif count <= 5:
            status_eng = 'moderate crowded'
            status_kor = '보통'
            cv2.putText(annotated_frame, status_eng, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        else:
            status_eng = 'crowded'
            status_kor = '혼잡함'
            cv2.putText(annotated_frame, status_eng, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        update_html(count, status_kor)
        cv2.imshow('Yolo ', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
