---
title: "8. 실전 패턴: 비동기 시스템의 함수형 아키텍처"
date: 2026-07-15T00:00:00+09:00
draft: false
tags: ["functional-programming", "python", "architecture", "book"]
categories: ["books"]
description: "의존성 주입과 미들웨어 패턴을 클로저·고차 함수·함수 합성으로 재해석한 실전 아키텍처를 다룹니다."
---


## 1-7장 복습: 여기까지의 여정

8장을 시작하기 전에, 지금까지 배운 핵심 개념들을 정리해봅시다. 우리는 1장부터 7장까지 함수형 프로그래밍의 이론적 토대를 닦았습니다. `map`, `flatMap`, `Result`, `Applicative`, 그리고 `Observable`까지.

이제 이 모든 개념들이 어떻게 **실제 시스템 아키텍처**로 통합되는지 확인할 차례입니다. "이론은 알겠는데, 실제로는 어떻게 쓰나요?"라는 질문에 대한 답이 이 장에 있습니다. 의존성 주입부터 트랜잭션 관리까지, 우리가 배운 작은 블록들이 어떻게 거대한 시스템을 지탱하는지 살펴봅시다.

**1장: 함수형 프로그래밍의 핵심 원칙**
- 순수 함수와 참조 투명성
- 합성 가능성: 작은 함수를 조합해서 복잡한 함수를 만듦
- 고차 함수: 함수를 값으로 다루기

**2장: 콜백에서 Promise로**
- 콜백의 문제: 합성 불가능, 에러 처리 분산
- 비동기를 값(Future)으로 표현하는 발상의 전환

**3장: Functor - 컨텍스트 안의 변환**
- map: 컨텍스트 안의 값을 변환하되 컨텍스트 유지
- 독립적인 변환들의 합성

**4장: Monad - 순차적 의존성의 합성**
- flatMap: 이전 결과에 의존하는 연산들을 연결
- async/await는 flatMap의 문법적 설탕

**5장: Result - 에러를 값으로 다루기**
- 에러도 값으로 다루면 합성 가능
- Railway-Oriented Programming

**6장: Applicative Functor - 병렬 합성**
- 독립적인 작업들을 병렬로 실행
- asyncio.gather

**7장: Observable - 시간에 걸친 스트림**
- 시간 차원을 추가한 Monad
- 시간 기반 연산자 (debounce, throttle)

이제 우리는 마지막 질문에 도달합니다: **이 모든 개념을 실제 시스템 아키텍처에 어떻게 적용할까요?**

---

## 7장에서 8장으로: 이론에서 실전 아키텍처로

7장에서 우리는 **시간에 걸친 스트림(Observable)**을 다뤘습니다. 검색 자동완성에서 `debounce`로 불필요한 요청을 줄이고, 여러 이벤트 스트림을 병합하는 방법을 배웠죠. 하지만 실제 웹 애플리케이션은 단일 기능만으로 이루어지지 않습니다.

**실전 시스템의 복잡성**:
- 인증 미들웨어가 모든 요청을 검증하고
- 비즈니스 로직이 여러 비동기 작업(DB 쿼리, API 호출)을 조율하며
- 트랜잭션이 데이터 일관성을 보장하고
- 로깅, 에러 처리, 성능 모니터링이 모든 레이어에 걸쳐 작동합니다

**핵심 질문**: 우리가 배운 Functor, Monad, Applicative, Observable이 **거대한 시스템 아키텍처**에서 어떻게 **조화롭게 작동**할까요?

이 장에서는 세 가지 아키텍처 패턴을 함수형 관점에서 재해석합니다:

1. **의존성 주입 (Dependency Injection)**: 클로저와 고차 함수로 상태 없는 합성
2. **미들웨어 (Middleware)**: 함수 합성으로 횡단 관심사 분리
3. **트랜잭션 (Transaction)**: Result Monad로 원자적 연산 보장

그리고 실전 통합 예제에서는 7장의 Observable 패턴도 활용하여, **실시간 이벤트 처리**와 **전통적인 요청-응답 패턴**이 어떻게 공존하는지 보여줍니다.

**중요한 관점 전환**: 이 패턴들은 표면적으로는 서로 다른 문제를 해결하는 것처럼 보이지만, 근본적으로는 모두 **"부수 효과를 격리하고 합성 가능하게 만든다"**는 같은 철학을 공유합니다. 의존성 주입은 고차 함수와 클로저로, 미들웨어는 함수 합성으로, 트랜잭션은 Monad로 재해석할 수 있습니다. 이 장을 마치면 당신은 복잡한 시스템을 더 단순하고 합성 가능한 부품들로 분해하는 방법을 알게 될 것입니다.

## 의존성 주입의 재해석: 클로저가 답이다

의존성 주입(Dependency Injection, DI)은 현대 소프트웨어 아키텍처의 필수 요소입니다. 하지만 많은 프레임워크가 제공하는 DI 컨테이너는 복잡하고 마법처럼 느껴집니다. 데코레이터, 메타클래스, 리플렉션을 사용해서 의존성을 자동으로 주입합니다. 이것은 강력하지만 추론하기 어렵습니다. 어디서 의존성이 오는지, 어떤 순서로 초기화되는지 코드만 봐서는 알기 어렵습니다.

함수형 프로그래밍은 더 단순한 해법을 제시합니다. 1장에서 배운 클로저를 기억하시나요? 함수는 자신이 생성된 환경을 기억할 수 있습니다. 이것이 바로 의존성 주입입니다. 의존성을 함수에 주입하는 것이 아니라, 의존성을 포함하는 환경에서 함수를 생성하는 것입니다.

전통적인 DI를 먼저 봅시다. 사용자 서비스가 데이터베이스와 이메일 발송자에 의존한다고 가정해봅시다.

