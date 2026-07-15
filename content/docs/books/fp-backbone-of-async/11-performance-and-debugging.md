---
title: "11. 성능과 디버깅: 비동기 코드 최적화하기"
date: 2026-07-15T00:00:00+09:00
draft: false
tags: ["functional-programming", "python", "performance", "book"]
categories: ["books"]
description: "비동기 코드의 성능 최적화와 디버깅 전략을 함수형 관점에서 정리합니다."
---


## 인트로: 왜 비동기 코드가 느릴까?

당신의 FastAPI 서버가 느리다는 제보를 받았습니다. 명백히 비동기로 작성했는데, 동시 요청 10개를 처리하는데 3초나 걸립니다. 로그를 확인하니 이상한 패턴이 보입니다:

```
[INFO] 요청 #1 처리 시작
[INFO] DB 쿼리 완료 (0.05초)
... 2초 동안 로그 없음 ...
[INFO] 응답 전송
```

`await`로 DB를 쿼리했는데 왜 2초나 멈춰있을까요? 답은 **블로킹 작업**입니다. 누군가 비동기 함수 안에서 `time.sleep(2)`를 호출했거나, CPU 집약적 작업을 실행한 것입니다. 이것이 이벤트 루프를 독점하여 다른 모든 요청을 멈춥니다.

10장에서 우리는 비동기 코드를 테스트하는 법을 배웠습니다. 정확하게 작동하는 코드를 만드는 것이 첫 번째 단계라면, **효율적이고 안정적으로** 작동하게 만드는 것이 그 다음 단계입니다. 비동기 프로그래밍은 성능을 위한 선택입니다. 하나의 스레드로 수천 개의 동시 연결을 처리할 수 있지만, 이런 이점은 저절로 주어지지 않습니다. 잘못 작성된 비동기 코드는 동기 코드보다 느릴 수 있고, 디버깅하기 훨씬 어려울 수 있습니다.

여기서 함수형 프로그래밍의 원칙이 다시 빛을 발합니다. 순수 함수는 같은 입력에 항상 같은 출력을 반환하므로, 성능을 측정하고 예측하기 쉽습니다. 불변 데이터는 상태 변화를 추적할 필요가 없으므로, 디버깅이 단순해집니다. 합성 가능한 추상화는 복잡한 동시성 제어를 작은 조각으로 나누어 이해하고 테스트할 수 있게 합니다.

**이 장의 핵심 목표:**
1. **이벤트 루프**의 작동 원리를 이해하고, 블로킹이 왜 치명적인지 파악하기
2. **메모리 누수와 과부하**를 방지하는 실용적인 패턴 익히기 (Semaphore, 백프레셔)
3. **복잡한 비동기 흐름**을 추적하고 디버깅하는 도구 습득하기 (contextvars, 로깅)
4. **함수형 원칙**이 성능 최적화와 디버깅을 어떻게 단순하게 만드는지 경험하기

이 장을 마치면 당신은 기계적으로 돌아가는 코드를 넘어, **복잡한 시스템을 안정적으로 운영하는 능력**을 갖추게 될 것입니다.

---

## 1부: 성능 문제의 근원 이해하기

### 이벤트 루프의 해부

성능 문제를 이해하려면 이벤트 루프의 작동 방식을 알아야 합니다. asyncio의 이벤트 루프는 단일 스레드에서 여러 코루틴을 협력적으로 스케줄링합니다. 핵심은 "협력적"이라는 점입니다. 각 코루틴은 await를 통해 자발적으로 제어를 양보해야 합니다.

이벤트 루프를 의사 코드로 표현하면 이렇습니다.

```python
# 이것은 실제 asyncio 코드가 아니라 개념적 설명입니다
while True:
    # 1. 실행 준비된 Task들을 가져옵니다
    ready_tasks = get_ready_tasks()

    # 2. 각 Task를 조금씩 실행합니다
    for task in ready_tasks:
        task.run_until_await()  # await를 만날 때까지 실행

    # 3. I/O 이벤트를 확인합니다 (select/epoll)
    io_events = wait_for_io_events(timeout=0)

    # 4. I/O가 완료된 Task들을 ready 상태로 만듭니다
    for event in io_events:
        mark_task_ready(event.task)

    # 5. 타이머를 확인합니다
    expired_timers = check_timers()
    for timer in expired_timers:
        mark_task_ready(timer.task)

    # 6. 모든 Task가 완료되었으면 종료
    if no_more_tasks():
        break
```

이 모든 것이 **하나의 스레드**에서 일어납니다. 어떤 Task가 await 없이 오래 실행되면, 다른 모든 Task가 기다려야 합니다. 이것이 블로킹 문제의 본질입니다.

### 블로킹의 영향: 실험으로 확인하기

