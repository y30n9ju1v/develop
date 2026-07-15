---
title: "6. 동시성과 병렬성: 독립적인 작업을 효율적으로"
date: 2026-07-15T00:00:00+09:00
draft: false
tags: ["functional-programming", "python", "concurrency", "book"]
categories: ["books"]
description: "Applicative Functor로 독립적인 작업을 병렬 실행하고 결과를 조합하는 원리 — asyncio.gather의 철학을 다룹니다."
---


지금까지 우리는 주로 **순차적인** 비동기 작업을 다뤘습니다. 4장의 `Monad`와 `flatMap`, 그리고 5장의 `Result`와 에러 처리는 모두 "이 작업이 끝나면, 그 결과를 가지고 다음 작업을 수행하라"는 순차적 흐름을 다루는 도구였습니다. 사용자를 조회하고, 그 결과로 게시글을 조회하는 것처럼 말이죠.

하지만 실무에서는 서로 **독립적인** 여러 작업을 동시에 수행하고 싶을 때가 많습니다. 다섯 명의 사용자 정보를 가져올 때, 한 명씩 순차적으로 조회할 이유가 없습니다. 각 조회는 완전히 독립적이므로 동시에 실행할 수 있고, 그렇게 하면 훨씬 빠릅니다. 이 장에서는 독립적인 비동기 작업을 **병렬**로 실행하고, 그 결과를 조합하는 `Applicative Functor`의 개념을 배울 것입니다. 이는 성능 최적화의 핵심입니다.

## 1-5장에서 배운 것들

먼저 여기까지의 여정을 복습해봅시다.

**1장: 함수형 프로그래밍의 철학**
- **합성(Composition)**: `compose(f, g)` - 작은 함수를 조합해서 큰 함수 만들기
- **참조 투명성(Referential Transparency)**: 같은 입력 → 같은 출력, 부작용 없음

**2장: 문제의 발견**
- **블로킹은 부수 효과를 가집니다**: 실행 시간이 예측 불가능
- **콜백은 합성이 불가능합니다**: 중첩만 가능, 조합 불가능
- **해답**: 미래의 값을 타입(Future)으로 표현하기

**3장: Functor - 독립적 변환의 합성**
- **map**: 컨텍스트 안의 값을 변환하되 컨텍스트 유지
- **한계**: map 안에서 또 다른 컨텍스트를 반환하면 중첩 발생

**4장: Monad - 의존적 합성의 해결**
- **flatMap**: 의존적 작업의 순차 합성 - 첫 번째 결과에 따라 두 번째 작업 결정
- **결론**: `await`는 flatMap의 문법적 설탕

**5장: Result - 실패를 합성 가능하게**
- **Result[T, E]**: 성공과 실패를 타입으로 표현
- **Railway-Oriented Programming**: 에러도 flatMap으로 우아하게 전파

**6장: 동시성과 병렬성 - 독립적 작업의 병렬 합성**

4장의 flatMap은 **순차 합성**이었습니다. "A가 끝나면 B 시작"의 패턴이죠. 하지만 A와 B가 서로 독립적이라면? 동시에 실행하면 더 빠를 것입니다. 이 장에서는 **병렬 합성** - 여러 독립적인 작업을 동시에 실행하고 결과를 조합하는 방법을 배웁니다. 이것이 바로 **Applicative Functor**의 핵심입니다.

## 문제의 발견: 불필요한 순차 실행

간단한 상황을 생각해봅시다. 날씨 정보 대시보드를 만들고 있고, 세 개의 서로 다른 API에서 데이터를 가져와야 합니다. 현재 날씨, 일주일 예보, 대기질 정보입니다. 각 API는 약 1초가 걸립니다.

순차적으로 작성하면 이렇게 됩니다.

```python
import asyncio
import time

async def fetch_current_weather(city: str) -> dict:
    """현재 날씨를 가져옵니다"""
    print(f"  현재 날씨 조회 시작: {city}")
    await asyncio.sleep(1)  # API 호출 시뮬레이션
    print(f"  현재 날씨 조회 완료: {city}")
    return {"temp": 22, "condition": "맑음"}

async def fetch_weekly_forecast(city: str) -> list:
    """주간 예보를 가져옵니다"""
    print(f"  주간 예보 조회 시작: {city}")
    await asyncio.sleep(1)  # API 호출 시뮬레이션
    print(f"  주간 예보 조회 완료: {city}")
    return [{"day": "월", "temp": 20}, {"day": "화", "temp": 21}]

async def fetch_air_quality(city: str) -> dict:
    """대기질 정보를 가져옵니다"""
    print(f"  대기질 조회 시작: {city}")
    await asyncio.sleep(1)  # API 호출 시뮬레이션
    print(f"  대기질 조회 완료: {city}")
    return {"aqi": 50, "status": "좋음"}

async def get_weather_dashboard_sequential(city: str) -> dict:
    """날씨 대시보드 데이터를 순차적으로 가져옵니다"""
    print(f"=== 순차 실행 시작: {city} ===")
    start = time.time()
    
    current = await fetch_current_weather(city)
    forecast = await fetch_weekly_forecast(city)
    air = await fetch_air_quality(city)
    
    elapsed = time.time() - start
    print(f"=== 순차 실행 완료: {elapsed:.2f}초 ===\n")
    
    return {
        "current": current,
        "forecast": forecast,
        "air_quality": air
    }

# 실행
result = asyncio.run(get_weather_dashboard_sequential("서울"))
```

실행하면 이렇게 출력됩니다.

```
=== 순차 실행 시작: 서울 ===
  현재 날씨 조회 시작: 서울
  현재 날씨 조회 완료: 서울
  주간 예보 조회 시작: 서울
  주간 예보 조회 완료: 서울
  대기질 조회 시작: 서울
  대기질 조회 완료: 서울
=== 순차 실행 완료: 3.01초 ===
```

총 3초가 걸렸습니다. 하지만 잠깐 생각해보세요. 세 API 호출은 서로 완전히 독립적입니다. 현재 날씨를 알기 위해 주간 예보를 먼저 알 필요가 없습니다. 대기질도 마찬가지입니다. 우리는 불필요하게 순차적으로 기다리고 있는 것입니다.

이것은 마치 세 가지 요리를 주문했는데, 첫 번째 요리가 완전히 나올 때까지 두 번째 요리를 만들기 시작하지 않는 것과 같습니다. 세 요리가 서로 관련이 없다면, 세 명의 요리사가 동시에 만들 수 있을 것입니다.

## asyncio.gather: 병렬 실행의 시작

파이썬의 asyncio는 여러 코루틴을 동시에 실행하는 간단한 방법을 제공합니다. asyncio.gather입니다.

