# 미니프로젝트: 지하철 혼잡도 판별 시스템

## 프로젝트 설명  
**지하철의 CCTV 영상을 기반으로 대기 인원을 추정하고 혼잡도를 시각적으로 나타내는 시스템**

- OpenCV의 **배경 제거**와 **ROI(Region of Interest)** 기법을 이용하여 특정 구역의 인원 밀도를 계산  
- 계산된 밀도를 바탕으로 **혼잡도 상태**를 판별  
- 결과를 **HTML 페이지**로 실시간 업데이트  
  
> 네이버 지도와 같은 길안내 서비스에 **실시간 지하철 혼잡도 정보를 제공**하는 기능을 목표로 합니다.  

## 프로젝트 진행 배경
### 초기 계획 (웹캠 기반)
- 처음에는 **웹캠을 통해 대기자 수를 직접 인식**하여 혼잡도를 판별하려 했음  
- 그러나 웹캠 환경에서는 **표본 인구수가 너무 적고, 실제 지하철 상황을 반영하기 어려움**  

### 접근 변경 (지하철 CCTV + YOLO)
- 실제 지하철 CCTV 영상을 기반으로 **YOLO 모델**을 활용하여 대기자 수를 직접 카운트  
- 그러나 YOLO는 **지하철 내 대기자와 단순 통행객을 구분하기 어려움**, 인식 오류가 잦음  
- 손, 다리, 어깨 일부를 사람으로 잘못 인식하는 문제 발생  

### 최종 접근 (GRAYSCALE + 밀도 기반)
- YOLO 대신 **영상 밀도(density) 기반 추정 방식**으로 전환  
- **전처리 과정**:
  1. GRAYSCALE 변환  
  2. 가우시안 블러 (Gaussian Blur) 적용  
  3. 모폴로지 연산 (열림, 닫힘)으로 노이즈 제거  
  4. 배경 제거(MOG2) 후 ROI(관심 영역) 마스크 적용  

- **밀도 계산 로직**:
  - ROI 영역 내 흰색 픽셀의 비율(`white_pixels / roi_total_pixels`)을 계산  
  - 혼잡도 구간을 **세분화**하고, 각 구간에 맞게 **대기 인원 추정식** 적용  
  - 결과를 HTML에 실시간 반영  

**이로써 YOLO의 한계를 보완하면서도 실제 혼잡도를 비교적 안정적으로 추정할 수 있었음.**  

## 구동 방법  

```bash
# 1. 가상환경 실행 (선택)
python -m venv venv
source venv/Scripts/activate   # (Windows)
source venv/bin/activate       # (Mac/Linux)

# 2. 필수 라이브러리 설치
pip install opencv-python numpy

# 3. 실행 (최종 코드 실행)
cd src/final
python final_congestion.py
```

이후 index.html 파일이 자동 갱신되며, 브라우저에서 혼잡도를 확인할 수 있음

## 필수 설치

- Python 3.10+
- OpenCV: ```pip install opencv-python```
- NumPy: ```pip install opencv-python numpy```

## 파일구조
```
Mini_project/
│
├── assets/                    
│   └── subway_cctv.mp4        # 실제 테스트에 사용한 CCTV 영상
│
├── feedback/                  
│   └── feedback.md            # 날짜별 피드백 기록
│
├── docs/                      
│   ├── 01-problem-discovery.md
│   └── project_description.docx
│
├── src/
│   ├── tests/                 # 중간 테스트 코드
│   └── final/
│       ├── final_congestion.py  # 최종 코드
│       └── index.html           # 혼잡도 결과 출력
│
└── README.md
```

## 오류 내용 및 해결

- 사람 인식 오류 (손, 어깨 등을 사람으로 잘못 인식)
    - 원인: YOLO 모델이 작은 물체까지 탐지 -> 손/다리를 사람으로 잘못 인식
    - 해결: ```conf=0.8```이상의 신뢰도만 인정하도록 수정

- ROI(관심영역)외 인원까지 대기자로 인식
    - 원인: 승강장 전체를 인식해 지나가는 사람까지 포함됨
    - 해결: ```cv2.fillPoly()```를 사용하여 ROI 영역을 마스크 처리 -> ROI 내부 픽셀만 분석