블로킹 작업이 이벤트 루프에 미치는 영향을 실험해봅시다.

```python
import asyncio
import time

async def ticker() -> None:
    """매초 시간을 출력하는 백그라운드 작업"""
    count: int = 0
    while count < 10:
        count += 1
        print(f"  [Ticker] {count}초 경과")
        await asyncio.sleep(1)

async def blocking_operation() -> None:
    """블로킹 작업 (잘못된 예)"""
    print("블로킹 작업 시작...")
    time.sleep(3)  # ❌ 이것은 블로킹입니다!
    print("블로킹 작업 완료")

async def non_blocking_operation() -> None:
    """논블로킹 작업 (올바른 예)"""
    print("논블로킹 작업 시작...")
    await asyncio.sleep(3)  # ✅ 이것은 논블로킹입니다
    print("논블로킹 작업 완료")

async def test_blocking() -> None:
    """블로킹의 영향을 테스트합니다"""
    print("=== 블로킹 테스트 시작 ===")

    # ticker와 blocking_operation을 동시에 실행
    await asyncio.gather(
        ticker(),
        blocking_operation()
    )

async def test_non_blocking() -> None:
    """논블로킹 동작을 테스트합니다"""
    print("\n=== 논블로킹 테스트 시작 ===")

    # ticker와 non_blocking_operation을 동시에 실행
    await asyncio.gather(
        ticker(),
        non_blocking_operation()
    )

# 실행
print("먼저 블로킹 버전을 실행합니다:")
asyncio.run(test_blocking())

print("\n이제 논블로킹 버전을 실행합니다:")
asyncio.run(test_non_blocking())
```

블로킹 버전을 실행하면 이런 출력을 볼 수 있습니다.

```
=== 블로킹 테스트 시작 ===
블로킹 작업 시작...
(3초 동안 아무 출력 없음 - ticker도 멈춤)
블로킹 작업 완료
  [Ticker] 1초 경과
  [Ticker] 2초 경과
  [Ticker] 3초 경과
  ...
```

blocking_operation이 실행되는 3초 동안 ticker도 완전히 멈춥니다. time.sleep이 이벤트 루프를 블로킹했기 때문입니다. 논블로킹 버전은 다릅니다.

```
=== 논블로킹 테스트 시작 ===
  [Ticker] 1초 경과
논블로킹 작업 시작...
  [Ticker] 2초 경과
  [Ticker] 3초 경과
  [Ticker] 4초 경과
논블로킹 작업 완료
  [Ticker] 5초 경과
  ...
```

await asyncio.sleep이 이벤트 루프에 제어를 양보하므로, ticker가 계속 실행됩니다. **await는 양보 지점입니다.** await 없이는 코루틴이 이벤트 루프를 독점합니다.

---

## 2부: 실전 성능 최적화 패턴

### 블로킹 작업의 올바른 처리

블로킹 작업을 완전히 피할 수는 없습니다. 파일 읽기, CPU 집약적 계산, 비동기를 지원하지 않는 라이브러리 사용 등이 필요할 때가 있습니다. asyncio는 두 가지 해결책을 제공합니다.

**방법 1: ThreadPoolExecutor로 I/O 블로킹 격리**

run_in_executor로 블로킹 작업을 별도의 스레드에서 실행합니다.

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

# 블로킹 함수 (동기)
def cpu_intensive_task(data: bytes) -> str:
    """CPU 집약적인 작업 (해시 계산)"""
    import hashlib

    # 의도적으로 느린 해시 계산 (비밀번호 해싱 시뮬레이션)
    result = data
    for _ in range(100000):
        result = hashlib.sha256(result).digest()

    return result.hex()

async def run_blocking_correctly() -> str:
    """블로킹 작업을 올바르게 실행합니다"""
    loop = asyncio.get_running_loop()

    # ThreadPoolExecutor 생성
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 블로킹 함수를 executor에서 실행
        result = await loop.run_in_executor(
            executor,
            cpu_intensive_task,
            b"password123"
        )

    return result

async def main() -> None:
    """ticker와 함께 블로킹 작업을 실행합니다"""

    async def ticker() -> None:
        for i in range(5):
            print(f"  Tick {i + 1}")
            await asyncio.sleep(0.5)

    # 동시 실행
    ticker_task = asyncio.create_task(ticker())
    result = await run_blocking_correctly()

    await ticker_task

    print(f"계산 결과: {result}")

asyncio.run(main())
```

run_in_executor는 Future를 반환하고, await로 기다리는 동안 이벤트 루프는 다른 작업을 계속 실행합니다.

**방법 2: ProcessPoolExecutor로 CPU 작업 병렬화**

CPU 집약적 작업은 ProcessPoolExecutor를 사용합니다. 파이썬의 GIL 때문에 스레드는 CPU 작업을 병렬로 실행할 수 없지만, 프로세스는 가능합니다.

```python
from concurrent.futures import ProcessPoolExecutor