```python
async def get_weather_dashboard_parallel(city: str) -> dict:
    """날씨 대시보드 데이터를 병렬로 가져옵니다"""
    print(f"=== 병렬 실행 시작: {city} ===")
    start = time.time()
    
    # 세 코루틴을 동시에 시작하고 모두 완료될 때까지 기다립니다
    current, forecast, air = await asyncio.gather(
        fetch_current_weather(city),
        fetch_weekly_forecast(city),
        fetch_air_quality(city)
    )
    
    elapsed = time.time() - start
    print(f"=== 병렬 실행 완료: {elapsed:.2f}초 ===\n")
    
    return {
        "current": current,
        "forecast": forecast,
        "air_quality": air
    }

# 실행
result = asyncio.run(get_weather_dashboard_parallel("서울"))
```

실행하면 놀라운 일이 일어납니다.

```
=== 병렬 실행 시작: 서울 ===
  현재 날씨 조회 시작: 서울
  주간 예보 조회 시작: 서울
  대기질 조회 시작: 서울
  현재 날씨 조회 완료: 서울
  주간 예보 조회 완료: 서울
  대기질 조회 완료: 서울
=== 병렬 실행 완료: 1.00초 ===
```

세 작업이 거의 동시에 시작되고, 거의 동시에 완료됩니다. 총 소요 시간은 1초입니다. 순차 실행의 3초에 비해 3배 빠릅니다. 이것이 병렬 실행의 힘입니다.

asyncio.gather가 하는 일을 정확히 이해해봅시다. gather는 여러 개의 코루틴을 인자로 받아서, 각 코루틴을 즉시 Task로 만들어 실행을 시작합니다. 그리고 모든 Task가 완료될 때까지 기다렸다가, 결과들을 튜플로 반환합니다. 결과의 순서는 코루틴을 전달한 순서와 같습니다. 완료 순서와는 관계없이 말이죠.

좀 더 많은 작업을 병렬로 실행해봅시다. 여러 도시의 날씨를 동시에 조회하는 경우입니다.

```python
async def fetch_multiple_cities_sequential(cities: list[str]) -> dict:
    """여러 도시의 날씨를 순차적으로 조회합니다"""
    print(f"=== 순차: {len(cities)}개 도시 조회 시작 ===")
    start = time.time()
    
    results = {}
    for city in cities:
        results[city] = await fetch_current_weather(city)
    
    elapsed = time.time() - start
    print(f"=== 순차: 완료 ({elapsed:.2f}초) ===\n")
    return results

async def fetch_multiple_cities_parallel(cities: list[str]) -> dict:
    """여러 도시의 날씨를 병렬로 조회합니다"""
    print(f"=== 병렬: {len(cities)}개 도시 조회 시작 ===")
    start = time.time()
    
    # 각 도시에 대한 코루틴 리스트를 만듭니다
    tasks = [fetch_current_weather(city) for city in cities]
    
    # 모두 병렬로 실행합니다
    results_list = await asyncio.gather(*tasks)
    
    # 도시 이름과 결과를 매핑합니다
    results = dict(zip(cities, results_list))
    
    elapsed = time.time() - start
    print(f"=== 병렬: 완료 ({elapsed:.2f}초) ===\n")
    return results

# 테스트
cities = ["서울", "부산", "대구", "인천", "광주"]

# 순차 실행: 5초
# result_seq = asyncio.run(fetch_multiple_cities_sequential(cities))

# 병렬 실행: 1초
result_par = asyncio.run(fetch_multiple_cities_parallel(cities))
```

다섯 개 도시를 순차적으로 조회하면 5초가 걸리지만, 병렬로 조회하면 1초만 걸립니다. 작업이 많을수록 병렬 실행의 이점은 더욱 커집니다.

## 순차와 병렬의 구분: 의존성이 핵심

그렇다면 언제 순차적으로 실행하고, 언제 병렬로 실행해야 할까요? 핵심은 의존성입니다. 한 작업이 다른 작업의 결과를 필요로 하면 순차적으로 실행해야 하고, 작업들이 서로 독립적이면 병렬로 실행할 수 있습니다.

### 의존성의 세 가지 종류

의존성을 판단할 때 세 가지 측면을 고려해야 합니다.

**1. 데이터 의존성**: A의 결과가 B의 입력으로 필요한가?
```python
# 데이터 의존성 있음 → 순차 실행 필수
user = await fetch_user(user_id)
posts = await fetch_posts(user["id"])  # user의 id가 필요
```

**2. 순서 의존성**: A가 B보다 먼저 완료되어야 하는가?
```python
# 순서 의존성 있음 → 순차 실행 필수
await create_directory("/data")
await write_file("/data/config.json", config)  # 디렉토리가 먼저 존재해야 함
```

**3. 부작용 의존성**: A의 부작용이 B에 영향을 주는가?
```python
# 부작용 의존성 있음 → 순차 실행 필수
await update_balance(account_id, -100)  # 잔액 차감
await check_balance(account_id)  # 차감된 잔액을 확인해야 함
```

세 가지 의존성 중 하나라도 있으면 순차 실행이 필요하고, 모두 없으면 병렬 실행이 가능합니다.

간단한 질문으로 판단할 수 있습니다. 이 작업을 시작하기 위해 저 작업의 결과가 필요한가요? 필요하다면 순차적으로, 필요하지 않다면 병렬로 실행할 수 있습니다.

예를 들어봅시다. 사용자 정보를 조회하고, 그 사용자의 게시글과 친구 목록을 가져오는 경우입니다.

```python
async def fetch_user(user_id: int) -> dict:
    """사용자 정보를 조회합니다"""
    await asyncio.sleep(1)
    return {"id": user_id, "name": f"사용자{user_id}"}

async def fetch_user_posts(user_id: int) -> list:
    """사용자의 게시글을 조회합니다"""
    await asyncio.sleep(1)
    return [{"title": f"게시글{i}"} for i in range(3)]

async def fetch_user_friends(user_id: int) -> list:
    """사용자의 친구 목록을 조회합니다"""
    await asyncio.sleep(1)
    return [{"name": f"친구{i}"} for i in range(5)]

async def get_user_profile(user_id: int) -> dict:
    """사용자 프로필을 가져옵니다"""
    # 1단계: 사용자 정보를 먼저 가져와야 합니다 (순차)
    user = await fetch_user(user_id)
    
    # 2단계: 게시글과 친구는 독립적이므로 병렬로 가져올 수 있습니다
    posts, friends = await asyncio.gather(
        fetch_user_posts(user["id"]),
        fetch_user_friends(user["id"])
    )
    
    return {
        "user": user,
        "posts": posts,
        "friends": friends
    }

# 실행
start = time.time()
profile = asyncio.run(get_user_profile(123))
print(f"총 소요 시간: {time.time() - start:.2f}초")
# 총 2초: 사용자 조회(1초) + 병렬로 게시글과 친구 조회(1초)
```

