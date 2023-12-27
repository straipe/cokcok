# Django+MySQL+MoveNet




  
## Django



- **Directory Structure**

  ```
  📦badminton
   ┣ 📂accounts
   ┃ ┣ 📜models.py
   ┃ ┣ 📜views.py
   ┣ 📂badminton
   ┣ 📂process
   ┃ ┣ 📜movenet.py
   ┃ ┣ 📂core
   ┃ ┃ ┣ 📂data
   ┃ ┃ ┃ ┣ 📜features.txt
   ┃ ┃ ┃ ┗ 📜knn_model.joblib
   ┃ ┣ 📜models.py
   ┃ ┣ 📜views.py
  ```



- **Django App**



  📂**accounts**

  - 회원가입, 마이페이지 조회와 같은 계정 관련 기능을 구현하기 위한 app이다.

  ┃ ┣  📜**models.py**

  - Player 모델은 회원 정보를 처리하기 위해 구현하였다. 이 모델은 DB의 Player table에 대응된다.

  ┃ ┣ 📜**views.py**

  - APIView를 상속받은 클래스 기반 뷰 PlayerInfo를 구현하였다. GET, POST, PUT, DELETE 메서드를 재정의하였으며, 특히 POST 메서드의 경우 회원 정보를 DB에 저장할 때 회원과 업적 간의 관계에 대한 정보를 추가로 저장하게끔 하였다.



  📂**process**

  - 스윙분석&경기분석을 위한 Django app이다.

   ┃ ┣ 📜**movenet.py**

  - movenet 모델을 로드하고 영상 데이터를 분석하여 원하는 데이터를 추출하는 로직이 구현되어 있다.

   ┃ ┣ 📂**core**

  - data 폴더와 analysis.py, classification.py가 담겨있다. data 폴더는 스윙분석&경기분석에 사용할 전문가 데이터가 담겨있으며, analysis.py는 하이클리어 스윙을 분석하는 알고리즘이, classification.py는 경기 중 발생한 스윙을 분류하는 KNN 알고리즘이 담겨있다.

   ┃ ┣ 📜**models.py**

  - Motion 모델은 스윙 분석 데이터를 처리하기 위해 구현하였으며, MatchRecord는 경기 기록 데이터를, Achievement는 업적 데이터를, SwingScore는 한 경기에 대한 유저의 각 스윙 별 점수 데이터를 처리하기 위해 구현하였다. PlayerAchievement는 유저-업적의 M:N 관계를 해소하기 위해 구현하였다.

   ┃ ┣ 📜**views.py**

  - accounts 앱과 마찬가지로 APIVEW를 상속받은 클래스 기반 뷰를 구현하였다. 
  - class MatchRecordList
    - MatchRecordList는 LimitOffsetPagination을 추가로 상속받아 Pagination 기능을 구현하였다. 이 기능은 각 클래스의 get 메서드에서 활용하였다.
    - post 메서드는 클라이언트로부터 전송된 json파일과 csv파일을 처리하고 DB와 storage에 저장하는 로직이 구현되었다. json파일은 애플워치가 수집한 경기기록 데이터가 담겨있으며 csv파일은 한 경기에서 발생한 애플워치의 x,y,z축 가속도 시계열 데이터와 각속도 시계열 데이터가 저장되었다. 경기기록과 분석정보를 DB에 저장하면 유저의 업적 별 누적치를 업데이트하고 달성여부를 체크하는 로직이 구현되었다.
  - class PlayerMotionList
    - LimitOffsetPagination을 추가로 상속받아 Pagination 기능을 구현하였다. 이 기능은 각 클래스의 get 메서드에서 활용하였다.
    - post 메서드는 클라이언트로부터 전송된 mp4파일과 csv파일을 처리하고 DB&storage에 저장하는 로직이 구현되었다. Mp4파일은 iOS에서 촬영한 사용자의 하이클리어 스윙(1회) 영상 데이터를 뜻하며, csv파일은 사용자의 하이클리어 스윙(1회)에 대한 x,y,z축 가속도, 각속도 시계열 데이터를 뜻한다. movenet.py를 통해 mp4파일을 분석하고, analysis.py를 통해 csv파일을 분석하여 피드백 데이터를 DB에 저장한다.



## MySQL



- **ERD** (Swing_Score Entity 제외)