async def run_cpu_intensive() -> list[str]:
    """CPU 집약적인 작업을 프로세스에서 실행합니다"""
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor(max_workers=4) as executor:
        # 여러 계산을 병렬로 실행
        passwords = [b"pass1", b"pass2", b"pass3", b"pass4"]
        tasks = [
            loop.run_in_executor(executor, cpu_intensive_task, pw)
            for pw in passwords
        ]

        results = await asyncio.gather(*tasks)

    return results
```

ProcessPoolExecutor는 멀티코어 CPU를 최대한 활용합니다. 단, 프로세스 생성 비용이 있으므로 작업이 충분히 무거울 때만 사용하세요.

**📌 지침**:
- I/O 블로킹 → ThreadPoolExecutor
- CPU 집약적 작업 → ProcessPoolExecutor
- 가능하면 비동기 라이브러리(aiohttp, aiofiles, asyncpg) 사용

### 함수형 원칙으로 성능 개선하기

**불변성과 메모리 관리**

CPU 시간만큼이나 중요한 것이 메모리입니다. 비동기 프로그램은 수천 개의 코루틴을 동시에 유지할 수 있지만, 잘못 관리하면 메모리 누수로 이어집니다.

가장 흔한 메모리 누수 원인은 **"상태 변이(State Mutation)"**입니다. 객체의 상태를 계속 변경하다 보면, 언제 이 객체가 더 이상 필요 없는지 추적하기 어려워집니다. 특히 클로저나 콜백 지옥에서는 의도치 않게 거대한 객체 그래프가 메모리에 남게 됩니다.

함수형 프로그래밍의 **불변성(Immutability)** 원칙은 여기서 빛을 발합니다.

1.  **참조의 단순화**: 불변 객체는 상태가 변하지 않으므로, 복잡한 참조 고리(Cycle)를 만들 가능성이 줄어듭니다.
2.  **명확한 수명 주기**: 함수 인자로 전달된 데이터는 함수 실행이 끝나면(참조가 없으면) 즉시 해체될 수 있습니다.
3.  **공유의 안전성**: 여러 코루틴이 같은 불변 객체를 참조해도 안전하므로, 방어적 복사(Defensive Copy)가 필요 없어 메모리를 절약합니다.

상태 관리가 필요하다면, 상태를 변이시키는 대신 **새로운 상태를 반환**하는 방식을 사용하세요. 이는 메모리 관리뿐만 아니라 흐름 추적도 훨씬 쉽게 만듭니다.

**메모이제이션: 순수 함수의 강점**

순수 함수는 같은 입력에 항상 같은 출력을 반환합니다. 이것은 결과를 캐싱할 수 있다는 뜻입니다.

```python
from functools import lru_cache
import asyncio

# 동기 순수 함수: lru_cache 사용 가능
@lru_cache(maxsize=1000)
def expensive_calculation(n: int) -> int:
    """비싼 계산을 캐싱"""
    return sum(i * i for i in range(n))

# 비동기 함수를 위한 캐싱
def async_lru_cache(maxsize: int = 128):
    """비동기 함수용 LRU 캐시 데코레이터"""
    cache: dict = {}

    def decorator(func):
        async def wrapper(*args):
            key = args
            if key in cache:
                return cache[key]

            result = await func(*args)

            if len(cache) >= maxsize:
                # 가장 오래된 항목 제거 (간단한 구현)
                oldest = next(iter(cache))
                del cache[oldest]

            cache[key] = result
            return result

        return wrapper
    return decorator

@async_lru_cache(maxsize=100)
async def fetch_user_cached(user_id: str) -> dict:
    """사용자 정보를 캐싱"""
    await asyncio.sleep(0.5)  # DB 조회
    return {"id": user_id, "name": f"User {user_id}"}
```

### 동시 실행 수 제한: Semaphore

메모리 문제 외에도, 무제한 동시 실행은 다른 자원(네트워크 연결, 파일 핸들, API rate limits)도 고갈시킵니다. Semaphore는 동시에 실행할 수 있는 작업의 수를 제한합니다.

10,000개의 URL을 크롤링할 때 동시에 모두 요청하면 어떻게 될까요?

```python
import asyncio
import aiohttp

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """URL을 가져옵니다"""
    async with session.get(url) as response:
        return await response.text()