이 코드는 순차와 병렬을 적절히 섞어서 사용합니다. 사용자 정보를 먼저 가져와야 user_id를 알 수 있으므로 이것은 순차적입니다. 하지만 일단 user_id를 얻으면, 게시글과 친구 목록은 서로 독립적이므로 병렬로 가져올 수 있습니다.

만약 모든 것을 순차적으로 실행했다면 3초가 걸렸을 것입니다. 하지만 병렬 실행을 활용해서 2초로 줄였습니다. 이것은 작지만 의미 있는 최적화입니다. 사용자 경험 측면에서 1초의 차이는 크게 느껴질 수 있습니다.

## 이론적 배경: Applicative Functor

이론적으로 말하면, asyncio.gather는 Applicative Functor의 개념을 구현한 것입니다. Applicative는 Functor와 Monad 사이에 있는 추상화입니다.

### Functor < Applicative < Monad 계층 구조

함수형 프로그래밍에서 이 세 가지는 계층 구조를 이룹니다. 각각이 제공하는 능력이 다릅니다.

```
Functor     →  map:     (A → B) → F[A] → F[B]
                        "컨텍스트 안의 값을 변환"

Applicative →  ap:      F[A → B] → F[A] → F[B]
               pure:    A → F[A]
                        "여러 독립적인 컨텍스트를 결합"

Monad       →  flatMap: (A → F[B]) → F[A] → F[B]
                        "의존적인 컨텍스트를 순차 연결"
```

**Functor**는 map만 제공합니다. 컨텍스트 안의 값을 변환할 수 있지만, 여러 컨텍스트를 조합할 수는 없습니다.

**Applicative**는 여기에 ap(apply)와 pure를 추가합니다. 여러 독립적인 컨텍스트를 결합할 수 있습니다. 하지만 한 작업의 결과에 따라 다음 작업을 결정할 수는 없습니다.

**Monad**는 flatMap을 추가합니다. 한 작업의 결과로 다음 작업을 결정할 수 있습니다. 가장 강력하지만, 순차적입니다.

### 왜 Monad가 아닌 Applicative를 쓰나요?

Monad가 더 강력한데 왜 Applicative를 쓸까요? **Monad는 순차적이기 때문입니다.**

```python
# Monad (flatMap/await): 순차 실행 강제
# user를 가져와야만 posts를 가져올 수 있다고 가정합니다 (의존적)
user = await fetch_user(user_id)      # 1초
posts = await fetch_posts(user_id)    # 1초 (user 완료 후 시작)
comments = await fetch_comments(user_id)  # 1초 (posts 완료 후 시작)
# 총 3초

# Applicative (gather): 병렬 실행 가능
# 세 작업이 서로 독립적이라면 동시에 실행할 수 있습니다 (독립적)
user, posts, comments = await asyncio.gather(
    fetch_user(user_id),      # 1초
    fetch_posts(user_id),     # 1초 (동시 시작)
    fetch_comments(user_id)   # 1초 (동시 시작)
)
# 총 1초
```

flatMap은 "이전 결과를 사용해서 다음 작업 결정"이라는 의미를 가지므로, 컴파일러/런타임은 순차 실행할 수밖에 없습니다. 반면 Applicative의 ap는 **"독립적인 작업들의 결합"**이므로, 병렬 실행이 가능합니다. 이 "독립성"이 바로 성능 최적화의 열쇠입니다. 작업들 사이에 의존성이 없다면, 우리는 그것들을 동시에 실행하여 시간을 절약할 수 있습니다.

### Python에서의 Applicative

파이썬에는 Applicative를 위한 전용 문법(`ap` 연산자 등)이 없지만, `asyncio.gather`가 그 역할을 완벽하게 수행합니다.

`gather`는 여러 개의 Future를 받아서, 그것들을 동시에 실행하고(병렬성), 모든 결과를 모아서 하나의 Future로 반환합니다(조합). 이것이 바로 Applicative Functor의 핵심인 **"독립적인 컨텍스트들의 결합"**입니다.


### Monad vs Applicative: 핵심 차이

| 측면 | Monad (flatMap) | Applicative (gather) |
|------|-----------------|---------------------|
| **실행 방식** | 순차적 | 병렬 가능 |
| **의존성** | 이전 결과에 의존 가능 | 독립적이어야 함 |
| **표현력** | 더 강력 | 더 제한적 |
| **성능** | 순차로 인한 지연 | 병렬로 성능 향상 |
| **Python 문법** | `await` 연쇄 | `asyncio.gather` |

**핵심 통찰**: 작업이 독립적이라면 Applicative(gather)를 사용하세요. 의존적이라면 Monad(await 연쇄)를 사용하세요. 이 구분이 성능 최적화의 핵심입니다.

## asyncio.gather의 세부 사항

asyncio.gather는 몇 가지 유용한 옵션을 제공합니다. 가장 중요한 것은 return_exceptions 파라미터입니다.

```python
async def task_success() -> str:
    """성공하는 작업"""
    await asyncio.sleep(0.5)
    return "성공"

async def task_failure() -> str:
    """실패하는 작업"""
    await asyncio.sleep(0.5)
    raise ValueError("의도적인 에러")

async def test_gather_default():
    """기본 동작: 하나라도 실패하면 예외 발생"""
    print("=== 기본 gather ===")
    try:
        results = await asyncio.gather(
            task_success(),
            task_failure(),
            task_success()
        )
        print(f"결과: {results}")
    except ValueError as e:
        print(f"예외 발생: {e}")
    print()

async def test_gather_return_exceptions():
    """return_exceptions=True: 예외를 결과로 반환"""
    print("=== return_exceptions=True ===")
    results = await asyncio.gather(
        task_success(),
        task_failure(),
        task_success(),
        return_exceptions=True
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"작업 {i}: 예외 - {result}")
        else:
            print(f"작업 {i}: 성공 - {result}")
    print()

# 실행
asyncio.run(test_gather_default())
# 예외 발생: 의도적인 에러

asyncio.run(test_gather_return_exceptions())
# 작업 0: 성공 - 성공
# 작업 1: 예외 - 의도적인 에러
# 작업 2: 성공 - 성공
```

기본적으로 gather는 하나라도 실패하면 즉시 예외를 발생시킵니다. 이것은 보통 원하는 동작입니다. 모든 작업이 성공해야만 의미가 있을 때 사용합니다.