- 혼잡도와 웹페이지 인원 수 불일치
    - 원인: 밀도 계산 로직이 단순하여 실제 인원과 오차 발생
    - 해결: 혼잡도 구간을 세분화하고 인원 추정식을 개선
    ```
    if density < 0.001:      # 혼잡하지 않음
    elif density <= 0.18:    # 매우 한산
        elif density <= 0.25:    # 한산
    elif density <= 0.35:    # 보통
    elif density <= 0.45:    # 약간 혼잡
    else:                    # 매우 혼잡
    ```

## 개선 및 발전 방향
- **YOLOv11 + OpenCV 결합**: 현재는 밀도 기반이므로, 정확한 인원수 카운트를 위해 YOLO 모델과 결합 가능

- **CSV/DB 연동**: 혼잡도 데이터를 저장하여 시간대별 패턴 분석 → 네이버 지도 Mock-up 반영

- **실시간 CCTV 연동**: 샘플 영상 대신 실제 지하철 CCTV 서버 스트리밍 적용

- **UI 개선**: 단순 HTML → Flask/Django 기반 웹 서버로 발전 가능

- **모바일 연동**: API 형태로 혼잡도 데이터를 제공하여 앱 서비스에 활용 가능


### 바로가기
- [실행코드](./src/final/final_congestion.py)
- [웹페이지](./src/final/index.html)
- [피드백진행](./feedback/feedback.md)
- [피드백문제개선방안](./docs/01-problem-discovery.md)
- [사용영상](./assets/subway_cctv.mp4)

### 진행상황
<details>
<summary>08.13(수)</summary>  

## 15분 룰 적용
### 1. 빠른 제품 체험 및 핵심 문제 발견 (15분 룰 적용)  
네이버지도 대중교통 길안내는 혼잡도 표시가 아예 없음  
  
### 2. 경쟁사 제품 15분 체험  
카카오 맵은 지하철 혼잡도가 지하철 칸 별로 색깔로 표시됨  
카카오 맵은 대중교통 도착 예정 시간이 초 단위로 표시되는 반면 네이버지도는 분 단위로만 됨  
  
### 3. 사용자 리뷰 스캔  
#### 카카오 맵: 앱스토어 별점 4.7.   
-	몇몇 장소들의 위치와 영업일이 잘못되어 있음 (업데이트 필요)  
-	즐겨찾기 기능이 효과적이지만 비로그인 상태에서는 즐겨찾기 기능이 사라짐 (정보유출 때문)  
-	음식점 랭킹 확인가능, 다만 리뷰 보완 필요  
-	대중교통의 도착 예정 시간이 잘 맞음 (혼잡도 확인가능)  
  
#### 네이버지도: 앱스토어 별점 2.0.  
-	대중교통 길안내 시 도착시간이 맞지 않은 경우가 대다수  
-	출퇴근길에 지하철 연착 또는 혼잡함 때문에 도착 예정 시간 지연된 적이 많음  
-	광고가 많아 발열이 심함  
-	네비게이션 성능이 많이 안 좋음  
  
## 문제 우선순위화  
### 가장 짜증나는점 선택  
네이버지도 대중교통 길안내에 혼잡도 표시가 아예 없는 문제  
네이버지도 도착시간 정확도가 떨어짐  

### 1시간 안에 테스트 가능한 것  
대중교통 길안내의 혼잡도 표시 생성  

  
</details> 
<details> <summary>08.14(목)</summary>

## 진행 상황
- 목표 변경
- 기본 목표:  
"네이버지도의 길안내에 지하철 역 내 CCTV 영상을 기반으로 YOLO를 이용해 지하철을 기다리는 사람 수를 카운트하여 혼잡도 확인 기능을 추가하고 실제 제품 형식으로 반영하는 시스템"

- 새 목표:  
**웹캠에서 사람 수를 세어서 '지하철 혼잡도: 여유/보통/혼잡'을 간단한 HTML 페이지에 표시하기**

- [전체코드](./src/tests.py/yolocam.py)

## 목표
### 1. 웹캠에서 사람 카운트하기
- Yolo를 이용해 웹캠으로 사람이 인식되는지 확인
- 화면에 몇명 인식되는지 표시하기