async def crawl_unlimited(urls: list[str]) -> list:
    """무제한 동시 요청 (위험!)"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 10,000개 URL
urls = [f"https://example.com/page{i}" for i in range(10000)]

# ❌ 이것은 문제를 일으킬 가능성이 높습니다
# asyncio.run(crawl_unlimited(urls))
```

10,000개 요청이 동시에 시작되어 파일 디스크립터 한계, 서버 과부하, 메모리 부족 문제가 발생합니다. Semaphore로 제한하면 해결됩니다.

```python
import asyncio
import aiohttp

async def fetch_url_limited(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore
) -> str:
    """동시 실행 수가 제한된 URL 가져오기"""
    async with semaphore:
        # semaphore를 획득했습니다
        # 최대 N개만 이 블록에 동시 진입 가능
        async with session.get(url) as response:
            return await response.text()

async def crawl_limited(urls: list[str], max_concurrent: int = 100) -> list:
    """제한된 동시 요청"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_url_limited(session, url, semaphore)
            for url in urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return results

# ✅ 이제 안전합니다
# asyncio.run(crawl_limited(urls, max_concurrent=50))
```

Semaphore(50)은 최대 50개만 동시 실행되도록 제한합니다. 적절한 값은 rate limit, 메모리, 네트워크 대역폭에 따라 다릅니다. 10, 50, 100 같은 값부터 시작해서 테스트하세요.

### 백프레셔: 과부하 방지

백프레셔(backpressure)는 생산자가 소비자보다 빠를 때 생산 속도를 늦추는 메커니즘입니다. 생산이 소비보다 빠르면 데이터가 메모리에 쌓여 결국 메모리가 부족해집니다.

```python
import asyncio
from collections import deque

async def producer(queue: asyncio.Queue) -> None:
    """빠른 생산자"""
    for i in range(100):
        item = f"아이템 {i}"
        await queue.put(item)
        print(f"생성: {item}")
        await asyncio.sleep(0.01)  # 매우 빠름

    await queue.put(None)  # 종료 신호

async def consumer(queue: asyncio.Queue) -> None:
    """느린 소비자"""
    while True:
        item = await queue.get()

        if item is None:
            break

        print(f"  처리 중: {item}")
        await asyncio.sleep(0.1)  # 생산자보다 10배 느림
        print(f"  처리 완료: {item}")

async def main_no_backpressure() -> None:
    """백프레셔 없이 실행 (문제 발생 가능)"""
    queue = asyncio.Queue()  # 무제한 큐

    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

# asyncio.run(main_no_backpressure())
```

생산자는 초당 100개를 넣고, 소비자는 초당 10개를 처리합니다. 큐가 무한정 커집니다. 백프레셔를 추가합니다.

```python
async def main_with_backpressure() -> None:
    """백프레셔와 함께 실행"""
    queue = asyncio.Queue(maxsize=10)  # ✅ 큐 크기 제한

    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

# asyncio.run(main_with_backpressure())
```

Queue(maxsize=10)은 큐가 가득 차면 put이 블로킹됩니다. 생산 속도가 자동으로 소비 속도에 맞춰지고, 메모리가 무한정 증가하지 않습니다.

여러 단계의 파이프라인에서는 각 단계 사이에 제한된 버퍼를 두면 전체 파이프라인이 균형을 유지합니다. 가장 느린 단계가 전체 속도를 결정합니다.

### 구조적 동시성: TaskGroup

Python 3.11에서 도입된 asyncio.TaskGroup은 8장에서 배운 "브라켓팅" 패턴의 비동기 버전입니다. 파일을 열고, 사용하고, 반드시 닫는 것처럼, TaskGroup은 Task를 생성하고, 실행하고, 반드시 정리합니다.

```python
import asyncio

async def fetch_data(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name}: 완료"

async def fetch_may_fail(name: str) -> str:
    await asyncio.sleep(0.5)
    if name == "bad":
        raise ValueError(f"{name}: 실패!")
    return f"{name}: 성공"

# 기존 방식: gather
async def old_way() -> list:
    results = await asyncio.gather(
        fetch_data("A", 1),
        fetch_data("B", 2),
        return_exceptions=True
    )
    return results

# 새로운 방식: TaskGroup
async def new_way() -> tuple[str, str]:
    async with asyncio.TaskGroup() as tg:
        task_a = tg.create_task(fetch_data("A", 1))
        task_b = tg.create_task(fetch_data("B", 2))

    # 이 시점에 모든 Task가 완료됨
    return task_a.result(), task_b.result()
```

TaskGroup의 핵심 이점은 **예외 처리**입니다. 하나의 Task가 실패하면 다른 모든 Task가 자동으로 취소되고, ExceptionGroup으로 모든 예외가 수집됩니다.

```python
async def demonstrate_exception_handling() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_may_fail("good"))
            tg.create_task(fetch_may_fail("bad"))  # 실패
            tg.create_task(fetch_may_fail("also_good"))

    except* ValueError as eg:
        # Python 3.11의 except* 구문
        for exc in eg.exceptions:
            print(f"잡힌 예외: {exc}")

