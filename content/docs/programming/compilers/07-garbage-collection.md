---
title: "7. 가비지 컬렉션: Mark-Sweep과 Copying"
date: 2026-07-14T00:00:00+09:00
draft: false
tags: ["compilers", "mit-6035", "garbage-collection", "mark-sweep", "copying-gc", "runtime"]
categories: ["programming"]
description: "활성화 레코드로는 회수할 수 없는 힙 객체를 언제 어떻게 되찾을지, 도달 가능성 개념과 mark-sweep·copying GC의 동작 원리, 그리고 두 방식의 트레이드오프를 정리합니다."
---

[6편](06-code-generation-register-machine/)에서 활성화 레코드가 함수 반환과 함께 자동으로 정리된다고 했습니다. 하지만 MiniLang에 만약 객체를 동적으로 만드는 기능(예: 리스트, 클로저)이 있다면, 이 객체들은 함수가 반환된 뒤에도 계속 살아있어야 할 수 있습니다 — 활성화 레코드처럼 스택에서 자동으로 사라지면 안 됩니다. 이런 객체가 저장되는 메모리 영역이 **힙(Heap)**이고, 이 글은 힙에 있는 객체 중 더 이상 쓰이지 않는 것을 자동으로 찾아 회수하는 **가비지 컬렉션(Garbage Collection, GC)**을 다룹니다.

---

## 1. 언제 객체를 회수해도 안전한가: 도달 가능성

