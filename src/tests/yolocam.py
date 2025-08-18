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
    </head>

    <body>

        <h1>🚇 강남역 2호선</h1>

        <div id="congestion">
            <h2>현재 혼잡도: <span id="level">{status}</span></h2>
            <p>대기 인원: <span id="count">{count}</span>명</p>
        </div>
    </body>
    </html>
    """
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

while True:
    ret, frame = cap.read()
    if ret:
        results = model(frame, classes=[0], conf=0.6, verbose= False) # 사람(class=0)만 탐지, conf(정확도) 0.6 이상만 카운트
        annotated_frame = results[0].plot()

        # 사람 수 카운트하기
        people = [box for box in results[0].boxes if box.conf[0] >= 0.6] # people을 리스트 형식으로 만들어 후처리를 유연하게 만듦
        count = len(results[0].boxes)
        cv2.putText(annotated_frame, f'People: {count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 혼잡도 분류하기
        if count <= 2:
            status = 'not crowded'
            cv2.putText(annotated_frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        elif count <= 5:
            status = 'moderate crowded'
            cv2.putText(annotated_frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        else:
            status = 'crowded'
            cv2.putText(annotated_frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
        update_html(count, status)
        cv2.imshow('Yolo ', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