```python
# === 이 장에서 사용할 타입들 ===
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable, Protocol, TypeVar

# 5장의 Result 타입 재사용 (실행 가능한 코드를 위해 재정의)
T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Ok[T]:
    """성공 값을 담는 Result 타입"""
    value: T

    def is_ok(self) -> bool: return True
    def is_err(self) -> bool: return False
    def unwrap(self) -> T: return self.value
    def unwrap_or(self, default: T) -> T: return self.value

@dataclass(frozen=True)
class Err[E]:
    """에러 값을 담는 Result 타입"""
    error: E

    def is_ok(self) -> bool: return False
    def is_err(self) -> bool: return True
    def unwrap(self) -> T: raise ValueError(f"Err: {self.error}")
    def unwrap_or(self, default: T) -> T: return default

# Result 타입 별칭
Result = Ok[T] | Err[E]

# 도메인 모델
@dataclass
class User:
    name: str
    email: str
    id: Optional[str] = None

# Database, EmailSender는 Protocol로 정의 (덕 타이핑)
# 실제 구현은 PostgreSQL, SMTP 등이 될 수 있음
class Database(Protocol):
    """데이터베이스 인터페이스"""
    async def find_user_by_email(self, email: str) -> Optional[User]: ...
    async def save_user(self, user: User) -> None: ...

class EmailSender(Protocol):
    """이메일 발송 인터페이스"""
    async def send_welcome_email(self, user: User) -> None: ...

# 전통적인 클래스 기반 DI
class UserService:
    """사용자 관련 비즈니스 로직"""
    
    def __init__(self, db: Database, email_sender: EmailSender):
        self.db = db
        self.email_sender = email_sender
    
    async def create_user(self, name: str, email: str) -> Result[User, str]:
        """새 사용자를 생성합니다"""
        # 중복 확인
        existing = await self.db.find_user_by_email(email)
        if existing:
            return Err("이미 존재하는 이메일입니다")
        
        # 사용자 생성
        user = User(name=name, email=email)
        await self.db.save_user(user)
        
        # 환영 이메일 발송
        await self.email_sender.send_welcome_email(user)
        
        return Ok(user)

# 의존성 수동 주입
db = Database(connection_string="...")
email_sender = EmailSender(smtp_config="...")
user_service = UserService(db, email_sender)

# 사용
result = await user_service.create_user("철수", "chulsoo@example.com")
```

이 방식은 작동하지만 몇 가지 문제가 있습니다. 첫째, UserService는 상태를 가진 객체입니다. self.db와 self.email_sender를 필드로 저장하고 있죠. 이것은 동시성 문제를 일으킬 수 있습니다. 둘째, 테스트하려면 UserService 인스턴스를 만들어야 합니다. 의존성을 목(mock)으로 교체하는 것이 번거롭습니다. 셋째, 의존성이 많아지면 생성자가 복잡해집니다.

함수형 접근을 봅시다. 클래스 대신 함수를 사용하고, 생성자에서 의존성을 받는 대신 **클로저(Closure)**를 사용합니다.

```python
from typing import Callable, Awaitable

# 타입 별칭으로 의존성 시그니처를 명확히 합니다
DatabaseFind = Callable[[str], Awaitable[Optional[User]]]
DatabaseSave = Callable[[User], Awaitable[None]]
EmailSend = Callable[[User], Awaitable[None]]

def make_user_service(
    find_user_by_email: DatabaseFind,
    save_user: DatabaseSave,
    send_welcome_email: EmailSend
):
    """의존성을 주입받아 사용자 서비스를 생성합니다"""
    
    async def create_user(name: str, email: str) -> Result[User, str]:
        """새 사용자를 생성합니다"""
        # 중복 확인
        existing = await find_user_by_email(email)
        if existing:
            return Err("이미 존재하는 이메일입니다")
        
        # 사용자 생성
        user = User(name=name, email=email)
        await save_user(user)
        
        # 환영 이메일 발송
        await send_welcome_email(user)
        
        return Ok(user)
    
    # create_user 함수는 의존성을 클로저로 캡처합니다
    return create_user

# 실제 의존성으로 서비스 생성
create_user = make_user_service(
    find_user_by_email=db.find_user_by_email,
    save_user=db.save_user,
    send_welcome_email=email_sender.send_welcome_email
)

# 사용 (의존성이 이미 주입되어 있음)
result = await create_user("철수", "chulsoo@example.com")
```

이 접근의 장점을 봅시다. 첫째, create_user는 순수 함수에 가깝습니다. 외부 상태를 변경하지 않고, 의존성은 클로저에 캡처되어 있습니다. 둘째, 테스트가 매우 쉽습니다. 의존성을 람다로 교체하기만 하면 됩니다.

```python
# 테스트: 의존성을 간단한 async 함수로 교체
# 주의: Python은 async lambda를 지원하지 않으므로 async 함수를 정의합니다

async def mock_find_user(email: str):
    return None  # 항상 존재하지 않음

async def mock_save_user(user):
    pass  # 아무것도 하지 않음

async def mock_send_email(user):
    pass  # 아무것도 하지 않음

test_create_user = make_user_service(
    find_user_by_email=mock_find_user,
    save_user=mock_save_user,
    send_welcome_email=mock_send_email
)

# 테스트 실행
result = await test_create_user("테스트", "test@example.com")
assert result.is_ok()
```

셋째, 부분 적용이 가능합니다. 일부 의존성만 주입하고 나머지는 나중에 주입할 수 있습니다.

```python
def make_user_service_partial(
    find_user_by_email: DatabaseFind,
    save_user: DatabaseSave
):
    """이메일 발송자는 나중에 주입받습니다"""
    
    def with_email_sender(send_welcome_email: EmailSend):
        async def create_user(name: str, email: str) -> Result[User, str]:
            # 같은 로직...
            pass
        return create_user
    
    return with_email_sender

# 데이터베이스 의존성만 먼저 주입
partial_service = make_user_service_partial(
    find_user_by_email=db.find_user_by_email,
    save_user=db.save_user
)

# 나중에 이메일 발송자 주입
create_user = partial_service(email_sender.send_welcome_email)
```

### 함수형 의존성 주입의 핵심: "환경 기억하기"

이 패턴의 핵심은 1장에서 배운 **클로저(Closure)**입니다.

1.  `make_user_service`는 의존성(DB, 이메일 등)을 인자로 받습니다.
2.  내부 함수(`create_user`)는 이 의존성들을 몰래 훔쳐보고 기억합니다(Capture).
3.  우리는 `create_user`만 사용하지만, 이 함수는 이미 의존성을 몸에 지니고 있습니다.

이것이 바로 함수형 프로그래밍에서 상태와 환경을 다루는 방식입니다. 복잡한 프레임워크나 매직이 전혀 없습니다. 단지 "함수가 자신이 태어난 환경을 기억한다"는 언어의 특성을 이용할 뿐입니다.

우리의 `create_user` 함수는 "의존성"이라는 환경을 읽어서(Read) 사용자를 생성하는 작업을 수행합니다.

실무에서는 보통 여러 함수가 같은 의존성을 공유합니다. 이럴 때는 의존성을 하나의 컨텍스트 객체로 묶는 것이 편리합니다.