# Python 3.11 미만 버전에서는 `trio` 라이브러리나
# `aiotools`의 `TaskGroup`을 사용하여 비슷한 기능을 구현할 수 있습니다.
asyncio.run(demonstrate_exception_handling())
```

**왜 함수형 프로그래밍과 연결될까요?**

TaskGroup은 **"전부 성공하거나 전부 실패"**라는 원칙을 구현합니다. 이것은 트랜잭션의 원자성과 같은 개념이며, 4장에서 배운 Monad의 'fail-fast' 원칙(하나 실패 시 전체 중단)을 구현합니다. 부분적인 성공 상태가 없으므로, 시스템의 상태를 추론하기 쉽습니다. 또한 with 블록을 벗어나면 모든 Task가 정리되므로, 자원 누수가 불가능합니다.

```python
# 실제 사용 예: 여러 API를 동시에 호출
async def fetch_user_data(user_id: str) -> dict:
    async with asyncio.TaskGroup() as tg:
        profile_task = tg.create_task(fetch_profile(user_id))
        orders_task = tg.create_task(fetch_orders(user_id))
        preferences_task = tg.create_task(fetch_preferences(user_id))

    return {
        "profile": profile_task.result(),
        "orders": orders_task.result(),
        "preferences": preferences_task.result()
    }

async def fetch_profile(user_id: str) -> dict:
    await asyncio.sleep(0.1)
    return {"id": user_id, "name": "User"}

async def fetch_orders(user_id: str) -> list:
    await asyncio.sleep(0.2)
    return [{"order_id": 1}, {"order_id": 2}]

async def fetch_preferences(user_id: str) -> dict:
    await asyncio.sleep(0.1)
    return {"theme": "dark", "language": "ko"}
```

### 취소와 정리: 우아한 종료

비동기 시스템에서 취소(cancellation)는 피할 수 없습니다. 사용자가 요청을 중단하거나, 타임아웃이 발생하거나, 시스템이 종료될 때 진행 중인 작업을 정리해야 합니다. 이것을 제대로 처리하지 않으면 자원 누수, 데이터 손상, 또는 무한 대기가 발생할 수 있습니다.

asyncio에서 취소는 CancelledError 예외로 처리됩니다.

```python
import asyncio

async def cancellable_work() -> str:
    """취소 가능한 작업"""
    try:
        print("작업 시작...")
        await asyncio.sleep(10)  # 긴 작업
        print("작업 완료")  # 취소되면 실행되지 않음
        return "결과"

    except asyncio.CancelledError:
        print("작업이 취소되었습니다")
        # 정리 작업 수행
        raise  # ⚠️ 취소를 다시 발생시켜야 함!

async def main() -> None:
    task = asyncio.create_task(cancellable_work())

    await asyncio.sleep(1)  # 1초 후
    task.cancel()  # 취소

    try:
        await task
    except asyncio.CancelledError:
        print("Task가 취소됨을 확인")

asyncio.run(main())
```

**📌 중요한 규칙**: CancelledError를 잡았으면 반드시 다시 발생시키세요. 그렇지 않으면 취소가 전파되지 않아 시스템이 제대로 종료되지 않습니다.

때로는 취소되어도 반드시 완료해야 하는 작업이 있습니다. asyncio.shield가 이런 상황에 사용됩니다.

```python
async def critical_cleanup() -> None:
    """반드시 완료해야 하는 정리 작업"""
    print("중요한 정리 시작...")
    await asyncio.sleep(1)
    print("정리 완료")

async def work_with_cleanup() -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("취소됨 - 하지만 정리는 완료해야 함")
        # shield로 정리 작업 보호
        await asyncio.shield(critical_cleanup())
        raise
```

프로덕션 시스템에서는 graceful shutdown이 필수입니다. SIGTERM 신호를 받으면 새 요청 수락을 중단하고, 진행 중인 요청을 완료한 후 종료해야 합니다.

```python
import asyncio
import signal

class GracefulServer:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.active_tasks: set[asyncio.Task] = set()

    async def handle_request(self, request_id: int) -> None:
        """개별 요청 처리"""
        task = asyncio.current_task()
        if task:
            self.active_tasks.add(task)

        try:
            print(f"요청 {request_id} 처리 중...")
            await asyncio.sleep(2)  # 작업 시뮬레이션
            print(f"요청 {request_id} 완료")
        finally:
            if task:
                self.active_tasks.discard(task)

    async def run(self) -> None:
        """서버 실행"""
        loop = asyncio.get_running_loop()

        # 시그널 핸들러 등록
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.shutdown())
            )

        print("서버 시작됨")

        # 요청 시뮬레이션
        request_id = 0
        while not self.shutdown_event.is_set():
            request_id += 1
            asyncio.create_task(self.handle_request(request_id))
            await asyncio.sleep(0.5)

    async def shutdown(self) -> None:
        """우아한 종료"""
        print("\n종료 신호 수신 - 새 요청 중단")
        self.shutdown_event.set()

        if self.active_tasks:
            print(f"진행 중인 {len(self.active_tasks)}개 요청 완료 대기...")
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

        print("모든 요청 완료 - 서버 종료")
