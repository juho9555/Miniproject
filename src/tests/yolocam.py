from ultralytics import YOLO
import cv2

model = YOLO('yolo11n.pt')

cap = cv2.VideoCapture(0)

# HTML 파일 경로
html_file = 'index.html'

def update_html(count, status):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>지하철 혼잡도 확인</title>
        <meta http-equiv="refresh" content="1">

        <!--CSS 스타일 정의-->
        <style>
            /* 전체 페이지 폰트 설정*/
            body {{
                font-family: Arial, sans-serif;
            }}

            /*지하철 정보 전체 박스 스타일*/
            #subway-info {{
                border: 1px solid #ccc;
                padding: 15px;
                border-radius: 10px;
                width: 350px;
            }}

            /*혼잡도 표시 영역 박스 스타일*/
            #congestion {{
                margin-top: 20px;
                padding: 10px;
                border-radius: 8px;
                background-color: #f2f2f2;
            }}

            /*혼잡도 레벨 텍스트 스타일*/
            #level {{
                font-weight: bold;
                color: {"green" if status=="혼잡하지않음" else ("orange" if status=="보통" else "red")}
            }}
        </style>
    </head>
    <body>
        <!-- 기존 첨부 이미지(열차 도착정보) -->
        <div id="subway-info">
            <h1>🚇 강남역 2호선</h1>
            <img src="../../assets/map_example.PNG" alt="열차 도착 정보" width="330">
            
            <!-- 혼잡도 추가 부분 -->
            <div id="congestion">
                <h2>현재 혼잡도: <span id="level">{status}</span></h2>
                <p>대기 인원: <span id="count">{count}</span>명</p>
            </div>
        </div>
    </body>
    </html>
    """
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