```python
from dataclasses import dataclass

@dataclass
class Dependencies:
    """애플리케이션의 모든 의존성"""
    find_user_by_email: DatabaseFind
    save_user: DatabaseSave
    send_welcome_email: EmailSend
    # 다른 의존성들...

def make_user_service(deps: Dependencies):
    """의존성 컨텍스트를 받아 서비스를 생성합니다"""
    
    async def create_user(name: str, email: str) -> Result[User, str]:
        existing = await deps.find_user_by_email(email)
        if existing:
            return Err("이미 존재하는 이메일입니다")
        
        user = User(name=name, email=email)
        await deps.save_user(user)
        await deps.send_welcome_email(user)
        
        return Ok(user)
    
    async def delete_user(user_id: str) -> Result[None, str]:
        # delete도 같은 deps를 사용합니다
        pass
    
    return {
        "create_user": create_user,
        "delete_user": delete_user
    }

# 의존성을 한 번에 주입
deps = Dependencies(
    find_user_by_email=db.find_user_by_email,
    save_user=db.save_user,
    send_welcome_email=email_sender.send_welcome_email
)

user_service = make_user_service(deps)

# 사용
result = await user_service["create_user"]("철수", "chulsoo@example.com")
```

이 패턴의 핵심은 이것입니다. 복잡한 DI 프레임워크가 필요 없습니다. 고차 함수와 클로저만으로 충분합니다. 함수는 자신이 생성된 환경을 기억하고, 그 환경에는 의존성이 포함되어 있습니다. 이것은 명시적이고, 추론하기 쉽고, 테스트하기 쉽습니다. 마법이 없고, 모든 것이 명확합니다.

### 함수형 DI의 테스트 이점

함수형 의존성 주입의 가장 큰 장점은 테스트 용이성입니다:

```python
import pytest

# 1. 단위 테스트: 의존성을 완전히 제어
async def test_create_user_success():
    """사용자 생성 성공 케이스"""
    saved_users = []
    sent_emails = []

    async def mock_find(email): return None
    async def mock_save(user): saved_users.append(user)
    async def mock_email(user): sent_emails.append(user)

    create_user = make_user_service(mock_find, mock_save, mock_email)
    result = await create_user("철수", "chulsoo@test.com")

    assert result.is_ok()
    assert len(saved_users) == 1
    assert len(sent_emails) == 1

async def test_create_user_duplicate_email():
    """중복 이메일 케이스"""
    existing_user = User(name="기존유저", email="exists@test.com")

    async def mock_find(email): return existing_user  # 이미 존재함
    async def mock_save(user): pass
    async def mock_email(user): pass

    create_user = make_user_service(mock_find, mock_save, mock_email)
    result = await create_user("새유저", "exists@test.com")

    assert result.is_err()
    assert "이미 존재" in result.error

# 2. 부작용 추적: 무엇이 호출되었는지 정확히 검증
async def test_email_only_sent_on_success():
    """이메일은 저장 성공 후에만 발송"""
    email_sent = False

    async def mock_find(email): return None
    async def mock_save(user): raise Exception("DB 오류!")
    async def mock_email(user):
        nonlocal email_sent
        email_sent = True

    create_user = make_user_service(mock_find, mock_save, mock_email)

    # save가 실패해도 이메일은 시도되지 않아야 함
    # (실제로는 예외가 발생하므로 Result로 감싸야 함)
```

클래스 기반 DI와 비교:
- **클래스**: mock 객체 생성, 메서드 패칭, 복잡한 설정
- **함수형**: 간단한 async 함수만 전달, 추가 도구 불필요

## 암묵적 의존성 해결: Reader Monad와 ContextVars

함수형 의존성 주입은 명확하지만, 모든 함수에 `deps`나 `config`를 인자로 전달해야 하는 단점이 있습니다. 흔히 **Prop Drilling**이라고 부르는 문제입니다.

```python
# Prop Drilling: deps를 계속 전달해야 함
async def handle_request(req, deps):
    await process_order(req.order_id, deps)

async def process_order(order_id, deps):
    await validate_order(order_id, deps)
    await save_order(order_id, deps)

async def validate_order(order_id, deps):
    # 여기서 실제로 deps를 사용
    pass
```

순수 함수형 언어에서는 이를 **Reader Monad**라는 패턴으로 해결합니다. 함수가 "값을 반환하는 것"이 아니라 "환경을 받아서 값을 반환하는 계산"을 반환하게 하는 것입니다. 하지만 Python에서 Reader Monad를 직접 구현하면 코드가 매우 복잡해집니다 (`flatMap` 지옥).

Python에는 더 실용적인 해결책이 있습니다. 바로 `contextvars`입니다.

```python
from contextvars import ContextVar

# 1. 컨텍스트 변수 정의 (기본값 설정 가능)
# 이것이 우리의 "Reader 환경"입니다
request_id_var: ContextVar[str] = ContextVar("request_id", default="unknown")
current_user_var: ContextVar[User] = ContextVar("current_user")

# 2. 값 설정 (미들웨어 등에서)
async def middleware_handler(request):
    token = request.headers.get("Authorization")
    user = extract_user(token)
    
    # 컨텍스트 설정 (이후 호출되는 모든 함수에서 유효)
    token = current_user_var.set(user)
    
    try:
        await next_handler(request)
    finally:
        # 사용 후 정리 (필수!)
        current_user_var.reset(token)

# 3. 값 사용 (인자 전달 없이!)
async def process_business_logic():
    # 마치 전역 변수처럼 접근하지만, 요청마다 격리됨
    user = current_user_var.get()
    print(f"Processing for {user.name}")
```

`contextvars`는 **비동기 작업(Task)별로 독립적인 저장소**를 제공합니다. 이는 함수형 프로그래밍의 Reader Monad가 하는 역할(암묵적인 환경 전달)을 언어 차원에서 지원하는 것입니다.

**주의할 점**: `contextvars`는 "요청 컨텍스트"(`request_id`, `current_user`, `db_session`) 같은 **실행 문맥**을 전달할 때만 사용하세요. 또한, ContextVar에 저장되는 객체는 가능한 **불변(Immutable)**이어야 합니다. `dict`나 `list` 같은 가변 객체를 저장하고 수정하면, 예기치 않은 부수 효과가 발생할 수 있습니다. `frozen dataclass`나 `NamedTuple`을 사용하는 것이 안전합니다.

`UserService` 같은 **정적 의존성**은 앞서 배운 클로저 방식(명시적 주입)을 사용하는 것이 좋습니다. 비즈니스 로직과 인프라 구성을 분리하기 위해서입니다.

## 미들웨어: 함수 합성의 실용적 응용

웹 애플리케이션을 만들 때 요청이 들어오면 여러 단계를 거쳐 처리됩니다. 로깅, 인증, 권한 확인, 요청 파싱, 비즈니스 로직 실행, 응답 직렬화, 에러 처리 등입니다. 이런 횡단 관심사(cross-cutting concerns)를 어떻게 깔끔하게 구현할까요? 미들웨어 패턴이 답입니다.

