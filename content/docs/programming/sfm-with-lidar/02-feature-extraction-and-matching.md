---
title: "2편: Feature 추출 및 매칭"
date: 2026-05-15T01:00:00+09:00
draft: false
tags: ["SfM", "OpenCV", "SIFT", "Feature Matching", "RANSAC"]
categories: ["programming"]
description: "SIFT로 feature를 추출하고 BFMatcher + RANSAC으로 세 프레임 간 대응점을 찾습니다."
---

> **지난 이야기 (1편 요약) 💡**
> 지난 **[1편: 개요 및 데이터 준비]**에서는 3-View SfM의 청사진을 그리고 실습에 쓸 고해상도 ETH3D Pipes 이미지 3장과 카메라 Intrinsic 파라미터를 로딩했습니다. 
> 이번 2편에서는 이 세 장의 2D 이미지들을 정밀 대조하여, 서로 겹치는 물리적 부분들을 일대일 매칭해 주는 **대응점(Correspondences) 탐색 엔진**을 구현합니다. 이 대응점들이 앞으로 진행될 3편(카메라 Pose 복원)과 5편(PnP)의 가장 핵심적인 기초 입력 데이터가 됩니다!

---

## 1. Feature(특징점)란? 이미지 속의 명확한 랜드마크

3D 공간을 복원하려면 여러 사진 속에서 "이 부분이 서로 같은 위치의 물체다"라고 선언해 주는 매칭 작업이 필요합니다. 이때 컴퓨터가 쉽게 인지하고 매칭할 수 있는 신뢰성 높은 픽셀 지점을 **Feature(특징점)**라고 합니다.

> [!NOTE]  
> **초보자를 위한 특징점 비유**
> 
> 우리가 지도를 보고 약속 장소를 정할 때 **'남산타워'**나 **'에펠탑'**처럼 멀리서 보든, 각도를 틀어 보든, 밤에 보든 한눈에 알아볼 수 있는 독특하고 명확한 장소를 고릅니다. 이것이 바로 좋은 **특징점(Feature)**입니다.
> 
> 반대로 아무 무늬도 없는 하얀 벽지나 평범한 아스팔트 바닥의 한 지점은 아무리 다각도로 촬영해 봐야 어디가 어디인지 컴퓨터가 매칭할 수 없습니다. 즉, 좋은 특징점은 **회전, 크기 변화, 밝기 변화가 생겨도 변함없이 뚜렷하게 구별되는 픽셀 지점**을 의미합니다.

---

## 2. SIFT: 회전과 스케일 변화에도 끄떡없는 지문 탐지기

**SIFT(Scale-Invariant Feature Transform)**는 컴퓨터 비전 역사상 가장 신뢰도가 높고 널리 검증된 특징점 검출 알고리즘입니다. 실시간성 속도가 생명인 단말 모바일 환경(예: ORB 알고리즘 활용)과 달리, SfM은 **정밀한 3D 복원 품질이 최우선**이므로 다소 느리더라도 매칭 정확도가 압도적인 SIFT를 주로 사용합니다.

SIFT는 두 단계를 거쳐 동작합니다.
1. **Keypoint 검출:** 이미지에서 랜드마크 역할을 할 특징점의 좌표를 찾습니다.
2. **Descriptor(기술자) 생성:** 각 특징점 주변의 밝기 패턴 흐름을 분석하여, **128차원의 숫자 벡터**로 이루어진 고유의 **"지문(Descriptor)"**을 부여합니다. 

사람마다 지문이 다르듯, 이 128개의 숫자로 표현된 고유 지문 정보 덕분에 다른 각도에서 찍힌 물체의 특징점과 확실하게 대조해 볼 수 있습니다.

---

## 3. 실습 1: SIFT 특징점 및 지문(Descriptor) 추출

OpenCV의 간단한 API를 사용하여 이미지 딕셔너리로부터 특징점과 지문 벡터를 수집합니다.

