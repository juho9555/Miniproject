from ultralytics import YOLO
import cv2

model = YOLO('yolo11n.pt')

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if ret:
        results = model(frame, classes=[0], verbose= False) # 사람(class=0)만 탐지
        annotated_frame = results[0].plot()

        # 사람 수 카운트하기
        count = len(results[0].boxes)
        cv2.putText(annotated_frame, f'People: {count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Yolo ', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