미들웨어는 1장에서 배운 함수 합성의 실용적 응용입니다. 각 미들웨어는 요청을 받아서 처리하고 다음 미들웨어에 전달하는 함수입니다. 여러 미들웨어를 합성하면 전체 요청-응답 파이프라인이 됩니다.

간단한 HTTP 서버를 생각해봅시다. 요청과 응답을 표현하는 간단한 타입부터 정의하겠습니다.

```python
from dataclasses import dataclass
from typing import Dict, Any, Callable, Awaitable

@dataclass
class Request:
    """HTTP 요청"""
    method: str
    path: str
    headers: Dict[str, str]
    body: Any

@dataclass
class Response:
    """HTTP 응답"""
    status: int
    headers: Dict[str, str]
    body: Any

# 핸들러는 요청을 받아서 응답을 반환합니다
Handler = Callable[[Request], Awaitable[Response]]

# 미들웨어는 핸들러를 받아서 새로운 핸들러를 반환합니다
Middleware = Callable[[Handler], Handler]
```

타입을 자세히 봅시다. Handler는 Request를 받아서 Response를 반환하는 함수입니다. Middleware는 Handler를 받아서 Handler를 반환하는 함수입니다.

### 미들웨어의 본질: 함수 감싸기 (Decorating)

미들웨어가 하는 일은 핸들러 함수를 감싸서(wrapping), 앞뒤에 로직을 추가하는 것입니다. 이것은 파이썬의 데코레이터와 비슷하지만, 동적으로 여러 개를 이어 붙일 수 있다는 점이 다릅니다.

핵심은 **"합성(Composition)"**입니다.

- **로그 미들웨어**: "요청 기록" + "원래 핸들러" + "응답 기록"
- **인증 미들웨어**: "인증 확인" + "원래 핸들러"

이것들을 계속 이어 붙이면 거대한 파이프라인이 됩니다.

로깅 미들웨어를 만들어봅시다.

```python
def logging_middleware(handler: Handler) -> Handler:
    """요청과 응답을 로깅하는 미들웨어"""
    
    async def wrapped(request: Request) -> Response:
        print(f"→ {request.method} {request.path}")
        
        # 다음 핸들러를 호출합니다
        response = await handler(request)
        
        print(f"← {response.status}")
        return response
    
    # 래핑된 핸들러를 반환합니다
    return wrapped
```

이 미들웨어는 요청을 로깅하고, 다음 핸들러를 호출하고, 응답을 로깅합니다. 핵심은 handler(request)를 호출하는 부분입니다. 이것이 다음 단계로의 제어 이전입니다. 미들웨어는 앞뒤로 무언가를 할 수 있지만, 반드시 다음 핸들러를 호출해야 합니다.

인증 미들웨어를 추가해봅시다.

```python
def auth_middleware(handler: Handler) -> Handler:
    """인증을 확인하는 미들웨어"""
    
    async def wrapped(request: Request) -> Response:
        # Authorization 헤더 확인
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            # 인증 실패: 즉시 응답을 반환하고 다음 핸들러를 호출하지 않습니다
            return Response(
                status=401,
                headers={"Content-Type": "application/json"},
                body={"error": "인증이 필요합니다"}
            )
        
        # 인증 성공: 다음 핸들러를 호출합니다
        return await handler(request)
    
    return wrapped
```

auth_middleware는 조건부로 다음 핸들러를 호출합니다. 인증이 실패하면 바로 401 응답을 반환하고, 파이프라인을 중단합니다. 이것은 Railway-Oriented Programming의 실용적 응용입니다. 성공 경로는 다음 단계로 진행하고, 실패 경로는 즉시 종료합니다.

이제 여러 미들웨어를 합성해봅시다.

```python
def compose_middleware(*middlewares: Middleware) -> Middleware:
    """여러 미들웨어를 하나로 합성합니다"""
    
    def combined(handler: Handler) -> Handler:
        # 오른쪽에서 왼쪽으로 적용합니다
        # compose(f, g, h)(handler) = f(g(h(handler)))
        result = handler
        for middleware in reversed(middlewares):
            result = middleware(result)
        return result
    
    return combined

# 실제 핸들러 (비즈니스 로직)
async def hello_handler(request: Request) -> Response:
    """간단한 핸들러"""
    return Response(
        status=200,
        headers={"Content-Type": "text/plain"},
        body=f"Hello from {request.path}!"
    )

# 미들웨어를 합성합니다
app = compose_middleware(
    logging_middleware,
    auth_middleware
)(hello_handler)

# 사용
request = Request(
    method="GET",
    path="/hello",
    headers={"Authorization": "Bearer token123"},
    body=None
)

response = await app(request)
```

실행 흐름을 추적해봅시다. compose_middleware는 오른쪽에서 왼쪽으로 미들웨어를 적용합니다. 따라서 실제 구조는 이렇습니다.

```
logging_middleware(auth_middleware(hello_handler))
```

요청이 들어오면 이런 순서로 실행됩니다.

1. logging_middleware가 "→ GET /hello"를 출력합니다.
2. auth_middleware가 인증을 확인합니다.
3. 인증이 성공하면 hello_handler가 실행됩니다.
4. hello_handler가 응답을 반환합니다.
5. auth_middleware가 응답을 그대로 전달합니다.
6. logging_middleware가 "← 200"을 출력합니다.

이것은 양파와 같은 구조입니다. 각 미들웨어는 레이어이고, 요청은 바깥쪽에서 안쪽으로 들어가고, 응답은 안쪽에서 바깥쪽으로 나옵니다.

더 복잡한 미들웨어를 만들어봅시다. 에러를 포착하고 500 응답으로 변환하는 미들웨어입니다.

```python
def error_handling_middleware(handler: Handler) -> Handler:
    """에러를 포착하고 적절한 응답으로 변환합니다"""
    
    async def wrapped(request: Request) -> Response:
        try:
            return await handler(request)
        except ValueError as e:
            # 검증 에러: 400
            return Response(
                status=400,
                headers={"Content-Type": "application/json"},
                body={"error": str(e)}
            )
        except PermissionError as e:
            # 권한 에러: 403
            return Response(
                status=403,
                headers={"Content-Type": "application/json"},
                body={"error": "권한이 없습니다"}
            )
        except Exception as e:
            # 그 외 에러: 500
            print(f"내부 에러: {e}")
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body={"error": "내부 서버 오류"}
            )
    
    return wrapped
```

이 미들웨어를 가장 바깥쪽에 배치하면 모든 에러를 포착합니다.

```python
app = compose_middleware(
    error_handling_middleware,  # 가장 바깥쪽
    logging_middleware,
    auth_middleware
)(hello_handler)
```