```python
import cv2
import numpy as np

def extract_features(images: dict) -> dict:
    """
    로드된 이미지 딕셔너리로부터 SIFT 특징점과 지문을 추출합니다.
    """
    # 5,000개의 풍부한 특징점을 검출하도록 인스턴스 생성
    sift = cv2.SIFT_create(nfeatures=5000)
    features = {}
    
    for name, img in images.items():
        # SIFT 연산은 연산량 감소를 위해 흑백(GrayScale) 이미지 상에서 작동합니다.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # kps: 특징점 위치 정보 (x, y 좌표 등)
        # descs: 각 특징점당 128차원의 고유 지문 행렬 (N, 128)
        kps, descs = sift.detectAndCompute(gray, None)
        
        features[name] = {'kps': kps, 'descs': descs}
        print(f"{name}: {len(kps)}개의 특징점(Keypoint) 추출 완료")
        
    return features
```

---

## 4. Feature 매칭과 Lowe's Ratio Test: 1등만 기억하는 냉혹한 필터

두 이미지에서 뽑아낸 지문(Descriptor) 행렬들을 일대일로 비교하여 가장 가까운 쌍을 맺어줍니다. 

### 4.1 BFMatcher (Brute-Force Matcher)
A 이미지의 지문 1개를 들고 B 이미지에 있는 수천 개의 지문들과 유클리드 거리를 전부 다 대조해 보는 가장 무식하지만 확실한 **전수 조사 매칭 기법**입니다. 정확도가 생명인 SfM 구조에 가장 이상적인 매처입니다. (`cv2.NORM_L2`는 SIFT 지문 벡터 간의 거리를 유클리드 거리식으로 잰다는 의미입니다)

### 4.2 Lowe's Ratio Test (애매한 녀석 탈락 필터)
단순 전수 조사(BFMatcher)만 하면, 반복되는 격자무늬나 타일벽처럼 비슷하게 생긴 패턴에서 컴퓨터가 꼬인 2등, 3등 매칭을 덥석 선택해 버립니다. SIFT 제안자인 David Lowe 교수가 고안한 Ratio Test는 이러한 **"애매한 오답 매칭"**을 수학적으로 완전히 솎아냅니다.

$$\frac{\text{1순위 후보까지의 거리 } (d_1)}{\text{2순위 후보까지의 거리 } (d_2)} < 0.75$$

> [!TIP]  
> **Lowe's Ratio Test의 직관적 원리**
> 
> "가장 닮은 1등 매칭 후보의 신뢰도가 2등 매칭 후보보다 **압도적으로 월등할 때만** 진짜로 인정하겠다!" 
> 
> 만약 1등 매칭점의 거리가 10픽셀이고 2등 매칭점의 거리도 11픽셀이라면, 두 점이 너무 비슷해 컴퓨터가 헷갈려 꼬였을 확률이 높으므로 **"애매하니까 둘 다 매칭 대상에서 탈락!"**시키겠다는 지혜로운 기각 알고리즘입니다.

```python
def match_features(feat_a: dict, feat_b: dict) -> list:
    """
    두 이미지의 지문을 전수 비교하고 Lowe's ratio test로 애매한 오답 매칭을 기각합니다.
    """
    bf = cv2.BFMatcher(cv2.NORM_L2)
    # k=2 옵션으로 각 특징점당 가장 가까운 1순위(m)와 2순위(n) 매칭점 후보 2개를 구합니다.
    raw_matches = bf.knnMatch(feat_a['descs'], feat_b['descs'], k=2)

    # Lowe's ratio test 적용
    good_matches = []
    for m, n in raw_matches:
        # 1순위 거리가 2순위 거리의 75% 미만으로 월등하게 차이가 나는 경우만 엄선
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)
            
    return good_matches
```

---

## 5. RANSAC으로 기하학적 거짓말(Outlier) 영구 정화하기

Lowe's ratio test를 통과한 점들도 여전히 논리적으로 말이 안 되는 매칭 오류(**Outlier**)들이 숨어 있습니다. 
예를 들어 물체의 형태상 도저히 연결될 수 없는 하늘 끝점과 바닥 끝점이 우연히 패턴 지문이 비슷해서 통과한 경우 등입니다. 

이를 물리 공간적으로 완전무결하게 정제하기 위해 **Fundamental Matrix (기초 행렬, $F$) 기반 RANSAC**을 작동시킵니다.