하지만 때로는 일부 작업이 실패해도 다른 작업의 결과를 받고 싶을 때가 있습니다. 예를 들어, 여러 소스에서 데이터를 가져오는데 일부가 실패해도 가능한 것들은 보여주고 싶은 경우입니다. 이럴 때 `return_exceptions=True`를 사용합니다.

**주의: `return_exceptions=True`를 사용할 때는 반드시 결과 타입을 확인해야 합니다!**
반환된 리스트에는 성공한 값과 예외 객체(`Exception`)가 섞여 있습니다.

```python
results = await asyncio.gather(task1(), task2(), return_exceptions=True)
valid_results = [
    r for r in results 
    if not isinstance(r, Exception)
]  # 예외 필터링 필수
```

gather의 또 다른 특징은 취소입니다. gather를 취소하면 모든 하위 Task가 취소됩니다.

```python
async def long_task(name: str, duration: float) -> str:
    """오래 걸리는 작업"""
    try:
        print(f"{name} 시작")
        await asyncio.sleep(duration)
        print(f"{name} 완료")
        return f"{name} 결과"
    except asyncio.CancelledError:
        print(f"{name} 취소됨")
        raise

async def test_gather_cancellation():
    """gather 취소 테스트"""
    print("=== gather 취소 ===")
    
    # gather를 Task로 만듭니다
    gather_task = asyncio.create_task(
        asyncio.gather(
            long_task("작업A", 3),
            long_task("작업B", 3),
            long_task("작업C", 3)
        )
    )
    
    # 1초 후에 취소합니다
    await asyncio.sleep(1)
    gather_task.cancel()
    
    try:
        await gather_task
    except asyncio.CancelledError:
        print("gather가 취소되었습니다")
    
    # 모든 작업이 취소되었는지 확인하기 위해 조금 대기
    await asyncio.sleep(0.5)

# 실행
asyncio.run(test_gather_cancellation())
# 작업A 시작
# 작업B 시작
# 작업C 시작
# 작업A 취소됨
# 작업B 취소됨
# 작업C 취소됨
# gather가 취소되었습니다
```

gather를 취소하면 아직 완료되지 않은 모든 Task가 취소됩니다. 이것은 타임아웃을 구현할 때 유용합니다.

## Python 3.11의 TaskGroup: 구조적 동시성 (Structured Concurrency)

지금까지 배운 `create_task`나 `gather`는 편리하지만, 한 가지 문제가 있습니다. 작업의 **생명주기(Lifecycle)**가 명확하지 않다는 점입니다. `create_task`로 만든 Task는 "Fire-and-forget" 방식으로, 부모 코루틴이 끝나도 계속 살아있을 수 있습니다. 이는 "dangling future" 문제를 일으키고, 자원 누수의 원인이 됩니다.

함수형 프로그래밍에서는 항상 **스코프(Scope)**를 중요하게 생각합니다. 어떤 자원이나 작업은 특정 범위 안에서만 유효해야 합니다. Python 3.11에서 도입된 `TaskGroup`은 바로 이 개념을 구현한 것입니다.

```python
async def fetch_user_data(user_id: int):
    async with asyncio.TaskGroup() as tg:
        # 이 블록 안에서 생성된 task들은 tg에 속합니다
        task1 = tg.create_task(fetch_user(user_id))
        task2 = tg.create_task(fetch_user_posts(user_id))
    
    # 블록을 벗어나는 순간, 모든 task가 완료되었음이 보장됩니다.
    # [중요] 만약 task1에서 예외가 발생하면, task2는 즉시 자동으로 취소(Cancel)됩니다.
    # 예외는 블록 밖으로 전파됩니다. 이것이 바로 "구조적 동시성"입니다.
    return task1.result(), task2.result()
```

이 패턴은 함수형 프로그래밍의 **Bracket Pattern** (자원 할당 -> 사용 -> 해제)과 일맥상통하며, 비동기 작업의 흐름을 훨씬 예측 가능하게 만듭니다. **함수형 언어에서 "부작용의 범위(Scope of side-effects)"를 엄격하게 제한하는 철학이, 비동기 프로그래밍에서는 "작업의 생명주기(Lifecycle of tasks)"를 엄격하게 제한하는 구조적 동시성으로 발전한 것입니다.**

최신 Python(3.11+)을 사용한다면 `gather`보다 `TaskGroup`을 사용하는 것이 더 안전하고 함수형적인 방식입니다. TaskGroup은 컨텍스트 매니저로 작업의 생명주기를 명확히 하고, 예외 처리를 자동화하며, 작업 누수를 방지합니다.

## asyncio.wait: 더 세밀한 제어

asyncio.gather는 간단하고 사용하기 쉽지만, 때로는 더 세밀한 제어가 필요합니다. asyncio.wait는 더 저수준의 API로, 다양한 대기 전략을 제공합니다.

```python
async def worker(name: str, duration: float) -> str:
    """작업을 수행합니다"""
    await asyncio.sleep(duration)
    return f"{name} 완료 ({duration}초)"

async def test_wait_all():
    """모든 작업이 완료될 때까지 기다립니다 (gather와 유사)"""
    print("=== WAIT: ALL_COMPLETED ===")
    
    tasks = [
        asyncio.create_task(worker("작업1", 1)),
        asyncio.create_task(worker("작업2", 2)),
        asyncio.create_task(worker("작업3", 0.5))
    ]
    
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    
    print(f"완료된 작업: {len(done)}")
    print(f"대기 중인 작업: {len(pending)}")
    
    for task in done:
        print(f"  결과: {task.result()}")
    print()

async def test_wait_first():
    """첫 번째 작업이 완료되면 반환합니다"""
    print("=== WAIT: FIRST_COMPLETED ===")
    
    tasks = [
        asyncio.create_task(worker("작업1", 2)),
        asyncio.create_task(worker("작업2", 3)),
        asyncio.create_task(worker("작업3", 1))  # 가장 빨리 완료됨
    ]
    
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    
    print(f"완료된 작업: {len(done)}")
    print(f"대기 중인 작업: {len(pending)}")
    
    for task in done:
        print(f"  첫 완료: {task.result()}")
    
    # 나머지 작업 취소
    for task in pending:
        task.cancel()
    print()

async def test_wait_first_exception():
    """첫 번째 예외가 발생하면 반환합니다"""
    print("=== WAIT: FIRST_EXCEPTION ===")
    
    async def failing_task():
        await asyncio.sleep(1)
        raise ValueError("에러!")
    
    tasks = [
        asyncio.create_task(worker("작업1", 3)),
        asyncio.create_task(failing_task()),
        asyncio.create_task(worker("작업2", 3))
    ]
    
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    
    print(f"완료된 작업: {len(done)}")
    print(f"대기 중인 작업: {len(pending)}")
    
    for task in done:
        if task.exception():
            print(f"  예외: {task.exception()}")
        else:
            print(f"  결과: {task.result()}")
    
    for task in pending:
        task.cancel()
    print()

# 실행
asyncio.run(test_wait_all())
asyncio.run(test_wait_first())
asyncio.run(test_wait_first_exception())
```