미들웨어 패턴의 아름다움은 합성 가능성입니다. 각 미들웨어는 독립적이고, 하나의 명확한 책임만 가지며, 순서를 바꾸거나 추가하거나 제거하기 쉽습니다. 에러 처리, 로깅, 인증 같은 횡단 관심사를 비즈니스 로직과 분리할 수 있습니다.

실무에서는 요청 컨텍스트를 전달하는 것도 중요합니다. 예를 들어, 인증 미들웨어가 사용자 정보를 추출하면 다음 핸들러가 그 정보를 사용할 수 있어야 합니다. **1장의 불변성 원칙**을 지켜서, 요청 객체를 직접 수정하지 않고 새로운 객체를 만듭니다.

```python
from dataclasses import dataclass, replace

@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str]
    body: Any
    context: Dict[str, Any]  # 컨텍스트를 추가합니다

def auth_middleware_with_context(handler: Handler) -> Handler:
    """인증하고 사용자 정보를 컨텍스트에 저장합니다"""

    async def wrapped(request: Request) -> Response:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return Response(status=401, headers={}, body={"error": "인증 필요"})

        # 토큰에서 사용자 정보 추출 (시뮬레이션)
        user_id = extract_user_id(auth_header)

        # 불변성 유지: 새 Request 생성 (1장의 원칙)
        new_request = replace(
            request,
            context={**request.context, "user_id": user_id}
        )

        return await handler(new_request)

    return wrapped

# 핸들러에서 사용
async def user_profile_handler(request: Request) -> Response:
    user_id = request.context["user_id"]
    # user_id를 사용해서 프로필을 가져옵니다...
    pass
```

**FP 원칙과의 조화**: `request.context["user_id"] = user_id` 같은 가변 수정은 1장의 불변성 원칙과 충돌합니다. `dataclasses.replace`를 사용하면, 원래 request는 그대로 두고 **새로운 request를 만들어서** 다음 핸들러에 전달합니다. 이렇게 하면 미들웨어 체인의 각 단계가 독립적이고 예측 가능해집니다.

이 패턴은 Express.js의 미들웨어, Django의 미들웨어, FastAPI의 dependencies와 본질적으로 같습니다. 표면적으로는 다르게 보이지만, 모두 함수 합성입니다. 각 프레임워크가 제공하는 것은 미들웨어를 등록하고 실행하는 편의 기능일 뿐입니다. 핵심 아이디어는 같습니다. 함수를 합성해서 파이프라인을 만드는 것입니다.

## 트랜잭션과 Monad: 컨텍스트 매니저의 재발견

데이터베이스 트랜잭션은 복잡합니다. 여러 작업을 원자적으로 실행하고, 하나라도 실패하면 모두 롤백해야 합니다. 파이썬의 컨텍스트 매니저는 이것을 우아하게 표현합니다.

```python
async with db.transaction():
    await db.insert_user(user)
    await db.insert_audit_log(log)
    # 블록을 벗어날 때 자동으로 커밋
    # 예외가 발생하면 자동으로 롤백
```

컨텍스트 매니저는 편리하지만, 합성이 어렵습니다. 트랜잭션 안에서 또 다른 트랜잭션을 시작하면 어떻게 될까요? 함수가 트랜잭션을 필요로 하는지 어떻게 알 수 있을까요? 이런 문제들을 함수형으로 해결해봅시다.

먼저 트랜잭션이 무엇인지 다시 생각해봅시다. 트랜잭션은 "성공하면 커밋, 실패하면 롤백"하는 계산입니다. 이것은 Result Monad와 매우 비슷합니다. Result는 "성공하면 값, 실패하면 에러"였죠. 트랜잭션을 Result로 표현할 수 있을까요?

트랜잭션 컨텍스트를 명시적으로 만들어봅시다.

```python
from typing import TypeVar, Generic, Callable, Awaitable
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Transaction:
    """트랜잭션 컨텍스트"""
    connection: Any  # 데이터베이스 연결
    is_committed: bool = False
    is_rolled_back: bool = False
    
    async def commit(self):
        """트랜잭션을 커밋합니다"""
        if not self.is_rolled_back:
            await self.connection.commit()
            self.is_committed = True
    
    async def rollback(self):
        """트랜잭션을 롤백합니다"""
        if not self.is_committed:
            await self.connection.rollback()
            self.is_rolled_back = True

# 트랜잭션 안에서 실행되는 함수의 타입 별칭
# 참고: 실제로는 구체적인 T, E와 함께 사용됩니다 (예: Callable[[Transaction], Awaitable[Result[User, str]]])
from typing import TypeAlias
TransactionAction: TypeAlias = Callable[[Transaction], Awaitable[Result]]
```

이제 트랜잭션을 실행하는 함수를 만듭니다.

```python
async def run_transaction[T, E](
    db: Database,
    action: Callable[[Transaction], Awaitable[Result[T, E]]]
) -> Result[T, E]:
    """트랜잭션을 실행합니다"""
    connection = await db.get_connection()
    await connection.begin()
    
    tx = Transaction(connection=connection)
    
    try:
        # 액션을 실행합니다
        result = await action(tx)
        
        if result.is_ok():
            # 성공: 커밋
            await tx.commit()
        else:
            # 실패: 롤백
            await tx.rollback()
        
        return result
    
    except Exception as e:
        # 예외 발생: 롤백
        await tx.rollback()
        return Err(str(e))
    
    finally:
        await connection.close()
```

이제 트랜잭션 안에서 실행할 작업을 작성합니다. 작업은 Transaction을 받아서 Result를 반환하는 함수입니다.

```python
async def create_user_with_audit(
    tx: Transaction,
    user: User
) -> Result[User, str]:
    """트랜잭션 안에서 사용자를 생성하고 감사 로그를 남깁니다"""
    
    # 1. 사용자 저장
    try:
        await tx.connection.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (user.name, user.email)
        )
    except Exception as e:
        return Err(f"사용자 저장 실패: {e}")
    
    # 2. 감사 로그 저장
    try:
        await tx.connection.execute(
            "INSERT INTO audit_log (action, user_email) VALUES (?, ?)",
            ("create_user", user.email)
        )
    except Exception as e:
        return Err(f"감사 로그 저장 실패: {e}")
    
    return Ok(user)

# 사용
result = await run_transaction(
    db,
    lambda tx: create_user_with_audit(tx, user)
)

if result.is_ok():
    print("사용자 생성 성공")
else:
    print(f"사용자 생성 실패: {result.error}")
```

이 접근의 장점은 명시성입니다. create_user_with_audit의 시그니처를 보면 이 함수가 트랜잭션을 필요로 한다는 것을 알 수 있습니다. Transaction을 인자로 받으니까요. 그리고 Result를 반환하므로 실패할 수 있다는 것도 알 수 있습니다.