### 2. 기본 HTML 틀 생성
```
<!DOCTYPE html>
<html>
<head>
    <title>지하철 혼잡도 확인</title>
</head>

<body>
    <h1>🚇 강남역 2호선</h1>
    <div id="congestion">
        <h2>현재 혼잡도: <span id="level">보통</span></h2>
        <p>대기 인원: <span id="count">4</span>명</p>
        <p>예상 대기시간: <span id="wait">3</span>분</p>
    </div>
</body>
</html>
```
- ```<meta http-equiv="refresh" content="1">``` 구문을 추가해 새로고침 빈도를 1초로 갱신

### 3. 사람 수에 따라 혼잡도 분류
```
if count <= 2:
    cv2.putText(annotated_frame, f'not crowded', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

elif count <= 5:
    cv2.putText(annotated_frame, f'moderate crowded', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
else:
    cv2.putText(annotated_frame, f'crowded', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
```
- 0~2명이면 not crowded(여유)
- 3~5명이면 moderate crowded(보통)
- 6명 이상이면 crowded(혼잡)
  
```
if count <= 2:
    status = 'not crowded'

elif count <= 5:
    status = 'moderate crowded'
        
else:
    status = 'crowded'

cv2.putText(annotated_frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
``` 
- 이 처럼 혼잡도를 변수로 지정해 간단하게 표시가능
- 하지만 색상을 변경하기 위해 전 방식을 사용

### 4. 기본 HTML 틀에 혼잡도 적용시키기
```
html_file = 'index.html'

def update_html(count, status):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>

        <title>지하철 혼잡도 확인</title>
        <meta http-equiv="refresh" content="5">
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

    ...
    ...
    ...

    update_html(count, status) # count = 사람 수, status = 혼잡도
```
- 기본 틀인 index.html을 가져와 update_html을 통해 인원수와 혼잡도를 웹 창에 표시

</details> 
<details> <summary>08.18(월)</summary>  

  
## 오늘의 목표

### 사람 인식 정확도 부분 수정
- [오류1](./assets/손을%20사람으로%20인식하는%20오류.png) : 손을 사람으로 인식하는 오류 발생
- [해결1](./assets/config_error_solved.PNG) : 정확도 구문 추가 후 정확도가 0.8 즉 80퍼센트 이상일 경우에만 사람으로 인식
- [오류2](./assets/오른쪽%20측면%20위.PNG) : 지하철 역 내의 cctv의 위치를 고려해 오른쪽 위에서 촬영한 결과 멀리 떨어진 사람의 인식기능이 약화됨
- [해결2](./assets/yolo11s%20오른쪽%20위.PNG) : 기존 yolo11n모델보다 정확도가 향상된 yolo11s모델을 사용함으로써 오른쪽 위에서 촬영 했을 때에도 사람이 잘 인식됨
- 개선 해야할 점 : 아주 멀리 떨어진 사람을 촬영했을 때 인식이 되는지 확인, CSV 데이터값을 연동시킬 수 있는지.

#### CSS로 스타일링
- [1차 수정](./assets/webpage_edited1.PNG)
- [2차 수정](./assets/webpage_edited2.PNG)

</details>

<details>
<summary>08.19(화)</summary>  

## 오늘의 목표

### 카메라의 영역을 설정해 대기열/승강장만 판별

1. ROI로 영역을 설정

2. ROI안의 사람만 대기자로 설정

3. 화질 개선해서 대기자 식별 기능 향상

- [피드백](./feedback/feedback.md)
    
    - [cctv 영상 확보](./assets/subway_cctv.mp4)
    - [ROI영역설정](./assets/Roi_cctv.PNG)
    - [개선점](./docs/01-problem-discovery.md)

강사님 피드백 : YOLO를 통해 사람을 다 파악하는 것은 불가능에 가까움. 그러므로 GRAYSCALE을 통한 색변환으로 밀도값을 더 정확히 구하는 것이 혼잡도 판별에 도움이 될 것.  
  
20일(수)에 YOLO대신 GRAYSCALE을 통한 혼잡도 표시하기 수행 예정

</details>

<details><summary>08.21(목)</summary>

## 오늘의 목표

- GRAYSCALE을 통해 혼잡도 확인하기

- 실제 대기 인원 수와 웹페이지에 표시되는 대기 인원 수의 정확도 향상 시키기

- 이동 평균 구문(smoothed_count)를 추가해 프레임 변동과 대기 인원 추정치를 안정화 시키기

- github readme 파일 총 정리하기

- 발표 자료 만들기

</details>