asyncio.wait는 두 개의 집합을 반환합니다. 완료된 Task들(done)과 아직 대기 중인 Task들(pending)입니다. return_when 파라미터로 언제 반환할지 제어할 수 있습니다. ALL_COMPLETED는 모두 완료될 때까지 기다리고, FIRST_COMPLETED는 첫 번째가 완료되면 즉시 반환하고, FIRST_EXCEPTION은 첫 번째 예외가 발생하면 반환합니다.

FIRST_COMPLETED는 경쟁(race) 패턴을 구현할 때 유용합니다. 여러 소스에서 데이터를 가져오는데 가장 빨리 응답하는 것만 사용하고 싶을 때 사용할 수 있습니다. 나머지 작업은 취소하면 됩니다.

## asyncio.as_completed: 완료 순서대로 처리

gather와 wait 외에도 asyncio.as_completed는 완료되는 순서대로 결과를 처리할 때 유용합니다.

```python
import random

async def fetch_with_timing(url: str) -> tuple[str, float]:
    """URL을 가져오고 소요 시간을 반환합니다"""
    start = time.time()
    await asyncio.sleep(random.uniform(0.5, 2.0))  # 시뮬레이션
    elapsed = time.time() - start
    return url, elapsed

async def process_as_completed():
    """완료되는 순서대로 처리합니다"""
    urls = [f"https://api.example.com/item{i}" for i in range(5)]

    # 코루틴들을 생성합니다
    coros = [fetch_with_timing(url) for url in urls]

    # 완료되는 순서대로 처리합니다
    for coro in asyncio.as_completed(coros):
        url, elapsed = await coro
        print(f"완료: {url} ({elapsed:.2f}초)")
        # 결과를 즉시 처리할 수 있습니다

# 실행하면 빨리 완료되는 것부터 출력됩니다
# 완료: https://api.example.com/item3 (0.52초)
# 완료: https://api.example.com/item1 (0.78초)
# 완료: https://api.example.com/item4 (1.23초)
# ...
```

as_completed의 장점은 결과를 기다리는 동안 이미 완료된 작업을 먼저 처리할 수 있다는 것입니다. 예를 들어, 검색 결과를 사용자에게 점진적으로 보여주고 싶을 때 유용합니다.

| API | 반환 시점 | 결과 순서 | 용도 |
|-----|----------|----------|------|
| `gather` | 모두 완료 | 입력 순서 | 모든 결과가 필요할 때 |
| `wait` | 조건 충족 시 | 완료/대기 분리 | 세밀한 제어가 필요할 때 |
| `as_completed` | 하나씩 완료 | 완료 순서 | 점진적 처리가 필요할 때 |

```python
async def fetch_from_backup_sources(url: str) -> str:
    """여러 백업 소스에서 데이터를 가져옵니다"""
    sources = [
        f"https://primary.com{url}",
        f"https://backup1.com{url}",
        f"https://backup2.com{url}"
    ]
    
    async def fetch_with_timeout(source: str) -> str:
        # 실제로는 aiohttp 등을 사용합니다
        await asyncio.sleep(1)  # 시뮬레이션
        return f"데이터 from {source}"
    
    tasks = [asyncio.create_task(fetch_with_timeout(src)) for src in sources]
    
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    
    # 첫 번째 결과를 가져옵니다
    result = next(iter(done)).result()
    
    # 나머지 작업을 취소합니다
    for task in pending:
        task.cancel()
    
    return result
```

이 패턴은 고가용성 시스템에서 자주 사용됩니다. 여러 백업 서버에 동시에 요청을 보내고, 가장 빨리 응답하는 것을 사용합니다.



## 동시 접속 수 제한: Semaphore

실무에서는 무제한으로 병렬 작업을 실행할 수 없습니다. 서버가 과부하되거나, 메모리가 부족하거나, API의 rate limit에 걸릴 수 있습니다. 동시 접속 수를 제한해야 할 때 Semaphore를 사용합니다.

```python
async def fetch_url_limited(url: str, semaphore: asyncio.Semaphore) -> str:
    """동시 접속 수가 제한된 URL 가져오기"""
    async with semaphore:
        # semaphore를 획득했습니다. 최대 N개만 이 블록에 동시 진입 가능
        print(f"  요청 시작: {url}")
        await asyncio.sleep(1)  # 실제 HTTP 요청
        print(f"  요청 완료: {url}")
        return f"내용 from {url}"

async def crawl_with_limit(urls: list[str], max_concurrent: int) -> list[str]:
    """동시 접속 수를 제한하면서 크롤링합니다"""
    print(f"=== 최대 {max_concurrent}개 동시 실행 ===")
    start = time.time()
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    tasks = [fetch_url_limited(url, semaphore) for url in urls]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"=== 완료: {elapsed:.2f}초 ===\n")
    return results

# 10개 URL을 크롤링
urls = [f"https://example.com/page{i}" for i in range(10)]

# 무제한으로 실행하면 모두 동시에 시작됩니다 (1초)
# result = asyncio.run(crawl_with_limit(urls, 10))

# 최대 3개로 제한하면 3개씩 실행됩니다 (4초: 3+3+3+1)
result = asyncio.run(crawl_with_limit(urls, 3))
```

Semaphore는 카운터입니다. 생성할 때 최대 개수를 지정하고, async with으로 획득을 시도합니다. 카운터가 0이면 대기하고, 0보다 크면 카운터를 감소시키고 진입합니다. 블록을 벗어나면 카운터를 증가시킵니다.

10개 URL을 크롤링하는데 최대 3개로 제한하면, 처음 3개가 시작되고, 하나가 완료되면 다음 것이 시작되는 식입니다. 총 4초가 걸립니다. 처음 3개가 1초, 다음 3개가 1초, 다음 3개가 1초, 마지막 1개가 1초입니다.

실제 크롤러에서는 Semaphore로 동시 접속 수를 제한하는 것이 필수입니다. API의 rate limit를 지키고, 서버에 부담을 주지 않기 위해서입니다.

## 실전 예제: 병렬 크롤러

모든 개념을 종합해서 실용적인 병렬 크롤러를 만들어봅시다. `Semaphore`로 동시 접속 수를 제어하고, `gather`로 병렬 실행하며, 결과와 에러를 수집합니다.