```

이 패턴은 함수형 프로그래밍의 자원 관리 원칙을 따릅니다. 자원(여기서는 Task)을 명시적으로 추적하고, 정리 시점을 명확히 정의합니다.

---

## 3부: 디버깅과 관측 가능성

### 비동기 디버깅의 도전: 끊어진 스택 트레이스

동기 코드에서는 에러가 나면 Stack Trace를 보면 됩니다. 함수 호출 과정이 그대로 남아있으니까요. 하지만 비동기 코드는 다릅니다. 에러가 발생했을 때 Stack Trace를 보면 `Event Loop` → `Task` → `Error` 만 보일 뿐, **"누가 이 Task를 호출했는지"**는 보이지 않습니다.

이때 **`contextvars`**가 구원투수입니다. 8장에서 배운 Reader Monad처럼, **실행 문맥(Execution Context)**을 전달하면 디버깅이 쉬워집니다.

```python
import contextvars
from uuid import uuid4
import asyncio

# 요청 ID를 저장할 컨텍스트 변수
request_id = contextvars.ContextVar("request_id", default="unknown")

async def process_request() -> None:
    # 요청마다 고유 ID 부여
    req_id = str(uuid4())
    token = request_id.set(req_id)
    try:
        await step1()
    finally:
        request_id.reset(token)

async def step1() -> None:
    # 로그에 항상 request_id를 포함시킵니다
    print(f"[{request_id.get()}] step1 시작")
    await asyncio.sleep(0.1)
    # 에러가 발생해도 로그를 통해 어떤 요청에서 발생했는지 추적 가능
```

대부분의 현대적인 로깅 라이브러리(`structlog` 등)는 `contextvars`를 지원하므로, 설정만 해주면 모든 로그에 자동으로 요청 ID가 붙습니다. 이것이 비동기 디버깅의 핵심입니다.

### 로깅과 분산 추적

여러 코루틴이 동시에 실행되면 어떤 로그가 어떤 요청에 속하는지 추적하기 어렵습니다. 컨텍스트 변수(contextvars)는 각 코루틴마다 독립적인 값을 가질 수 있어 이 문제를 해결합니다.

```python
import asyncio
import logging
from contextvars import ContextVar

# 요청 ID를 저장하는 컨텍스트 변수
request_id_var: ContextVar[str] = ContextVar('request_id', default='unknown')

class RequestIdFilter(logging.Filter):
    """로그에 요청 ID를 추가하는 필터"""

    def filter(self, record) -> bool:
        record.request_id = request_id_var.get()
        return True

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('[%(request_id)s] %(message)s')
)
handler.addFilter(RequestIdFilter())

logger.addHandler(handler)

async def process_request_logged(request_id: str) -> None:
    """요청을 처리합니다"""
    # 요청 ID 설정
    request_id_var.set(request_id)

    logger.info("요청 처리 시작")
    await asyncio.sleep(0.5)

    await fetch_data_logged()

    logger.info("요청 처리 완료")

async def fetch_data_logged() -> None:
    """데이터를 가져옵니다"""
    logger.info("데이터 조회 시작")
    await asyncio.sleep(0.3)
    logger.info("데이터 조회 완료")

async def main_logging() -> None:
    """여러 요청을 동시에 처리합니다"""
    await asyncio.gather(
        process_request_logged("req-001"),
        process_request_logged("req-002"),
        process_request_logged("req-003")
    )

# asyncio.run(main_logging())
```

출력은 이렇게 나타납니다.

```
[req-001] 요청 처리 시작
[req-002] 요청 처리 시작
[req-003] 요청 처리 시작
[req-001] 데이터 조회 시작
[req-002] 데이터 조회 시작
[req-003] 데이터 조회 시작
[req-001] 데이터 조회 완료
[req-002] 데이터 조회 완료
[req-003] 데이터 조회 완료
[req-001] 요청 처리 완료
[req-002] 요청 처리 완료
[req-003] 요청 처리 완료
```

여러 요청이 동시에 처리되어도 섞이지 않습니다. 마이크로서비스에서는 OpenTelemetry나 Jaeger 같은 분산 추적 도구로 여러 서비스를 거치는 요청을 추적할 수 있습니다.

성능 문제를 디버깅할 때는 로그에 타이밍 정보를 포함시키세요.

```python
import time