> [!IMPORTANT]  
> **RANSAC(Random Sample Consensus)의 민주주의 다수결 투표 비유**
> 
> 시끄러운 시장통에서 가짜 소문을 퍼뜨리는 아웃라이어 무리들 사이에서 **진실(Inlier)**을 밝히기 위해 RANSAC은 다음과 같은 **다수결 투표 기법**을 반복합니다.
> 
> 1. 매칭 쌍 전체 중 무작위로 딱 **8개쌍의 매칭 점(8-point algorithm의 기원)**만 추출하여 임시 기하학 공식($F$)을 속성으로 뚝딱 조립합니다.
> 2. 조립된 임시 공식에 다른 모든 매칭 쌍 점들을 대입해 봅니다. 이 공식이 딱 맞아떨어져 **"나도 동의해!"**라고 찬성표를 던지는 매칭 쌍(**Inlier**)의 개수를 차곡차곡 집계합니다.
> 3. 이 과정을 수천 번 반복(보통 1,000번 이상)하여 **"가장 압도적으로 많은 찬성표를 받아낸 최강의 기하학적 약속 공식"**을 최종 골라냅니다.
> 4. 그 공식을 만든 최강 주역 매칭 쌍(Inlier)들만 보존하고, 끝까지 공식에 반대한 엉터리 오답 매칭 쌍(Outlier)은 가차 없이 역사적 쓰레기통으로 던져 영구 소멸시킵니다.

```python
def filter_matches_ransac(feat_a, feat_b, matches, threshold=3.0):
    """
    RANSAC 알고리즘으로 기하학적 다수결 투표를 전개하여 완전무결한 인라이어 점들만 정제합니다.
    """
    # 매칭된 특징점들의 [x, y] 픽셀 좌표만 배열로 추출
    pts_a = np.float32([feat_a['kps'][m.queryIdx].pt for m in matches])
    pts_b = np.float32([feat_b['kps'][m.trainIdx].pt for m in matches])

    # ETH3D Pipes 데이터셋은 가로 6,000픽셀이 넘는 초고해상도이므로,
    # RANSAC의 일치 허용 임계 오차(Threshold)를 3.0픽셀 마진으로 여유 있게 설정합니다.
    F, mask = cv2.findFundamentalMat(
        pts_a, pts_b,
        method=cv2.FM_RANSAC,
        ransacReprojThreshold=threshold,
        confidence=0.999
    )

    # 투표 결과 정답으로 판명된 인라이어 마스크 추출
    inlier_mask = mask.ravel().astype(bool)
    
    # 아웃라이어가 걸러진 정예 매칭 좌표 쌍 획득
    pts_a_inliers = pts_a[inlier_mask]
    pts_b_inliers = pts_b[inlier_mask]
    
    print(f"  RANSAC 정화 결과: {inlier_mask.sum()} / {len(matches)} 개의 고품질 매칭점 확보")
    
    return pts_a_inliers, pts_b_inliers, F
```

---

## 6. 세 프레임 쌍 매칭 (3-View 복원 준비)

우리의 3-View SfM 엔진은 세 개의 이미지 쌍(1↔2, 2↔3, 1↔3) 사이의 모든 연결고리를 확보해야 합니다. 그래야만 입체 뼈대가 끊어지지 않고 이어집니다.

```python
# 1편에서 로드하여 준비한 dslr 이미지 데이터들을 할당합니다.
name0, name1, name2 = img_names
features = extract_features(images)

print("\n--- 이미지 쌍별 특징점 매칭 및 RANSAC 필터링 전개 ---")

# [쌍 1] 0번째 이미지 <-> 1번째 이미지 매칭
raw_01 = match_features(features[name0], features[name1])
pts0_1, pts1_0, F01 = filter_matches_ransac(features[name0], features[name1], raw_01)

# [쌍 2] 1번째 이미지 <-> 2번째 이미지 매칭
raw_12 = match_features(features[name1], features[name2])
pts1_2, pts2_1, F12 = filter_matches_ransac(features[name1], features[name2], raw_12)

# [쌍 3] 0번째 이미지 <-> 2번째 이미지 매칭
raw_02 = match_features(features[name0], features[name2])
pts0_2, pts2_0, F02 = filter_matches_ransac(features[name0], features[name2], raw_02)
```