객체 하나를 회수해도 안전하려면, 그 객체를 앞으로 프로그램이 **절대 참조할 수 없다**는 게 보장되어야 합니다. 이걸 판단하는 표준 기준이 **도달 가능성(Reachability)**입니다 — 프로그램이 지금 직접 접근할 수 있는 지점들(**루트, Root** — 레지스터, [6편](06-code-generation-register-machine/#5-함수-호출마다-필요한-데이터-활성화-레코드)에서 다룬 활성화 레코드의 지역 변수들)에서 출발해, 포인터를 따라가며 도달할 수 있는 모든 객체는 **살아있고(live)**, 도달할 수 없는 객체는 **가비지(garbage)**입니다.

```
루트(스택의 지역 변수, 레지스터)
   │
   ▼
[객체 A] ──▶ [객체 B]
                │
                ▼
             [객체 C]

[객체 D]   ← 어느 루트에서도 도달할 수 없음 → 가비지
```

객체 D는 어떤 변수도 더 이상 가리키고 있지 않으므로, 이 객체가 차지한 메모리는 안전하게 회수해 다른 객체를 위해 재사용할 수 있습니다. GC의 모든 알고리즘은 결국 이 "루트에서 도달 가능한 객체"를 찾아내는 방법과, 도달 불가능한 객체의 메모리를 회수하는 방법을 어떻게 조합하느냐의 차이입니다.

---

## 2. Mark-Sweep: 살아있는 것에 표시하고, 나머지를 쓸어버린다

가장 직접적인 방법이 **Mark-Sweep**입니다. 이름 그대로 두 단계로 이루어집니다.

**Mark 단계**: 루트에서 시작해 포인터를 따라가며 도달하는 모든 객체에 "살아있음" 표시를 남깁니다.

```python
def mark(obj):
    if obj is None or obj.marked:
        return
    obj.marked = True
    for child in obj.pointers_to_other_objects():
        mark(child)

def mark_phase(roots):
    for root in roots:
        mark(root)
```

이 재귀 구조는 [4편](04-semantic-analysis/#2-첫-번째-질문-이-이름은-어디서-왔는가-스코프와-심볼-테이블)의 스코프 탐색이나 [5편](05-intermediate-representation-stack-machine/)의 AST 순회와 같은 발상입니다 — 그래프(여기서는 객체 참조 그래프)를 따라가며 도달 가능한 노드를 전부 방문하는 탐색입니다. `obj.marked` 확인이 없으면 객체 A와 B가 서로를 가리키는 순환 참조에서 무한 루프에 빠지므로, 이 체크가 종료를 보장하는 핵심입니다.

**Sweep 단계**: 힙 전체를 순서대로 훑으며, 표시(mark)가 안 된 객체를 전부 회수합니다.

```python
def sweep_phase(heap):
    for obj in heap.all_objects():
        if not obj.marked:
            heap.free(obj)         # 가비지였으므로 회수
        else:
            obj.marked = False     # 다음 GC 사이클을 위해 표시 초기화
```

Mark-Sweep의 장점은 객체를 옮기지 않는다는 점입니다 — 회수된 자리는 빈 공간으로 남고, 살아있는 객체는 원래 있던 주소에 그대로 남습니다. 단점은 회수된 빈 공간들이 힙 여기저기 흩어져(**단편화, Fragmentation**) 남는다는 것입니다 — 나중에 큰 객체를 새로 만들려 할 때, 전체 빈 공간의 합은 충분해도 그걸 담을 만큼 **연속된** 빈 공간이 없을 수 있습니다.

---

## 3. Copying GC: 살아있는 것만 옮겨 담아 단편화를 없앤다

**Copying GC**는 이 단편화 문제를, 살아있는 객체를 전부 새로운 연속된 공간으로 옮겨버리는 방식으로 해결합니다. 힙을 두 절반(**From-space**, **To-space**)으로 나누고, 항상 한쪽만 사용합니다.

```
GC 시작 전 (From-space만 사용 중):
From-space: [A][B][가비지][C][가비지][D]
To-space:   (비어있음)

GC 실행: 루트에서 도달 가능한 A, B, C를 To-space로 순서대로 복사
From-space: [A][B][가비지][C][가비지][D]   ← 이제 통째로 버림
To-space:   [A][B][C]                       ← 이걸 새 From-space로 삼음
```

이 알고리즘의 핵심은 **Cheney's Algorithm**이라 불리는, 재귀 호출 없이 큐처럼 순회하는 복사 절차입니다.

```python
def copying_gc(roots, from_space, to_space):
    scan = free = to_space.start
    for i, root in enumerate(roots):
        roots[i] = copy(root, to_space, free)   # 루트가 가리키는 객체를 복사하고 포인터 갱신

    while scan < free:                # 이미 복사된 객체들을 훑으며, 그 객체가 가리키는 것도 복사
        obj = to_space.object_at(scan)
        for i, child in enumerate(obj.pointers):
            obj.pointers[i] = copy(child, to_space, free)
        scan += obj.size

def copy(obj, to_space, free):
    if obj.forwarding_pointer is not None:
        return obj.forwarding_pointer            # 이미 복사됐다면 새 위치를 그대로 반환 (중복 복사 방지)
    new_addr = to_space.allocate_at(free, obj)
    obj.forwarding_pointer = new_addr             # "이 객체는 이미 여기로 옮겨졌다"는 표시
    return new_addr
```

`forwarding_pointer`가 하는 역할이 2절의 `marked` 플래그와 같은 이유로 존재합니다 — 객체 A와 B가 서로를 가리키는 순환 참조가 있을 때, A를 복사하다가 B를 복사하려는데 B가 이미 복사되었다면 다시 복사하는 대신 그 새 위치를 그대로 재사용해야 하기 때문입니다.

Copying GC의 장점은 복사가 끝나면 살아있는 객체들이 To-space에 **빈틈없이 연속으로** 배치된다는 것입니다 — 단편화가 원천적으로 사라집니다. 단점은 힙의 절반을 항상 비워둬야 하므로(사용 가능한 메모리가 실질적으로 반으로 줄어듦), 그리고 살아있는 객체가 많을수록 복사 비용 자체가 크다는 점입니다.

이 "힙의 절반을 낭비한다"는 단점은 실제로는 OS의 **가상 메모리(Virtual Memory)** 덕분에 상당 부분 완화됩니다 — From-space와 To-space가 실제 물리 메모리를 두 배로 점유해야 하는 게 아니라, 가상 주소 공간의 페이지 매핑(page mapping)만 바꿔치기하는 방식으로 구현할 수 있습니다. 복사가 끝난 뒤 From-space였던 물리 페이지를 곧바로 다른 용도로 반납(unmap)하면, 실제로 두 배의 물리 메모리를 항상 쥐고 있을 필요가 없습니다. Copying GC가 "이론적으로는 절반 낭비"라는 평판과 달리 실전 런타임(JVM 등)에서 널리 쓰이는 이유 중 하나가 이겁니다.

---

## 4. 두 방식의 트레이드오프, 그리고 세대별 GC라는 절충안

| | Mark-Sweep | Copying |
|---|---|---|
| 단편화 | 발생함 | 발생하지 않음 |
| 메모리 오버헤드 | 낮음 (전체 힙 사용) | 높음 (절반만 사용 가능) |
| 비용이 비례하는 대상 | 힙 전체 크기 (sweep이 전체를 훑음) | 살아있는 객체의 양 (죽은 객체는 그냥 버려짐) |

이 표의 마지막 줄이 실전에서 중요한 관찰로 이어집니다 — 대부분의 프로그램에서 **갓 만들어진 객체일수록 금방 죽고, 오래 살아남은 객체는 앞으로도 오래 산다**는 경향(약한 세대 가설, Weak Generational Hypothesis)이 있습니다. 이 경향을 이용해 힙을 "갓 만든 객체용(young generation)"과 "오래 살아남은 객체용(old generation)"으로 나누고, young generation은 Copying GC로 자주 작게 청소하고(어차피 대부분 죽어서 복사 비용이 적음), old generation은 Mark-Sweep으로 드물게 청소하는 방식이 **세대별 GC(Generational GC)**입니다 — 두 방식을 각자 유리한 상황에만 적용해 단점을 서로 상쇄합니다.

다만 세대를 나누는 순간 새로운 문제가 생깁니다 — young generation만 청소하려면 "old generation에 있는 객체가 young generation의 객체를 가리키고 있진 않은가"도 루트처럼 확인해야 합니다(그렇지 않으면 young generation의 그 객체를 가비지로 오판해 잘못 회수할 수 있습니다). 이 역참조를 매번 old generation 전체를 훑어서 찾으면 "young generation만 빠르게 청소한다"는 이점이 사라지므로, 실전 런타임은 **Write Barrier**라는 장치를 씁니다 — 포인터를 저장하는 명령어 실행 시마다(컴파일러가 그 지점에 자동으로 삽입한 소량의 추가 코드로) "old→young 참조가 새로 생겼다"는 사실을 **카드 테이블(Card Table)** 같은 별도 자료구조에 즉시 기록해둡니다. young generation을 청소할 때는 old generation 전체가 아니라 이 카드 테이블에 표시된 부분만 확인하면 되므로, 세대별 GC의 속도 이점이 실제로 유지됩니다.

---

## 5. GC와 활성화 레코드: 루트는 어디서 오는가

1절에서 "루트"를 "레지스터와 지역 변수"라고 뭉뚱그렸는데, [6편](06-code-generation-register-machine/#5-함수-호출마다-필요한-데이터-활성화-레코드)에서 다룬 활성화 레코드가 정확히 이 지역 변수들이 있는 곳입니다. GC가 정확하게 동작하려면, 스택에 쌓인 각 활성화 레코드에서 "이 슬롯은 힙 객체를 가리키는 포인터인지, 아니면 그냥 정수 값인지"를 구별할 수 있어야 합니다 — 정수 `42`를 포인터로 착각해 그 주소를 따라가면 안 되고, 반대로 진짜 포인터를 정수로 착각해 마킹을 빼먹으면 살아있는 객체를 잘못 회수하게 됩니다. 이 구별 정보(**스택 맵, Stack Map**)를 코드 생성 단계([6편](06-code-generation-register-machine/))가 미리 남겨둬야, 런타임에 GC가 각 활성화 레코드를 정확히 스캔할 수 있습니다 — 코드 생성과 가비지 컬렉션이 이렇게 서로의 전제 조건을 주고받습니다.

---

## 6. 정리

- 가비지 컬렉션은 **루트에서 도달 가능한지**를 기준으로 살아있는 객체와 회수 가능한 객체를 구분합니다.
- **Mark-Sweep**은 도달 가능한 객체에 표시를 남긴 뒤 나머지를 회수하며, 객체를 옮기지 않지만 힙에 단편화를 남깁니다.
- **Copying GC**는 살아있는 객체만 새 공간으로 옮겨 단편화를 없애지만, 힙의 절반만 항상 쓸 수 있다는 오버헤드를 감수합니다.
- **세대별 GC**는 "갓 만든 객체는 금방 죽는다"는 경향을 이용해 두 방식을 영역별로 나눠 적용하는 실전 절충안이며, old→young 참조를 놓치지 않기 위해 **Write Barrier**와 **카드 테이블**을 씁니다. Copying GC의 "절반 낭비" 단점도 실전에서는 OS의 가상 메모리 페이지 매핑으로 상당 부분 완화됩니다.
- GC가 정확히 동작하려면 [6편](06-code-generation-register-machine/)의 활성화 레코드에서 어느 슬롯이 포인터인지 알아야 하며, 이 정보는 코드 생성 단계가 미리 남겨야 합니다.

지금까지 편들이 "AST를 올바르게 실행되는 코드로 만드는" 데 집중했다면, 다음 편에서는 그 코드를 **더 빠르게** 만드는 최적화 — 지역 최적화와 데이터플로우 분석을 다룹니다.
