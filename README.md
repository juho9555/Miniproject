# 미니프로젝트

## 프로젝트 설명  
네이버지도의 길안내 이용 시 지하철 혼잡도 확인기능 추가하기  


### 바로가기
- [피드백진행](./feedback/feedback.md)
- [피드백문제개선방안](./docs/project_description.docx)
- [기본HTML추가](./src/tests.py/index.html)

### 하드웨어
- 웹캠
- 데스크 탑

  
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