---

## 7. 매칭 시각화 그리기

인라이어로 엄선된 대응점들을 두 이미지 평면 사이에 알록달록한 실선으로 잇는 아름다운 시각화 결과물을 만듭니다.

> [!NOTE]  
> **cv2.DMatch 수동 생성 트릭**
> 
> OpenCV의 `cv2.drawMatches` 함수는 픽셀 좌표(`pts_a`, `pts_b`)를 직접 넘겨받지 못하고, 특징점 정보와 그들 사이의 인덱스 매칭 연결고리를 저장한 `cv2.DMatch` 리스트를 요구합니다.
> RANSAC 필터링 후에는 아웃라이어가 제거된 순수 픽셀 좌표(`pts_a_inliers`, `pts_b_inliers`)만 인라이어 순서대로 정비되어 남게 됩니다. 
> 
> 따라서 우리는 `i`번째 인라이어 A 픽셀과 `i`번째 인라이어 B 픽셀이 일대일 매칭이라는 뜻으로 `cv2.DMatch(i, i, 0)`를 수동 조립해 `drawMatches`에 공급하는 유용한 코딩 트릭을 활용합니다.

```python
def visualize_matches(img_a, img_b, pts_a, pts_b, max_show=100):
    """
    엄선된 인라이어 매칭 쌍을 실선으로 아름답게 시각화해 줍니다 (상위 max_show개 표시).
    """
    # OpenCV KeyPoint 객체 생성
    kps_a = [cv2.KeyPoint(p[0], p[1], 1) for p in pts_a[:max_show]]
    kps_b = [cv2.KeyPoint(p[0], p[1], 1) for p in pts_b[:max_show]]
    
    # 0번점끼리, 1번점끼리... 순차 일대일 매칭 선언 DMatch 생성 (거리 가중치 0)
    dmatches = [cv2.DMatch(i, i, 0) for i in range(len(kps_a))]

    # 단독 특징점은 제외하고 매칭된 실선만 뚜렷하게 묘사
    vis = cv2.drawMatches(img_a, kps_a, img_b, kps_b, dmatches, None,
                          flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    return vis
```

### 7.1 Google Colab / 로컬 최적화 렌더링
초고해상도 Pipes 이미지의 매칭 결과를 화면 크기에 맞춰 아름답게 스케일 다운하여 보여줍니다.

```python
from google.colab.patches import cv2_imshow
import cv2

# 이미지 0과 이미지 1 사이의 최종 100개 알짜배기 매칭 렌더링
vis = visualize_matches(images[name0], images[name1], pts0_1, pts1_0, max_show=100)

# 원본의 가로, 세로 해상도 파악
h, w = vis.shape[:2]

# 모니터 뷰에 보기 편하도록 가로폭 최대 1200 픽셀 비율로 자동 리사이즈
max_display_width = 1200
if w > max_display_width:
    scale = max_display_width / w
    new_w = int(w * scale)
    new_h = int(h * scale)
    vis_resized = cv2.resize(vis, (new_w, new_h))
    cv2_imshow(vis_resized)
else:
    cv2_imshow(vis)
```

![DSC_0634 ↔ DSC_0635 간 SIFT 매칭 결과 (RANSAC inlier 100개)](/images/programming/sfm-with-lidar/02-feature-matching.png)

---

## 다음 편 예고

우리는 세 이미지 사이에서 오차가 완벽히 제거된 보석 같은 고품질 매칭점 `pts0_1`, `pts1_0`을 획득하는 데 성공했습니다!

다음 **[3편: 2-View Geometry]** 편에서는 이 소중한 매칭 픽셀점들에 1편에서 읽어 들인 카메라 Intrinsic 돋보기 행렬($K$)을 곱하여 렌즈 왜곡을 걷어내고, 기하학적 보물상자인 **Essential Matrix(에센셜 행렬)**를 복원하여 두 카메라의 입체적인 상대 위치와 자세($R, t$)를 도출함과 동시에, 첫 번째 **3D 공간 포인트 클라우드(삼각측량)**를 화려하게 탄생시켜 보겠습니다. 다음 장에서 뵙겠습니다!