더 나아가서, 여러 트랜잭션 작업을 합성할 수 있습니다. 4장에서 배운 flatMap을 기억하시나요? 트랜잭션 작업도 flatMap으로 합성할 수 있습니다.

```python
def flatmap_transaction[T, E, U](
    action1: Callable[[Transaction], Awaitable[Result[T, E]]],
    func: Callable[[T], Callable[[Transaction], Awaitable[Result[U, E]]]]
) -> Callable[[Transaction], Awaitable[Result[U, E]]]:
    """두 트랜잭션 작업을 합성합니다"""

    async def combined(tx: Transaction) -> Result[U, E]:
        # 첫 번째 작업 실행
        result1 = await action1(tx)
        
        if result1.is_err():
            # 실패하면 두 번째 작업을 실행하지 않습니다
            return result1
        
        # 성공하면 결과를 사용해서 두 번째 작업 실행
        action2 = func(result1.unwrap())
        return await action2(tx)
    
    return combined

# 사용 예제
async def save_user(tx: Transaction, user: User) -> Result[User, str]:
    """사용자를 저장합니다"""
    # 구현...
    return Ok(user)

async def save_audit_log(tx: Transaction, user: User) -> Result[None, str]:
    """감사 로그를 저장합니다"""
    # 구현...
    return Ok(None)

# 두 작업을 합성
combined_action = flatmap_transaction(
    lambda tx: save_user(tx, user),
    lambda saved_user: lambda tx: save_audit_log(tx, saved_user)
)

# 하나의 트랜잭션으로 실행
result = await run_transaction(db, combined_action)
```

이것은 복잡해 보이지만 패턴은 명확합니다. 각 작업은 Transaction을 받아서 Result를 반환하고, flatmap_transaction으로 합성하면 하나의 큰 작업이 됩니다. 첫 번째 작업이 실패하면 두 번째 작업은 실행되지 않습니다. 이것은 Railway-Oriented Programming입니다.

실무에서는 이런 저수준 합성보다는 헬퍼 함수를 만들어서 사용하는 것이 편리합니다.

```python
class TransactionBuilder:
    """트랜잭션 작업을 체이닝하는 빌더"""
    
    def __init__(self):
        self.actions = []
    
    def add(self, action: TransactionAction) -> 'TransactionBuilder':
        """작업을 추가합니다"""
        self.actions.append(action)
        return self
    
    def build(self) -> TransactionAction:
        """모든 작업을 하나로 합성합니다"""
        async def combined(tx: Transaction) -> Result[list, str]:
            results = []
            for action in self.actions:
                result = await action(tx)
                if result.is_err():
                    return result
                results.append(result.unwrap())
            return Ok(results)
        
        return combined

# 사용
builder = TransactionBuilder()
builder.add(lambda tx: save_user(tx, user))
builder.add(lambda tx: save_audit_log(tx, user))
builder.add(lambda tx: update_statistics(tx))

result = await run_transaction(db, builder.build())
```

트랜잭션을 Result와 결합하는 이 접근은 여러 장점이 있습니다. 첫째, 트랜잭션 범위가 명확합니다. run_transaction으로 감싸진 부분이 트랜잭션입니다. 둘째, 에러 처리가 자연스럽습니다. Result의 Err가 자동으로 롤백을 유발합니다. 셋째, 합성 가능합니다. 여러 트랜잭션 작업을 조합해서 복잡한 비즈니스 로직을 만들 수 있습니다.

컨텍스트 매니저와 비교해봅시다. 컨텍스트 매니저는 편리하지만 암묵적입니다. 어디서 트랜잭션이 시작되고 끝나는지 블록을 벗어나야 알 수 있습니다. 함수형 접근은 명시적입니다. Transaction 인자를 보면 이 함수가 트랜잭션 안에서 실행된다는 것을 알 수 있습니다.

## 아키텍처 패턴의 통합: 전체 그림

지금까지 배운 세 가지 패턴을 통합해봅시다. 의존성 주입, 미들웨어, 트랜잭션을 모두 사용하는 실용적인 예제입니다. 사용자 등록 API를 만들어보겠습니다.

먼저 의존성을 정의합니다.

```python
@dataclass
class Dependencies:
    """애플리케이션 의존성"""
    db: Database
    email_sender: EmailSender
    logger: Logger

def make_dependencies() -> Dependencies:
    """의존성을 생성합니다"""
    return Dependencies(
        db=Database(connection_string="..."),
        email_sender=EmailSender(smtp_config="..."),
        logger=Logger()
    )
```

트랜잭션 작업을 정의합니다.

```python
async def register_user_transaction(
    tx: Transaction,
    deps: Dependencies,
    name: str,
    email: str
) -> Result[User, str]:
    """트랜잭션 안에서 사용자를 등록합니다"""
    
    # 1. 중복 확인
    existing = await tx.connection.fetch_one(
        "SELECT * FROM users WHERE email = ?", (email,)
    )
    if existing:
        return Err("이미 존재하는 이메일입니다")
    
    # 2. 사용자 생성
    user = User(name=name, email=email)
    await tx.connection.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (user.name, user.email)
    )
    
    # 3. 환영 이메일 발송 (트랜잭션 밖에서 실행되어야 함)
    # 일단 여기서는 플래그만 설정하고, 트랜잭션이 성공하면 발송합니다
    
    return Ok(user)
```

핸들러를 정의합니다.

```python
def make_register_handler(deps: Dependencies) -> Handler:
    """의존성을 주입받아 등록 핸들러를 생성합니다"""
    
    async def handle(request: Request) -> Response:
        # 요청 파싱
        try:
            name = request.body["name"]
            email = request.body["email"]
        except KeyError as e:
            return Response(
                status=400,
                headers={"Content-Type": "application/json"},
                body={"error": f"필수 필드 누락: {e}"}
            )
        
        # 트랜잭션 실행
        result = await run_transaction(
            deps.db,
            lambda tx: register_user_transaction(tx, deps, name, email)
        )
        
        if result.is_err():
            return Response(
                status=400,
                headers={"Content-Type": "application/json"},
                body={"error": result.error}
            )
        
        user = result.unwrap()
        
        # 트랜잭션 성공 후 이메일 발송
        await deps.email_sender.send_welcome_email(user)
        
        return Response(
            status=201,
            headers={"Content-Type": "application/json"},
            body={"id": user.id, "name": user.name, "email": user.email}
        )
    
    return handle
```

미들웨어를 적용합니다.