async def instrumented_function() -> None:
    """타이밍 정보를 로그하는 함수"""
    start = time.time()

    logger.info("단계 1 시작")
    await asyncio.sleep(0.5)
    logger.info(f"단계 1 완료 (소요: {time.time() - start:.2f}초)")

    step2_start = time.time()
    logger.info("단계 2 시작")
    await asyncio.sleep(0.3)
    logger.info(f"단계 2 완료 (소요: {time.time() - step2_start:.2f}초)")

    logger.info(f"전체 완료 (총 소요: {time.time() - start:.2f}초)")
```

이런 로그는 어떤 단계가 느린지 즉시 보여줍니다. 프로덕션 환경에서도 이런 로깅을 유지하면 성능 문제를 조기에 발견할 수 있습니다.

### 디버깅 도구와 프로파일링

비동기 코드의 성능을 개선하려면 먼저 정확히 측정해야 합니다. 하지만 `print` 문이나 단순한 로깅만으로는 비동기 시스템의 복잡한 실행 흐름을 파악하기 어렵습니다.

**Asyncio 디버그 모드**

가장 먼저 해야 할 일은 **asyncio 디버그 모드**를 켜는 것입니다.

```bash
PYTHONASYNCIODEBUG=1 python your_script.py
```

이 모드는 다음과 같은 흔한 실수들을 자동으로 감지해줍니다:
1.  **느린 콜백**: 이벤트 루프를 오랫동안 블로킹하는 동기 작업
2.  **버려진 코루틴**: `await`하지 않고 실행된 코루틴
3.  **스레드 안전성 위반**: 동기 함수에서 비동기 객체 접근

**프로파일링 도구**

프로파일링 도구로는 `yappi`나 `py-spy` 같은 비동기 특화 도구를 추천합니다. 일반적인 `cProfile`은 `await` 대기 시간을 구분하지 못해 정확한 측정이 어렵습니다.

**yappi 사용 예시**:

```python
import asyncio
import yappi

async def slow_function() -> None:
    await asyncio.sleep(1)

async def main_profile() -> None:
    yappi.set_clock_type("wall")  # 실제 시간 측정
    yappi.start()

    await slow_function()

    yappi.stop()
    yappi.get_func_stats().print_all()
    yappi.get_thread_stats().print_all()

# asyncio.run(main_profile())
```

10장에서 테스트를 배웠으므로, **테스트된 코드를 어떻게 프로파일링하는가?** 연결해봅시다. pytest에서 pytest-benchmark 플러그인을 사용하면 성능 테스트를 자동화할 수 있습니다.

```python
# test_performance.py
import pytest
import asyncio

@pytest.mark.asyncio
async def test_fetch_performance(benchmark):
    """fetch_user_cached의 성능 테스트"""

    async def run_fetch():
        return await fetch_user_cached("user123")

    # benchmark는 동기 함수를 기대하므로 래핑
    result = benchmark(lambda: asyncio.run(run_fetch()))
    assert result["id"] == "user123"
```

---

## 4부: 심화 - 함수형 추상화의 비용과 현실적 타협

함수형 프로그래밍이 모든 성능 문제의 만병통치약은 아닙니다. 특히 Python은 순수 함수형 언어가 아니기 때문에, 함수형 추상화에는 비용이 따릅니다.

### 1. 불변 객체의 복사 비용

거대한 리스트나 딕셔너리를 매번 복사해서 수정하면 성능이 급격히 떨어집니다.

**해결책 1**: `pyrsistent` 같은 영속적 자료구조(Persistent Data Structure) 라이브러리를 사용하세요. 구조 공유(Structural Sharing)를 통해 복사 비용을 O(1)에 가깝게 줄여줍니다.

**해결책 2**: 정말 성능이 중요한 "Hot Path"에서는 **지역적인 가변성(Local Mutation)**을 허용하세요. 함수 내부에서는 가변 리스트를 쓰고, 반환할 때만 불변으로(예: `tuple`) 변환하면 외부적으로는 순수성을 유지할 수 있습니다.

```python
# 지역적 가변성 예시
def process_items(items: tuple[int, ...]) -> tuple[int, ...]:
    """외부적으로는 순수하지만 내부적으로는 가변"""
    # 내부에서는 list 사용 (빠름)
    result = list(items)
    for i in range(len(result)):
        result[i] *= 2

    # 반환할 때는 tuple로 변환 (불변)
    return tuple(result)
