---
title: "2편: Feature 추출 및 매칭"
date: 2026-05-15T00:00:00+09:00
draft: false
tags: ["SfM", "OpenCV", "SIFT", "Feature Matching", "RANSAC"]
categories: ["Programming"]
description: "SIFT로 feature를 추출하고 BFMatcher + RANSAC으로 세 프레임 간 대응점을 찾습니다."
---

> 이전 편에서 로딩한 세 장의 이미지에서 대응점(correspondences)을 찾습니다. 이 대응점이 이후 모든 기하학적 계산의 입력이 됩니다.

## Feature란

SfM에서 "feature"는 이미지 내에서 여러 시점에서도 안정적으로 찾을 수 있는 특징점입니다. 좋은 feature는:

- 회전, 스케일, 밝기 변화에 강인(robust)해야 하고
- 다른 feature와 구별되는 고유한 descriptor를 가져야 합니다

## SIFT

SIFT(Scale-Invariant Feature Transform)는 가장 검증된 feature 알고리즘입니다. ORB보다 느리지만 매칭 품질이 훨씬 좋아 SfM에 적합합니다.

SIFT는 각 keypoint에 대해 128차원 descriptor 벡터를 생성합니다. 두 이미지의 descriptor 사이의 거리가 가까울수록 같은 3D 점일 가능성이 높습니다.

## Feature 추출

```python
import cv2
import numpy as np

def extract_features(images: dict) -> dict:
    sift = cv2.SIFT_create(nfeatures=5000)
    features = {}
    for name, img in images.items():
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kps, descs = sift.detectAndCompute(gray, None)
        features[name] = {'kps': kps, 'descs': descs}
        print(f"{name}: {len(kps)} keypoints")
    return features
```

## Feature 매칭

두 이미지 간 descriptor를 비교해 가장 비슷한 쌍을 찾습니다. Lowe's ratio test로 애매한 매칭을 걸러냅니다.

$$\frac{d_1}{d_2} < 0.75 \implies \text{좋은 매칭}$$

가장 가까운 거리($d_1$)가 두 번째로 가까운 거리($d_2$)보다 충분히 작을 때만 신뢰합니다.

```python
def match_features(feat_a: dict, feat_b: dict) -> list:
    bf = cv2.BFMatcher(cv2.NORM_L2)
    raw = bf.knnMatch(feat_a['descs'], feat_b['descs'], k=2)

    # Lowe's ratio test
    good = []
    for m, n in raw:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    return good
```

## RANSAC으로 Outlier 제거

Lowe's ratio test를 통과해도 잘못된 매칭(outlier)이 남습니다. Fundamental Matrix를 이용한 RANSAC으로 기하학적으로 일관된 매칭만 남깁니다.

RANSAC의 핵심 아이디어:
1. 매칭 중 임의로 8개를 샘플링해 Fundamental Matrix 추정
2. 나머지 매칭이 이 행렬과 얼마나 일치하는지 확인 (inlier 수 측정)
3. 반복 후 inlier가 가장 많은 결과 선택

```python
def filter_matches_ransac(feat_a, feat_b, matches, threshold=3.0):
    pts_a = np.float32([feat_a['kps'][m.queryIdx].pt for m in matches])
    pts_b = np.float32([feat_b['kps'][m.trainIdx].pt for m in matches])

    # ETH3D는 6K 고해상도이므로 threshold를 여유있게 3.0 정도로 설정합니다.
    F, mask = cv2.findFundamentalMat(
        pts_a, pts_b,
        method=cv2.FM_RANSAC,
        ransacReprojThreshold=threshold,
        confidence=0.999
    )

    inlier_mask = mask.ravel().astype(bool)
    pts_a_in = pts_a[inlier_mask]
    pts_b_in = pts_b[inlier_mask]
    print(f"  RANSAC: {inlier_mask.sum()} / {len(matches)} inliers")
    return pts_a_in, pts_b_in, F
```

## 세 프레임 쌍 매칭

3-view SfM에서는 (1↔2), (2↔3), (1↔3) 세 쌍을 모두 매칭합니다.

```python
# 1편에서 로딩한 데이터 사용
img_names = sorted(poses.keys())[:3]
name0, name1, name2 = img_names

features = extract_features(images)

# 쌍별 매칭
raw_01 = match_features(features[name0], features[name1])
raw_12 = match_features(features[name1], features[name2])
raw_02 = match_features(features[name0], features[name2])

pts0_1, pts1_0, F01 = filter_matches_ransac(features[name0], features[name1], raw_01)
pts1_2, pts2_1, F12 = filter_matches_ransac(features[name1], features[name2], raw_12)
pts0_2, pts2_0, F02 = filter_matches_ransac(features[name0], features[name2], raw_02)
```

## 매칭 시각화

```python
def visualize_matches(img_a, img_b, pts_a, pts_b, max_show=100):
    # 시각화용 DMatch 객체 생성
    kps_a = [cv2.KeyPoint(p[0], p[1], 1) for p in pts_a[:max_show]]
    kps_b = [cv2.KeyPoint(p[0], p[1], 1) for p in pts_b[:max_show]]
    dmatches = [cv2.DMatch(i, i, 0) for i in range(len(kps_a))]

    vis = cv2.drawMatches(img_a, kps_a, img_b, kps_b, dmatches, None,
                          flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imwrite("matches_01.jpg", vis)
```

---

## 다음 편 예고

찾은 대응점 `pts0_1`, `pts1_0`을 이용해 Essential Matrix를 구하고 카메라 1, 2의 상대 pose (R, t)를 복원합니다.