```python
# 의존성 생성
deps = make_dependencies()

# 핸들러 생성 (의존성 주입)
register_handler = make_register_handler(deps)

# 미들웨어 합성
app = compose_middleware(
    error_handling_middleware,
    logging_middleware,
    rate_limiting_middleware,
    auth_middleware
)(register_handler)

# 사용
request = Request(
    method="POST",
    path="/register",
    headers={"Authorization": "Bearer token"},
    body={"name": "철수", "email": "chulsoo@example.com"}
)

response = await app(request)
```

전체 흐름을 봅시다. 요청이 들어오면 먼저 미들웨어 체인을 통과합니다. 에러 처리, 로깅, 속도 제한, 인증을 거치죠. 모든 미들웨어를 통과하면 register_handler가 실행됩니다. 핸들러는 클로저로 캡처된 의존성을 사용합니다. 트랜잭션을 시작하고, 사용자를 등록하고, 트랜잭션을 커밋합니다. 트랜잭션이 성공하면 이메일을 발송합니다. 최종적으로 응답을 반환하고, 응답은 미들웨어 체인을 거꾸로 통과해서 클라이언트에게 전달됩니다.

이 모든 것이 함수 합성입니다. 미들웨어는 핸들러를 합성하고, 핸들러는 트랜잭션 작업을 실행하고, 트랜잭션 작업은 Result를 합성합니다. 각 레이어는 독립적이고, 테스트하기 쉽고, 재사용 가능합니다. 복잡한 DI 컨테이너나 프레임워크 마법 없이, 순수한 함수형 개념만으로 견고한 아키텍처를 만들었습니다.

---

## 실전 적용 시 주의사항 및 함정

함수형 아키텍처 패턴은 강력하지만, **실무에서 흔히 마주치는 함정들**이 있습니다. 이 섹션에서는 성능 이슈, 오남용 패턴, 그리고 디버깅 팁을 다룹니다.

### 1. ContextVars 오남용 경고 ⚠️

**안티패턴**: 모든 의존성을 ContextVars에 넣기

```python
# ❌ 잘못된 사용 - 정적 의존성까지 ContextVars에!
user_service_var = ContextVar("user_service")
db_var = ContextVar("db")
logger_var = ContextVar("logger")

async def handle_request(request):
    # 모든 의존성을 ContextVar에서 가져옴
    user_service = user_service_var.get()
    db = db_var.get()
    ...
```

**문제점**:
- 함수 시그니처만 봐서는 어떤 의존성이 필요한지 알 수 없습니다.
- 코드 추론이 어렵고, IDE 자동완성도 작동하지 않습니다.
- 테스트 시 ContextVar를 일일이 설정해야 합니다.

**올바른 구분**:

```python
# ✅ 요청별로 달라지는 실행 문맥만 ContextVars 사용
request_id_var: ContextVar[str] = ContextVar("request_id")
current_user_var: ContextVar[Optional[User]] = ContextVar("current_user", default=None)

# ✅ 애플리케이션 수명 동안 고정된 의존성은 클로저 사용
def make_handler(db: Database, logger: Logger):
    """정적 의존성은 클로저로 캡처"""
    async def handle(request: Request):
        # 실행 문맥만 ContextVar에서 가져옴
        request_id = request_id_var.get()
        logger.info(f"[{request_id}] Processing...")

        # 정적 의존성은 클로저에서 사용
        await db.query(...)
    return handle
```

**원칙**:
- **ContextVars**: `request_id`, `current_user`, `db_session` (요청별 값)
- **클로저**: `Database`, `EmailSender`, `Logger` (정적 구성)

---

### 2. 트랜잭션 함정 🚨

#### 함정 1: 중첩 트랜잭션 미처리

```python
# ❌ 위험: 중첩 트랜잭션을 고려하지 않음
async def outer_action(tx: Transaction):
    await save_user(tx)  # OK
    await inner_transaction(tx)  # ← 문제!

async def inner_transaction(tx: Transaction):
    # 이미 트랜잭션이 시작된 상태에서 또 begin() 호출하면?
    await tx.connection.begin()  # 에러 발생 가능
```

**해결책**: PostgreSQL/MySQL은 SAVEPOINT를 사용해야 합니다.

```python
# ✅ SAVEPOINT 사용
async def create_nested_transaction(parent_tx: Transaction) -> Transaction:
    """중첩 트랜잭션 (SAVEPOINT) 생성"""
    savepoint_name = f"sp_{id(parent_tx)}"
    await parent_tx.connection.execute(f"SAVEPOINT {savepoint_name}")

    return Transaction(
        connection=parent_tx.connection,
        savepoint=savepoint_name
    )
```

---

#### 함정 2: 긴 트랜잭션으로 인한 성능 저하

```python
# ❌ 안티패턴: 트랜잭션 안에서 외부 API 호출
async def register_user_bad(tx: Transaction, user: User):
    await tx.connection.execute("INSERT INTO users ...")

    # DB 커넥션을 잡고 있는 상태에서 느린 외부 API 호출!
    await send_welcome_email(user)  # 3초 소요
    await notify_slack(user)        # 2초 소요
    # → 총 5초 동안 DB 커넥션 점유 (병목!)
```

**권장 패턴**: 트랜잭션은 DB 작업만, 외부 작업은 밖에서

```python
# ✅ 트랜잭션은 최소화
async def register_user_good(tx: Transaction, user: User) -> Result[User, str]:
    """트랜잭션: DB 작업만"""
    await tx.connection.execute("INSERT INTO users ...")
    return Ok(user)

async def register_user_handler(request: Request):
    # 트랜잭션 실행 (빠름)
    result = await run_transaction(db, lambda tx: register_user_good(tx, user))

    if result.is_ok():
        # 트랜잭션 밖에서 외부 작업 (DB 커넥션 해제됨)
        user = result.unwrap()
        await send_welcome_email(user)
        await notify_slack(user)
```

**핵심**: 트랜잭션 시간 = DB 락 시간. 최소화하세요!

---

#### 함정 3: 데드락 위험

```python
# ❌ 위험: 여러 트랜잭션이 다른 순서로 테이블 접근
# Transaction 1
async with tx1:
    await tx1.lock_table("users")
    await tx1.lock_table("orders")  # ← 데드락!

# Transaction 2 (동시 실행)
async with tx2:
    await tx2.lock_table("orders")
    await tx2.lock_table("users")  # ← 서로 기다림
```

**해결책**: 테이블 접근 순서를 일관되게 유지하세요.

---

### 3. 불변성 vs 부수 효과: 철학적 정리 🤔

8장의 `Transaction`, `Request.context`는 **가변 상태**를 가집니다. 이것이 FP 원칙과 충돌하는 것처럼 보일 수 있습니다.