```

### 2. 함수 호출 오버헤드

과도한 커링(Currying)이나 데코레이터 중첩은 Python의 함수 호출 비용을 누적시킵니다.

**해결책**: 불필요한 래핑을 줄이고, 성능이 중요한 루프 안에서는 인라인 코드나 List Comprehension을 사용하세요. `map/filter`보다 List Comprehension이 Python에서는 더 빠릅니다.

```python
# Before: 함수 호출 많음
result = list(map(lambda x: x * 2, filter(lambda x: x > 0, items)))

# After: List Comprehension (더 빠름)
result = [x * 2 for x in items if x > 0]
```

### 3. 재귀 깊이 제한

Python은 Tail Call Optimization(TCO)을 지원하지 않습니다. 깊은 재귀는 `RecursionError`를 일으키거나 스택 메모리를 낭비합니다.

**해결책**: 재귀 대신 반복문(Loop)을 사용하거나, `trampoline` 패턴을 사용하세요. 하지만 Python에서는 단순한 `while/for` 루프가 가장 빠르고 안전합니다.

```python
# Before: 재귀 (위험)
def factorial_recursive(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

# After: 반복문 (안전)
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

함수형 프로그래밍의 목표는 **가독성과 안정성**입니다. 대부분의 경우 이 이점이 약간의 성능 비용보다 큽니다. 하지만 병목 지점에서는 실용적인 타협이 필요함을 잊지 마세요. **먼저 측정하고(profiling), 그 다음 최적화하세요.**

### 적응형 동시성 제어 (Advanced)

에러율을 모니터링하면서 동시성을 동적으로 조정할 수도 있습니다. 이것을 적응형 동시성 제어(adaptive concurrency control)라고 합니다.

**핵심 아이디어**:
- 에러율 > 10% → 동시성 20% 감소
- 에러율 < 5% → 동시성 20% 증가

**함수형 원칙 적용**:
- 통계는 불변 객체(ConcurrencyStats)로 관리
- 한계 계산은 순수 함수(_calculate_new_limit)

실무에서는 `aiohttp-retry`, `tenacity` 같은 검증된 라이브러리 사용을 권장합니다. 직접 구현이 필요하다면 다음과 같은 구조로 시작하세요:

```python
from dataclasses import dataclass

@dataclass
class ConcurrencyStats:
    """동시성 통계를 불변 객체로 관리"""
    success_count: int = 0
    error_count: int = 0

    def record_success(self) -> 'ConcurrencyStats':
        return ConcurrencyStats(self.success_count + 1, self.error_count)

    def record_error(self) -> 'ConcurrencyStats':
        return ConcurrencyStats(self.success_count, self.error_count + 1)

    @property
    def error_rate(self) -> float:
        total = self.success_count + self.error_count
        return self.error_count / total if total > 0 else 0.0

# 한계 계산은 순수 함수로
def calculate_new_limit(current: int, stats: ConcurrencyStats, min_limit: int, max_limit: int) -> int:
    """에러율에 따른 새 한계 계산 (순수 함수)"""
    error_rate = stats.error_rate

    if error_rate > 0.1:
        return max(min_limit, int(current * 0.8))
    elif error_rate < 0.05:
        return min(max_limit, int(current * 1.2))
    return current
```

---

## 11장 요약: 측정하고, 최적화하라

이번 장에서는 효율적이고 안정적인 비동기 시스템을 구축하는 방법을 배웠습니다.

**핵심 내용 3줄 요약:**

1.  **이벤트 루프 이해**: 협력적 멀티태스킹의 원리를 이해하고, **블로킹 작업**을 적절히 격리(`run_in_executor`)했습니다.
2.  **구조적 동시성**: `TaskGroup`으로 자원 누수를 방지하고 예외를 안전하게 처리했습니다. Semaphore와 백프레셔로 과부하를 방지했습니다.
3.  **관측 가능성**: `contextvars`와 구조적 로깅으로 복잡한 비동기 흐름을 추적했습니다. 함수형 원칙(불변성, 순수 함수, 합성)이 성능 최적화와 디버깅을 단순하게 만듭니다.

### 1장 → 11장까지의 여정

우리는 1장의 순수 함수부터 시작해, 모나드, 아키텍처, 타입 시스템, 테스트, 그리고 성능 최적화까지 달려왔습니다. 이제 당신은 **FP 원칙을 실무 성능 문제에 적용할 수 있는 개발자**입니다.

### 다음 12장 예고: 함수형 비동기의 미래

다음 장, 대망의 마지막 장에서는 비동기 프로그래밍의 **미래**를 탐구합니다. `Effect System`, `Algebraic Effects` 같은 최신 개념들이 어떻게 언어 차원에서 비동기를 더 우아하게 해결하려 하는지 살펴봅니다. 우리가 배운 `async/await`가 종착역이 아님을 확인하고, 앞으로 다가올 변화에 대비해 봅시다.