```python
import asyncio
import aiohttp
from typing import Optional
from dataclasses import dataclass

# 크롤링 결과를 담을 데이터 클래스
@dataclass
class CrawlResult:
    url: str
    content: Optional[str]
    status: int
    error: Optional[str]

class BatchCrawler:
    """동시성 제어가 포함된 배치 크롤러"""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        # 세마포어로 동시 실행 수 제한
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_one(self, session: aiohttp.ClientSession, url: str) -> CrawlResult:
        """하나의 URL을 안전하게 가져옵니다"""
        
        # 세마포어 획득 (제한된 인원만 입장 가능)
        async with self.semaphore:
            try:
                print(f"  크롤링 시작: {url}")
                async with session.get(url, timeout=5) as response:
                    content = await response.text()
                    return CrawlResult(url, content[:100], response.status, None)
            except Exception as e:
                return CrawlResult(url, None, 0, str(e))

    async def crawl_all(self, urls: list[str]) -> list[CrawlResult]:
        """모든 URL을 병렬로 크롤링합니다"""
        print(f"=== 배치 크롤링 시작 ({len(urls)}개 URL, 동시 {self.max_concurrent}개) ===")
        
        async with aiohttp.ClientSession() as session:
            # 모든 작업을 Task로 생성
            tasks = [self.fetch_one(session, url) for url in urls]
            
            # 병렬 실행 (하나가 실패해도 나머지는 계속 진행)
            # Applicative Functor 패턴!
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 예외가 그대로 반환될 수 있으므로 필터링
            final_results = []
            for r in results:
                if isinstance(r, CrawlResult):
                    final_results.append(r)
                else:
                    # gather 자체에서 발생한 예상치 못한 에러
                    final_results.append(CrawlResult("unknown", None, 0, str(r)))
            
            return final_results

# 사용 예제
async def main():
    crawler = BatchCrawler(max_concurrent=3)
    
    urls = [
        "https://example.com",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404", # 실패 케이스
        "https://nonexistent-domain.com", # 에러 케이스
        "https://httpbin.org/delay/2",    # 지연 케이스
    ]
    
    results = await crawler.crawl_all(urls)
    
    print("\n=== 결과 요약 ===")
    for res in results:
        status = "성공" if res.content else "실패"
        print(f"[{status}] {res.url} (상태: {res.status}, 에러: {res.error})")

# asyncio.run(main())
```

이 코드는 실무에서 바로 사용할 수 있는 패턴입니다.
1. **Semaphore**: 서버에 과부하를 주지 않도록 동시 요청 수를 제한합니다.
2. **gather**: 독립적인 요청들을 병렬로 실행하여 전체 시간을 단축합니다.
3. **CrawlResult**: 성공과 실패/에러를 일관된 객체로 반환하여 후처리를 쉽게 합니다.

만약 순차적으로 실행했다면 `delay/2` 때문에 최소 2초 이상 걸리고, 타임아웃까지 더해져 훨씬 느렸을 것입니다. 병렬 실행 덕분에 전체 시간은 가장 느린 요청(2초)과 비슷하게 걸립니다.

## 심화: 병렬 실행의 실전 주의점

병렬 실행은 성능을 극대화하지만, 잘못 사용하면 오히려 시스템을 마비시킬 수 있습니다. 실무에서 마주치는 함정들을 살펴봅시다.

### 1. gather의 메모리 폭발 위험

`asyncio.gather`는 매우 편리하지만, 대량의 작업을 한꺼번에 시작하면 메모리가 폭발할 수 있습니다.

```python
# ❌ 위험한 코드: 10만 개 Task를 한꺼번에 생성
urls = [f"https://example.com/item{i}" for i in range(100_000)]

# 메모리 폭발! 10만 개 Task 객체가 즉시 생성됨
results = await asyncio.gather(*[fetch(url) for url in urls])
```

**문제점**:
1. **메모리 사용량**: 각 Task는 코루틴 프레임, 스택, 콜백 리스트 등을 메모리에 유지합니다. 10만 개면 수백 MB~수 GB가 될 수 있습니다.
2. **Event Loop 부담**: Event Loop가 10만 개 Task를 스케줄링하려면 큐 관리 오버헤드가 기하급수적으로 증가합니다.
3. **네트워크 소켓 고갈**: OS는 동시에 열 수 있는 파일 디스크립터(socket 포함)에 제한이 있습니다 (보통 1024~65535).

**해결책: Semaphore로 동시 실행 수 제한**

```python
# ✅ 안전한 코드: Semaphore로 최대 100개만 동시 실행
async def fetch_with_limit(url: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await fetch(url)

semaphore = asyncio.Semaphore(100)  # 최대 100개
tasks = [fetch_with_limit(url, semaphore) for url in urls]
results = await asyncio.gather(*tasks)
```

이렇게 하면 10만 개 Task가 생성되지만, **실제로 동시에 실행되는 것은 100개**로 제한됩니다. 메모리는 여전히 10만 개 Task 만큼 사용되므로, 더 나은 방법은 **청크 단위 처리**입니다.

```python
# ✅ 더 나은 방법: 청크로 나누어 처리
async def fetch_in_chunks(urls: list[str], chunk_size: int = 100):
    results = []
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i:i + chunk_size]
        # 청크마다 gather 사용 → 메모리 사용량 일정
        chunk_results = await asyncio.gather(*[fetch(url) for url in chunk])
        results.extend(chunk_results)
    return results

results = await fetch_in_chunks(urls, chunk_size=100)
```

### 2. Semaphore 교착 상태 (Deadlock)

Semaphore는 잘못 사용하면 교착 상태를 일으킬 수 있습니다.

```python
# ⚠️ 교착 상태 위험: 중첩된 Semaphore
semaphore = asyncio.Semaphore(2)  # 최대 2개

async def outer_task(id: int):
    async with semaphore:
        print(f"Outer {id} 시작")
        # 내부에서 또 Semaphore 획득 시도!
        await inner_task(id)
        print(f"Outer {id} 완료")

async def inner_task(id: int):
    async with semaphore:  # 교착 위험!
        print(f"Inner {id} 실행")
        await asyncio.sleep(1)

# 교착 상태 발생!
# outer_task(1)과 outer_task(2)가 Semaphore를 모두 점유하면,
# 둘 다 inner_task에서 Semaphore 획득을 무한히 대기
await asyncio.gather(outer_task(1), outer_task(2), outer_task(3))
```

**시나리오**:
1. `outer_task(1)`과 `outer_task(2)`가 Semaphore를 획득 (남은 슬롯: 0)
2. 둘 다 `inner_task`에서 Semaphore 획득 시도 → 대기
3. 아무도 Semaphore를 해제하지 못함 → 영구 대기 (Deadlock)

**해결책 1: 재진입 가능 Semaphore 사용 (Python에는 없음)**

Python의 `asyncio.Semaphore`는 재진입이 불가능하므로, 수동으로 관리해야 합니다.