**순수 FP (Haskell의 ST Monad)**:
```haskell
-- 모든 상태 변경이 타입 시스템에 표시됨
runTransaction :: DB -> Transaction a -> IO (Result a Error)
```

**실용적 FP (Python의 접근)**:
```python
# 부수 효과를 격리하고 명시적으로 표시
async def run_transaction(db, action) -> Result:
    # 부수 효과는 run_transaction 안에 격리됨
    ...
```

**핵심 원칙**:
1. **부수 효과를 제거할 수 없다면**, **범위를 제한**하고 **예측 가능하게** 만드세요.
2. **Transaction은 `run_transaction`으로 격리**되어 있습니다. 밖에서는 순수 함수처럼 보입니다.
3. **부수 효과가 있는 함수는 `async`로 표시**되어 있어, 호출자가 알 수 있습니다.

**함수형 프로그래밍의 실용적 정의**:
> "모든 부수 효과를 제거하는 것이 아니라, **부수 효과를 명시적으로 드러내고 격리하는 것**"

---

### 4. 클로저 메모리 누수 주의 ⚠️

```python
# ❌ 주의: 큰 객체를 클로저에 캡처
def make_handlers(huge_cache: Dict[str, bytes]):  # 1GB 딕셔너리
    # 모든 핸들러가 huge_cache를 참조하므로 메모리 해제 안 됨
    def handler1(): ...  # huge_cache 캡처
    def handler2(): ...  # huge_cache 캡처
    def handler3(): ...  # huge_cache 캡처

    return [handler1, handler2, handler3]
```

**해결책**: 필요한 부분만 추출해서 전달

```python
# ✅ 필요한 값만 캡처
def make_handlers(cache: Dict[str, bytes]):
    specific_value = cache["key"]  # 필요한 값만 추출

    def handler1():
        use(specific_value)  # 전체 cache가 아닌 specific_value만 캡처

    return [handler1]
```

---

### 5. 디버깅 팁: 함수형 코드 추적하기

함수형 코드는 합성이 많아서 스택 트레이스가 깊을 수 있습니다.

**권장사항**:
1. **명시적 함수 이름 사용**: 람다보다는 명명된 함수
2. **중간 결과 로깅**: 각 합성 단계의 출력 기록
3. **타입 힌트 철저히**: IDE의 도움을 받으세요

```python
# ❌ 디버깅 어려움
app = compose(f, g, h)(lambda x: k(l(m(x))))

# ✅ 디버깅 쉬움
def process_data(x):
    step1 = m(x)
    logger.debug(f"After m: {step1}")
    step2 = l(step1)
    logger.debug(f"After l: {step2}")
    return k(step2)

app = compose(f, g, h)(process_data)
```

---

## 연습 문제

아키텍처 패턴을 직접 적용해보세요.

**기본 문제**: 재시도 미들웨어를 구현하세요. 핸들러가 실패하면 자동으로 재시도하고, 최대 재시도 횟수를 초과하면 에러를 반환합니다.

```python
def retry_middleware(max_retries: int = 3) -> Middleware:
    """핸들러를 재시도하는 미들웨어"""
    import asyncio

    def middleware(handler: Handler) -> Handler:
        async def wrapped(request: Request) -> Response:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await handler(request)
                except Exception as e:
                    last_exception = e
                    wait_time = 0.1 * (2 ** attempt)  # 지수 백오프 (Exponential Backoff)
                    print(f"재시도 {attempt + 1}/{max_retries} ({wait_time:.2f}s 후)...")
                    await asyncio.sleep(wait_time)
            
            # 모든 재시도 실패 시 에러 반환
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body={"error": f"최대 재시도 초과: {last_exception}"}
            )
        return wrapped
    return middleware
```

**중급 문제**: 캐싱 레이어를 의존성 주입으로 구현하세요. 함수가 캐시를 의존성으로 받고, 결과를 자동으로 캐시하도록 만드세요.

```python
class Cache:
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    async def set(self, key: str, value: Any, ttl: int):
        pass

def make_cached_function(cache: Cache, func: Callable, ttl: int = 60):
    """함수를 캐시하는 래퍼를 만듭니다"""
    # 구현하세요
    pass
```


## 8장 요약: 프레임워크 없는 아키텍처

이번 장에서는 함수형 프로그래밍의 원칙들이 어떻게 **견고한 시스템 아키텍처**의 기반이 되는지 확인했습니다.

1.  **의존성 주입 (Dependency Injection)**: 복잡한 프레임워크 대신 **클로저(Closure)**를 사용하여 의존성을 주입하고, 테스트 용이성을 확보했습니다.
2.  **미들웨어 (Middleware)**: **함수 합성(Composition)**을 통해 로깅, 인증, 에러 처리 등 횡단 관심사를 우아하게 파이프라인으로 연결했습니다.
3.  **트랜잭션 (Transaction)**: **Result Monad**와 결합하여 실패 시 자동 롤백되는 원자적(Atomic) 연산을 구현했습니다.
4.  **컨텍스트 관리**: `ContextVars`를 통해 실행 문맥을 안전하게 전파하되, 불변성 원칙을 지켜야 함을 배웠습니다.

### 1장 → 8장까지의 여정: 이론에서 실전으로

| 장 | 이론적 개념 | 실전 아키텍처 적용 |
|----|-----------|-------------------|
| **1장** | 순수 함수, 합성 | 미들웨어 파이프라인 |
| **1장** | 클로저, 고차 함수 | 함수형 의존성 주입 |
| **4장** | Monad (flatMap) | 트랜잭션 작업 체이닝 |
| **5장** | Result, Railway | 트랜잭션 성공/실패 처리 |
| **6장** | Applicative | 병렬 비즈니스 로직 실행 |

함수형 프로그래밍은 단순히 코딩 스타일이 아닙니다. **복잡한 시스템을 합성 가능한 작은 부품들로 나누고, 안전하게 조립하는 아키텍처 원칙**입니다.

### 다음 9장 예고: 타입 시스템과 함수형 프로그래밍

다음 장에서는 **타입 시스템(Type System)**을 다룹니다.
파이썬의 타입 힌팅, 제네릭(Generic), 프로토콜(Protocol)을 활용하여, 우리가 만든 함수형 추상화를 **컴파일 타임**에 검증하고 더 안전하게 만드는 방법을 배웁니다.
타입은 단순한 문서화가 아닙니다. 프로그램의 정확성을 보장하는 **수학적 증명**입니다.

```python
# 9장 맛보기: 제네릭과 프로토콜을 활용한 타입 안전성
class Monad[T](Protocol):
    def flat_map[U](self, func: Callable[[T], 'Monad[U]']) -> 'Monad[U]': ...
```