![erd](https://github.com/straipe/cokcok/assets/43769778/0c8af767-3a77-43f3-8462-4c5a9983d05e)


- **Entity**
  - Player: 각 유저의 회원정보를 저장하기 위한 엔티티
  - Motion: 유저 별 스윙 분석 데이터를 저장하기 위한 엔티티
  - Match_Record: 유저 별 경기 기록 데이터를 저장하기 위한 엔티티
  - Achievement: 업적 데이터를 저장하기 위한 엔티티
  - Player_Achievement: 유저와 업적 간의 M:N 관계를 해소하기 위한 엔티티
  - Swing_Score: 경기 당 분류된 스윙들의 점수를 저장하기 위한 엔티티



## Amazon Web Services



- **S3 Storage**: 스윙 분석, 경기 분석에 필요한 mp4 파일과 csv 파일을 저장한다.
- **RDS**: MySQL 데이터베이스를 구축하기 위해 활용하였다.
- **EC2 instance**: AMI는 Ubuntu를 지정하였으며 movenet을 활용하기 위해 메모리가 비교적 크고 GPU가
  탑재된 instance를 활용할 계획이다.



## MoveNet



- **Model Architecture**

![MoveNet architecture](https://1.bp.blogspot.com/-GvLNT9SFGJ8/YJ7qxvGTsDI/AAAAAAAAENE/J-nRn34k48UbDpMhPvjX1RG66WX1IsppwCLcBGAsYHQ/s0/MoveNetArchitecture%2B%25281%2529.png)

  MoveNet은 히트맵을 사용하여 관절을 예측하는 하향식 추정 모델이다.  이 모델은 두 가지 요소로 구성되어 있다. Feature extractor와 prediction heads이다. 모든 모델은 TensorFlow Object Detection API를 활용하여 훈련시켰다. 

  Feature extractor는 feature pyramid network(FPN)가 연결된 MobileNetV2이다. 또한 4개의 prediction heads들이 연결되어 있으며, 이들은 각각 4가지 요소를 예측한다.

1. **Person center heatmap**: 사람 인스턴스의 중심 좌표를 예측한다.
2. **Keypoint regression field**: 사람 인스턴스 내의 17개 관절 좌표를 예측한다.
3. **Person keypoint heatmap**: 사람 인스턴스와는 독립적으로 17개 관절 좌표를 예측한다.
4. **2D per-keypoint offset field**: 특징맵의 pixel에서 각 관절의 sub-pixel 위치에 대한 local offset을 예측한다.

이를 종합하여 보다 정확한 관절의 위치를 예측한다.


- **Model Version**

  MoveNet은 Lightning과 Thunder 두 가지 버전이 존재한다. Lightning은 모바일 환경에서도 real-time 연산이 가능하고 초당 50프레임 연산이 가능하다. 반면 Thunder은 크고 느리지만 높은 정확도를 보인다. 

- **Use of MoveNet**

  이 프로젝트에서 MoveNet을 활용한 스윙 자세 분석 알고리즘을 소개한다.

  **(Step1)** 배드민턴 하이클리어 논문을 분석하여 하이클리어 자세에 중요한 3가지 요소(어깨 각도, 팔꿈치 각도, 상체 회전량)를 선정한다.  
  ![angle](https://github.com/straipe/cokcok/assets/43769778/0994024f-44be-44e7-ba85-437923df5f9f)

  **(Step2)** OpenCV의 VideoCapture를 활용해 mp4파일을 프레임 당 numpy 배열(1,480,360,3)로 변환한다.

  **(Step3)** 전처리된 영상 데이터에서 movenet을 통해 17개의 관절의 x,y좌표와 신뢰 점수를 추출한다. (신뢰 점수가 0.3 이하인 관절의 개수가 11개 이상이면 사용자가 촬영되지 않았다고 간주하고 예외처리를 한다.)

  **(Step4)** 오른 손목이 제일 위로 향한 시점에 대한 프레임을 추출하고 이 시점을 임팩트 시점이라 간주한다. 이 때 어깨 각도와 팔꿈치 각도를 벡터의 내적과 arccos를 통해 계산한다.  
![vector](https://github.com/straipe/cokcok/assets/43769778/1c299018-01a4-46a4-92cb-2b78f491d827)

  **(Step5)** 각 프레임 별 골반 너비의 길이를 계산한다. (오른쪽 골반과 왼쪽 골반의 x,y좌표에 대한 유클리디안 거리를 계산한다.) 이후 (상체 회전량) = { (골반 너비의 최댓값) – (골반 너비의 최솟값) } / (골반 너비의 최댓값)이라는 식을 통해 상체 회전량을 측정한다.  
  골반 너비 최댓값: p_max, 골반 너비 최솟값: p_min이라 하면,  
![pelvic](https://github.com/straipe/cokcok/assets/43769778/388542f2-85cb-4c0a-a6dd-c3236dd06a21)
  
  **(Step6)** 이처럼 추출된 임팩트 순간의 어깨 각도&팔꿈치 각도와 스윙 전반의 상체 회전량을 전문가 데이터와 비교하여 피드백을 제공한다.