**해결책 2: Semaphore를 중첩하지 않기**

```python
# ✅ 좋은 설계: 최상위에서만 Semaphore 사용
async def outer_task(id: int, semaphore: asyncio.Semaphore):
    async with semaphore:
        print(f"Outer {id} 시작")
        await inner_task_no_semaphore(id)
        print(f"Outer {id} 완료")

async def inner_task_no_semaphore(id: int):
    # Semaphore 없이 작업만 수행
    print(f"Inner {id} 실행")
    await asyncio.sleep(1)
```

**해결책 3: 타임아웃 설정**

```python
# ✅ 타임아웃으로 교착 상태 감지
async def safe_task(id: int, semaphore: asyncio.Semaphore):
    try:
        async with asyncio.timeout(5):  # Python 3.11+
            async with semaphore:
                await do_work(id)
    except asyncio.TimeoutError:
        print(f"Task {id}: 타임아웃 (교착 상태 의심)")
```

### 3. CPU-bound와 I/O-bound 혼용의 함정

`asyncio`는 I/O-bound 작업에 최적화되어 있습니다. CPU-bound 작업을 섞으면 Event Loop가 블로킹됩니다.

```python
import hashlib

# ❌ 나쁜 예: CPU-bound 작업이 Event Loop 블로킹
async def compute_hash_bad(data: bytes) -> str:
    """CPU 집약적 작업 - Event Loop 블로킹!"""
    # hashlib은 CPU를 오래 점유 (await 없음!)
    for _ in range(10000):
        hash_obj = hashlib.sha256(data)
        hash_obj.update(b"salt")
    return hash_obj.hexdigest()

async def mixed_workload_bad():
    """I/O와 CPU를 혼합 - 성능 악화!"""
    # 10개 작업을 "병렬"로 실행한다고 생각하지만...
    tasks = [
        fetch_data_from_api("url1"),  # I/O-bound (1초)
        compute_hash_bad(b"data1"),   # CPU-bound (1초 BUT 블로킹!)
        fetch_data_from_api("url2"),  # I/O-bound (1초)
    ]

    results = await asyncio.gather(*tasks)
    # 예상: 1초 (병렬)
    # 실제: 3초 (순차!) - compute_hash_bad가 Event Loop 블로킹
```

**문제**: `compute_hash_bad`는 `await`가 없으므로, 실행 중에 다른 Task로 전환할 수 없습니다. Event Loop가 멈춥니다.

**해결책: CPU-bound 작업을 별도 스레드/프로세스로 분리**

```python
import concurrent.futures

# ✅ 좋은 예: CPU-bound를 ThreadPoolExecutor로 분리
def compute_hash_sync(data: bytes) -> str:
    """동기 함수 (블로킹 OK)"""
    for _ in range(10000):
        hash_obj = hashlib.sha256(data)
        hash_obj.update(b"salt")
    return hash_obj.hexdigest()

async def compute_hash_good(data: bytes) -> str:
    """asyncio.to_thread로 Event Loop 블로킹 회피"""
    # Python 3.9+: asyncio.to_thread
    return await asyncio.to_thread(compute_hash_sync, data)

async def mixed_workload_good():
    """I/O와 CPU를 올바르게 혼합"""
    tasks = [
        fetch_data_from_api("url1"),  # I/O-bound
        compute_hash_good(b"data1"),  # CPU-bound (별도 스레드)
        fetch_data_from_api("url2"),  # I/O-bound
    ]

    results = await asyncio.gather(*tasks)
    # 실제: 1초 (진정한 병렬!)
```

**Python 3.9 미만에서는 `loop.run_in_executor` 사용**:

```python
async def compute_hash_legacy(data: bytes) -> str:
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor()
    return await loop.run_in_executor(executor, compute_hash_sync, data)
```

**언제 ThreadPoolExecutor vs ProcessPoolExecutor?**

| 작업 유형 | 권장 | 이유 |
|----------|------|------|
| **I/O-bound** | `asyncio` | Event Loop가 최적 |
| **CPU-bound (가벼움)** | `ThreadPoolExecutor` | 프로세스 생성 오버헤드 회피 |
| **CPU-bound (무거움)** | `ProcessPoolExecutor` | GIL 회피, 진정한 병렬 |
| **혼합** | `asyncio` + `to_thread` | 유연성 |

### 4. return_exceptions=True의 타입 안전성 문제

`gather(..., return_exceptions=True)`는 편리하지만, 타입 체커가 도와줄 수 없습니다.

```python
async def fetch_user(id: int) -> dict:
    if id < 0:
        raise ValueError("음수 ID")
    return {"id": id, "name": f"User{id}"}

async def dangerous_gather():
    # ⚠️ 타입 힌트: list[dict] (거짓말!)
    results: list[dict] = await asyncio.gather(
        fetch_user(1),
        fetch_user(-1),  # 예외 발생!
        fetch_user(2),
        return_exceptions=True
    )

    # 💥 런타임 에러 위험!
    for user in results:
        print(user["name"])  # results[1]은 ValueError 객체!
        # AttributeError: 'ValueError' object has no attribute '__getitem__'
```

**문제**: `results`의 실제 타입은 `list[dict | Exception]`이지만, 타입 체커는 `list[dict]`로만 인식합니다.

**해결책 1: 명시적 타입 가드**

```python
async def safe_gather():
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(-1),
        fetch_user(2),
        return_exceptions=True
    )

    # ✅ 타입 가드로 필터링
    users: list[dict] = []
    errors: list[Exception] = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(result)
            print(f"에러: {result}")
        else:
            users.append(result)

    # 이제 users는 안전하게 dict만 포함
    for user in users:
        print(user["name"])
```

**해결책 2: Result 타입 사용 (5장 패턴)**

```python
from typing import Union

# 5장의 Result 타입 재활용
async def fetch_user_result(id: int) -> Result[dict, str]:
    try:
        if id < 0:
            return Err("음수 ID는 허용되지 않습니다")
        return Ok({"id": id, "name": f"User{id}"})
    except Exception as e:
        return Err(str(e))

async def type_safe_gather():
    # return_exceptions=False (기본값) 사용
    # 각 함수가 이미 Result로 에러를 감쌌으므로 예외 발생 안 함
    results: list[Result[dict, str]] = await asyncio.gather(
        fetch_user_result(1),
        fetch_user_result(-1),
        fetch_user_result(2)
    )

    # ✅ 타입 안전하게 처리
    for result in results:
        match result:
            case Ok(user):
                print(f"성공: {user['name']}")
            case Err(error):
                print(f"실패: {error}")
```

**가이드라인**:
- `return_exceptions=True`는 프로토타입에서만 사용하세요.
- 프로덕션 코드에서는 `Result` 타입으로 에러를 명시적으로 처리하세요.
- 또는 `try-except`로 각 작업을 감싸서 예외를 값으로 변환하세요.

### 정리: 병렬 실행 체크리스트

| 위험 | 증상 | 해결책 |
|------|------|--------|
| **메모리 폭발** | OOM, 느린 시작 | Semaphore + 청크 처리 |
| **Semaphore 교착** | 영구 대기 | 중첩 회피, 타임아웃 |
| **CPU 블로킹** | 느린 응답 | `asyncio.to_thread` |
| **타입 불안정** | 런타임 에러 | `isinstance` 가드, Result 타입 |

병렬 실행은 **강력하지만 위험**합니다. 1장에서 배운 참조 투명성과 부수 효과 제어가, 병렬 세계에서는 **동시성 제어**와 **자원 관리**로 발전합니다. 함수형 프로그래밍의 철학 - 예측 가능성, 합성 가능성 - 은 여기서도 여전히 유효합니다.

## 연습 문제

동시성과 병렬성의 개념을 직접 연습해보세요.

**기본 문제**: 여러 API에서 데이터를 가져오는 함수를 작성하되, 모든 API가 성공해야만 Ok를 반환하고 하나라도 실패하면 Err를 반환하세요. asyncio.gather와 5장의 Result를 함께 사용하세요.

```python
async def fetch_api(url: str) -> Result[dict, str]:
    # API를 호출하고 Result를 반환합니다
    pass

async def fetch_all_apis(urls: list[str]) -> Result[list[dict], str]:
    # 모든 API를 병렬로 호출하고, 모두 성공하면 Ok(결과 리스트)를 반환
    # 하나라도 실패하면 Err(에러 메시지)를 반환
    pass
```

**중급 문제**: 동적 동시성 제어를 구현하세요. 처음에는 적은 수의 동시 요청으로 시작하고, 성공률이 높으면 동시성을 증가시키고, 에러가 많으면 감소시키는 적응형 크롤러를 만드세요.

```python
class AdaptiveCrawler:
    def __init__(self):
        self.current_concurrency = 5
        self.min_concurrency = 2
        self.max_concurrency = 20
    
    async def adjust_concurrency(self, success_rate: float):
        # success_rate에 따라 current_concurrency를 조정합니다
        pass
    
    async def crawl(self, urls: list[str]) -> list[CrawlResult]:
        # 크롤링하면서 동적으로 동시성을 조정합니다
        pass
```

**도전 문제**: 우선순위 큐를 사용하는 크롤러를 구현하세요. 각 URL에 우선순위가 있고, 높은 우선순위의 URL을 먼저 처리해야 합니다. 동시 접속 수는 제한되어 있으므로, 낮은 우선순위의 작업이 실행 중이더라도 높은 우선순위 작업이 오면 새로운 슬롯이 생길 때까지 기다려야 합니다.

```python
from dataclasses import dataclass
import heapq

@dataclass
class PriorityURL:
    priority: int
    url: str
    
    def __lt__(self, other):
        # 우선순위가 낮을수록 먼저 처리 (heapq는 min-heap)
        return self.priority < other.priority

class PriorityCrawler:
    async def worker(self, queue: asyncio.PriorityQueue, results: list):
        while not queue.empty():
            priority_url = await queue.get()
            # 크롤링 로직 (생략)
            print(f"Processing: {priority_url.url} (Priority: {priority_url.priority})")
            # 결과를 리스트에 추가한다고 가정
            results.append(CrawlResult(priority_url.url, "content", 200, None))
            queue.task_done()

    async def crawl_with_priority(
        self,
        urls: list[PriorityURL],
        max_concurrent: int
    ) -> list[CrawlResult]:
        # 1. 우선순위 큐 초기화
        queue = asyncio.PriorityQueue()
        for url in urls:
            queue.put_nowait(url)
            
        results = []
        # 2. 워커 생성 (세마포어 대신 워커 수로 제한)
        # 큐에서 작업을 꺼내서 처리하는 워커 패턴입니다
        workers = [asyncio.create_task(self.worker(queue, results)) for _ in range(max_concurrent)]
        
        # 3. 큐가 비을 때까지 대기
        await queue.join()
        
        # 4. 워커 종료
        for w in workers: w.cancel()
        return results
```

## 6장 요약: 독립적 작업의 해방

이번 장에서는 4장의 순차 실행(Monad)을 넘어, **병렬 실행(Applicative)**을 통해 성능을 극대화하는 방법을 배웠습니다.

1.  **순차 vs 병렬의 기준**: "이 작업의 결과가 다음 작업에 필요한가?" (의존성 여부)
    *   의존적임 → **Monad** (`await` / `flatMap`) → 순차 실행
    *   독립적임 → **Applicative** (`gather`) → 병렬 실행
2.  **도구들**:
    *   `asyncio.gather`: 가장 기본적인 병렬 실행 도구
    *   `TaskGroup`: Python 3.11+ 구조적 동시성 (자동 취소 및 생명주기 관리)
    *   `Semaphore`: 동시 실행 수 제한 (Rate limiting)

### 1장 → 6장까지의 여정

| 장 | 핵심 개념 | 해결한 문제 | 실행 방식 |
|----|----------|------------|----------|
| **1장** | 합성 (compose) | 순수 함수를 조합 가능하게 | 동기 |
| **3장** | Functor (map) | 독립적 변환의 합성 | 비동기 |
| **4장** | Monad (flatMap) | 의존적 작업의 순차 합성 | 비동기 순차 |
| **5장** | Result | **실패 가능성**을 합성 가능하게 | 비동기 순차 |
| **6장** | Applicative (gather) | **독립적 작업**의 병렬 합성 | **비동기 병렬** |

우리는 이제 순차와 병렬, 성공과 실패를 자유자재로 다룰 수 있게 되었습니다. 하지만 지금까지 우리는 '단일 값'(Future)이나 '단일 리스트'를 다뤘습니다. 만약 데이터가 시간에 따라 끊임없이 흐른다면 어떨까요?

### 다음 7장 예고: Observable과 Reactive Programming

다음 장에서는 **시간에 걸쳐 발생하는 데이터의 스트림**을 다루는 `Observable`을 만납니다. 클릭 이벤트, 센서 데이터, 웹소켓 메시지 등 끊임없이 흐르는 데이터를 함수형으로 우아하게 처리하는 방법을 배워봅시다.

```python
# 7장 맛보기: 스트림 처리
user_clicks = observe_clicks()
filtered = user_clicks.filter(lambda e: e.button == "left")
debounced = filtered.debounce(300)  # 300ms 동안 추가 클릭 없으면
debounced.subscribe(handle_click)
```
