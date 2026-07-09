---
title: "구조체"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "구조체"
---

# 1.4. Structures

The first step in writing a program is usually to identify the problem domain's concepts, and then find suitable representations for them in code.
Sometimes, a domain concept is a collection of other, simpler, concepts.
In that case, it can be convenient to group these simpler components together into a single “package”, which can then be given a meaningful name.
In Lean, this is done using *structures*, which are analogous to `struct`s in C or Rust and `record`s in C#.

프로그램을 작성하는 첫 번째 단계는 일반적으로 문제 영역의 개념을 식별한 다음, 코드에서 그들에 대한 적절한 표현을 찾는 것입니다.
때때로 영역 개념은 다른, 더 간단한 개념들의 모음입니다.
이 경우, 이러한 더 간단한 구성 요소를 단일 “패키지”로 그룹화하는 것이 편리할 수 있으며, 그러면 의미 있는 이름을 부여할 수 있습니다.
Lean에서 이는 C 또는 Rust의 `struct` 및 C#의 `record`와 유사한 *구조체(structures)*를 사용하여 수행됩니다.

Defining a structure introduces a completely new type to Lean that can't be reduced to any other type.
This is useful because multiple structures might represent different concepts that nonetheless contain the same data.
For instance, a point might be represented using either Cartesian or polar coordinates, each being a pair of floating-point numbers.
Defining separate structures prevents API clients from confusing one for another.

구조체를 정의하면 Lean에 다른 타입으로 축소될 수 없는 완전히 새로운 타입이 도입됩니다.
이는 여러 구조체가 동일한 데이터를 포함하지만 서로 다른 개념을 나타낼 수 있기 때문에 유용합니다.
예를 들어, 점은 데카르트 또는 극좌표를 사용하여 표현될 수 있으며, 각각은 부동 소수점 수의 쌍입니다.
별도의 구조체를 정의하면 API 클라이언트가 하나를 다른 것과 혼동하지 않도록 방지합니다.

Lean's floating-point number type is called `Float`, and floating-point numbers are written in the usual notation.

```lean
#check 1.2
```

```
1.2 : Float
```

```lean
#check -454.2123215
```

```
-454.2123215 : Float
```

```lean
#check 0.0
```

```
0.0 : Float
```

When floating point numbers are written with the decimal point, Lean will infer the type `Float`. If they are written without it, then a type annotation may be necessary.

```lean
#check 0
```

```
0 : Nat
```

```lean
#check (0 : Float)
```

```
0 : Float
```

Lean의 부동 소수점 수 타입은 `Float`이라고 하며, 부동 소수점 수는 일반적인 표기법으로 작성됩니다.

부동 소수점 수가 소수점과 함께 작성되면, Lean은 타입 `Float`을 추론합니다. 소수점 없이 작성되면, 타입 주석이 필요할 수 있습니다.

A Cartesian point is a structure with two `Float` fields, called `x` and `y`.
This is declared using the `structure` keyword.

```lean
structure Point where
  x : Float
  y : Float
```

After this declaration, `Point` is a new structure type.
The typical way to create a value of a structure type is to provide values for all of its fields inside of curly braces.
The origin of a Cartesian plane is where `x` and `y` are both zero:

```lean
def origin : Point := { x := 0.0, y := 0.0 }
```

The result of `#eval origin` looks very much like the definition of `origin`.

```
{ x := 0.000000, y := 0.000000 }
```

Because structures exist to “bundle up” a collection of data, naming it and treating it as a single unit, it is also important to be able to extract the individual fields of a structure.
This is done using dot notation, as in C, Python, Rust, or JavaScript.

```lean
#eval origin.x
```

```
0.000000
```

```lean
#eval origin.y
```

데카르트 점은 `x`와 `y`라는 두 개의 `Float` 필드를 가진 구조체입니다.
이는 `structure` 키워드를 사용하여 선언됩니다.

이 선언 후, `Point`는 새로운 구조체 타입입니다.
구조체 타입의 값을 생성하는 전형적인 방법은 중괄호 안에 모든 필드에 대한 값을 제공하는 것입니다.
데카르트 평면의 원점은 `x`과 `y`가 모두 0인 곳입니다.

`#eval origin`의 결과는 `origin`의 정의와 매우 유사해 보입니다.

구조체가 데이터 모음을 “묶어주고”, 이름을 지정하고 단일 단위로 취급하기 위해 존재하므로, 구조체의 개별 필드를 추출할 수 있어야 합니다.
이는 C, Python, Rust, JavaScript에서와 같이 점 표기법을 사용하여 수행됩니다.

This can be used to define functions that take structures as arguments.
For instance, addition of points is performed by adding the underlying coordinate values.
It should be the case that

```lean
#eval addPoints { x := 1.5, y := 32 } { x := -8, y := 0.2 }
```

yields

```
{ x := -6.500000, y := 32.200000 }
```

The function itself takes two `Point`s as arguments, called `p1` and `p2`.
The resulting point is based on the `x` and `y` fields of both `p1` and `p2`:

```lean
def addPoints (p1 : Point) (p2 : Point) : Point :=
  { x := p1.x + p2.x, y := p1.y + p2.y }
```

Similarly, the distance between two points, which is the square root of the sum of the squares of the differences in their `x` and `y` components, can be written:

```lean
def distance (p1 : Point) (p2 : Point) : Float :=
  Float.sqrt (((p2.x - p1.x) ^ 2.0) + ((p2.y - p1.y) ^ 2.0))
```

For example, the distance between `(1, 2)` and `(5, -1)` is `5`:

```lean
#eval distance { x := 1.0, y := 2.0 } { x := 5.0, y := -1.0 }
```

```
5.000000
```

이는 구조체를 인수로 가지는 함수를 정의하는 데 사용될 수 있습니다.
예를 들어, 점의 덧셈은 기본 좌표 값을 더하여 수행됩니다.
다음이 참이어야 합니다.

함수 자체는 `p1`과 `p2`라고 불리는 두 개의 `Point`를 인수로 받습니다.
결과 점은 `p1`과 `p2` 모두의 `x`과 `y` 필드를 기반으로 합니다.

마찬가지로, 두 점 사이의 거리는 `x`과 `y` 성분의 차이 제곱의 합의 제곱근입니다.

예를 들어, `(1, 2)`와 `(5, -1)` 사이의 거리는 `5`입니다.

Multiple structures may have fields with the same names.
A three-dimensional point datatype may share the fields `x` and `y`, and be instantiated with the same field names:

```lean
structure Point3D where
  x : Float
  y : Float
  z : Float
```

```lean
def origin3D : Point3D := { x := 0.0, y := 0.0, z := 0.0 }
```

This means that the structure's expected type must be known in order to use the curly-brace syntax.
If the type is not known, Lean will not be able to instantiate the structure.
For example,

```lean
#check { x := 0.0, y := 0.0 }
```

leads to the error

```
invalid {...} notation, expected type is not known
```

As usual, the situation can be remedied by providing a type annotation.

```lean
#check ({ x := 0.0, y := 0.0 } : Point)
```

```
{ x := 0.0, y := 0.0 } : Point
```

To make programs more concise, Lean also allows the structure type annotation inside the curly braces.

```lean
#check { x := 0.0, y := 0.0 : Point}
```

여러 구조체는 같은 이름의 필드를 가질 수 있습니다.
3차원 점 데이터타입은 `x`과 `y` 필드를 공유할 수 있고, 같은 필드 이름으로 인스턴스화될 수 있습니다.

이는 중괄호 구문을 사용하기 위해 구조체의 예상 타입을 알아야 한다는 의미입니다.
타입을 모르면, Lean은 구조체를 인스턴스화할 수 없습니다.
위 코드는 오류를 초래합니다.

일반적으로, 상황은 타입 주석을 제공하여 해결될 수 있습니다.

프로그램을 더 간결하게 만들기 위해, Lean은 중괄호 안에 구조체 타입 주석을 허용합니다.

## 1.4.1. Updating Structures

Imagine a function `zeroX` that replaces the `x` field of a `Point` with `0`.
In most programming language communities, this sentence would mean that the memory location pointed to by `x` was to be overwritten with a new value.
However, Lean is a functional programming language.
In functional programming communities, what is almost always meant by this kind of statement is that a fresh `Point` is allocated with the `x` field pointing to the new value, and all other fields pointing to the original values from the input.
One way to write `zeroX` is to follow this description literally, filling out the new value for `x` and manually transferring `y`:

```lean
def zeroX (p : Point) : Point :=
  { x := 0, y := p.y }
```

This style of programming has drawbacks, however.
First off, if a new field is added to a structure, then every site that updates any field at all must be updated, causing maintenance difficulties.
Secondly, if the structure contains multiple fields with the same type, then there is a real risk of copy-paste coding leading to field contents being duplicated or switched.
Finally, the program becomes long and bureaucratic.

Lean provides a convenient syntax for replacing some fields in a structure while leaving the others alone.
This is done by using the `with` keyword in a structure initialization.
The source of unchanged fields occurs before the `with`, and the new fields occur after.
For example, `zeroX` can be written with only the new `x` value:

```lean
def zeroX (p : Point) : Point :=
  { p with x := 0 }
```

Remember that this structure update syntax does not modify existing values—it creates new values that share some fields with old values.
Given the point `fourAndThree`:

```lean
def fourAndThree : Point :=
  { x := 4.3, y := 3.4 }
```

evaluating it, then evaluating an update of it using `zeroX`, then evaluating it again yields the original value:

```lean
#eval fourAndThree
```

```
{ x := 4.300000, y := 3.400000 }
```

```lean
#eval zeroX fourAndThree
```

```
{ x := 0.000000, y := 3.400000 }
```

```lean
#eval fourAndThree
```

One consequence of the fact that structure updates do not modify the original structure is that it becomes easier to reason about cases where the new value is computed from the old one.
All references to the old structure continue to refer to the same field values in all of the new values provided.

`Point`의 `x` 필드를 `0`으로 대체하는 함수 `zeroX`를 상상해 보세요.
대부분의 프로그래밍 언어 커뮤니티에서, 이 문장은 `x`가 가리키는 메모리 위치가 새 값으로 덮어씌워진다는 의미입니다.
그러나 Lean은 함수형 프로그래밍 언어입니다.
함수형 프로그래밍 커뮤니티에서, 이러한 종류의 명령문으로 거의 항상 의도되는 것은 `x` 필드가 새 값을 가리키고, 다른 모든 필드는 입력의 원본 값을 가리키는 새로운 `Point`가 할당된다는 것입니다.
`zeroX`를 작성하는 한 가지 방법은 이 설명을 문자 그대로 따르는 것이며, `x`의 새 값을 채우고 수동으로 `y`를 전송합니다.

그러나 이 프로그래밍 스타일에는 단점이 있습니다.
첫째, 새 필드가 구조체에 추가되면, 어떤 필드든 업데이트하는 모든 사이트를 업데이트해야 하므로 유지 관리 어려움을 초래합니다.
둘째, 구조체에 같은 타입의 여러 필드가 포함되면, 복사-붙여넣기 코딩으로 인해 필드 내용이 복제되거나 전환될 실질적인 위험이 있습니다.
마지막으로, 프로그램은 길고 관료적이 됩니다.

Lean은 구조체의 일부 필드를 대체하면서 나머지를 그대로 두는 편리한 구문을 제공합니다.
이는 구조체 초기화에서 `with` 키워드를 사용하여 수행됩니다.
변경되지 않은 필드의 원본은 `with` 앞에 나타나고, 새로운 필드는 뒤에 나타납니다.
예를 들어, `zeroX`는 새로운 `x` 값만으로 작성될 수 있습니다.

이 구조체 업데이트 구문은 기존 값을 수정하지 않습니다. 대신 기존 값과 일부 필드를 공유하는 새 값을 생성합니다.
점 `fourAndThree`가 주어지면.

그것을 평가한 다음, `zeroX`를 사용하여 그것의 업데이트를 평가한 다음, 다시 평가하면 원본 값을 산출합니다.

구조체 업데이트가 원본 구조체를 수정하지 않는다는 사실의 결과는 새 값이 이전 값에서 계산되는 경우를 추론하기가 더 쉬워진다는 것입니다.
이전 구조체에 대한 모든 참조는 제공된 모든 새 값에서 동일한 필드 값을 계속 참조합니다.

## 1.4.2. Behind the Scenes

Every structure has a *constructor*.
Here, the term “constructor” may be a source of confusion.
Unlike constructors in languages such as Java or Python, constructors in Lean are not arbitrary code to be run when a datatype is initialized.
Instead, constructors simply gather the data to be stored in the newly-allocated data structure.
It is not possible to provide a custom constructor that pre-processes data or rejects invalid arguments.
This is really a case of the word “constructor” having different, but related, meanings in the two contexts.

By default, the constructor for a structure named `S` is named `S.mk`.
Here, `S` is a namespace qualifier, and `mk` is the name of the constructor itself.
Instead of using curly-brace initialization syntax, the constructor can also be applied directly.

```lean
#check Point.mk 1.5 2.8
```

However, this is not generally considered to be good Lean style, and Lean even returns its feedback using the standard structure initializer syntax.

```
{ x := 1.5, y := 2.8 } : Point
```

Constructors have function types, which means they can be used anywhere that a function is expected.
For instance, `Point.mk` is a function that accepts two `Float`s (respectively `x` and `y`) and returns a new `Point`.

```lean
#check (Point.mk)
```

```
Point.mk : Float → Float → Point
```

모든 구조체는 *생성자(constructor)*를 가지고 있습니다.
여기서 “생성자”라는 용어는 혼동의 원인이 될 수 있습니다.
Java 또는 Python 같은 언어의 생성자와 달리, Lean의 생성자는 데이터타입이 초기화될 때 실행될 임의의 코드가 아닙니다.
대신 생성자는 새로 할당된 데이터 구조에 저장될 데이터를 단순히 수집합니다.
데이터를 전처리하거나 유효하지 않은 인수를 거부하는 사용자 정의 생성자를 제공하는 것은 불가능합니다.
이는 “생성자”라는 단어가 두 가지 컨텍스트에서 다르지만 관련된 의미를 가지는 경우입니다.

기본적으로, `S`라는 구조체의 생성자는 `S.mk`라고 이름이 지어집니다.
여기서 `S`는 네임스페이스 한정자이고, `mk`는 생성자 자체의 이름입니다.
중괄호 초기화 구문을 사용하는 대신, 생성자를 직접 적용할 수도 있습니다.

그러나 이는 일반적으로 좋은 Lean 스타일로 간주되지 않으며, Lean은 표준 구조체 이니셜라이저 구문을 사용하여 피드백을 반환합니다.

생성자는 함수 타입을 가지고 있으므로, 함수가 예상되는 곳에서 사용될 수 있습니다.
예를 들어, `Point.mk`는 두 개의 `Float`(각각 `x`과 `y`)를 받고 새로운 `Point`를 반환하는 함수입니다.

To override a structure's constructor name, write it with two colons at the beginning.
For instance, to use `Point.point` instead of `Point.mk`, write:

```lean
structure Point where
  point ::
  x : Float
  y : Float
```

In addition to the constructor, an accessor function is defined for each field of a structure.
These have the same name as the field, in the structure's namespace.
For `Point`, accessor functions `Point.x` and `Point.y` are generated.

```lean
#check (Point.x)
```

```
Point.x : Point → Float
```

```lean
#check (Point.y)
```

```
Point.y : Point → Float
```

In fact, just as the curly-braced structure construction syntax is converted to a call to the structure's constructor behind the scenes, the syntax `x` in the prior definition of `addPoints` is converted into a call to the `x` accessor.
That is, `#eval origin.x` and `#eval Point.x origin` both yield

```
0.000000
```

Accessor dot notation is usable with more than just structure fields.
It can also be used for functions that take any number of arguments.
More generally, accessor notation has the form `TARGET.f ARG1 ARG2 ...`.
If `TARGET` has type `T`, the function named `T.f` is called.
`TARGET` becomes its leftmost argument of type `T`, which is often but not always the first one, and `ARG1 ARG2 ...` are provided in order as the remaining arguments.
For instance, `String.append` can be invoked from a string with accessor notation, even though `String` is not a structure with an `append` field.

```lean
#eval "one string".append " and another"
```

```
"one string and another"
```

In that example, `TARGET` represents `"one string"` and `ARG1` represents `" and another"`.

구조체의 생성자 이름을 재정의하려면, 시작할 때 두 개의 콜론으로 작성하세요.
예를 들어, `Point.mk` 대신 `Point.point`를 사용하려면, 다음과 같이 작성하세요.

생성자 외에도, 구조체의 각 필드에 대해 접근자 함수가 정의됩니다.
이들은 필드와 같은 이름을 가지며, 구조체의 네임스페이스에 있습니다.
`Point`의 경우, 접근자 함수 `Point.x`와 `Point.y`가 생성됩니다.

실제로, 중괄호 구조체 생성 구문이 뒤에서 구조체의 생성자에 대한 호출로 변환되는 것처럼, `addPoints`의 이전 정의의 구문 `x`도 `x` 접근자에 대한 호출로 변환됩니다.
즉, `#eval origin.x`와 `#eval Point.x origin` 모두 다음을 산출합니다.

접근자 점 표기법은 구조체 필드뿐만 아니라 사용 가능합니다.
임의의 수의 인수를 가지는 함수에도 사용될 수 있습니다.
더 일반적으로, 접근자 표기법은 `TARGET.f ARG1 ARG2 ...` 형태를 가집니다.
`TARGET`이 타입 `T`를 가지면, `T.f`라는 이름의 함수가 호출됩니다.
`TARGET`은 타입 `T`의 가장 왼쪽 인수가 되며, 종종 첫 번째이지만 항상 그런 것은 아니고, `ARG1 ARG2 ...`는 나머지 인수로 순서대로 제공됩니다.
예를 들어, `String.append`는 `String`이 `append` 필드를 가진 구조체가 아니지만, 접근자 표기법을 사용하여 문자열에서 호출될 수 있습니다.

이 예제에서, `TARGET`은 `"one string"`을 나타내고 `ARG1`은 `" and another"`를 나타냅니다.

The function `Point.modifyBoth` (that is, `modifyBoth` defined in the `Point` namespace) applies a function to both fields in a `Point`:

```lean
def Point.modifyBoth (f : Float → Float) (p : Point) : Point :=
  { x := f p.x, y := f p.y }
```

Even though the `Point` argument comes after the function argument, it can be used with dot notation as well:

```lean
#eval fourAndThree.modifyBoth Float.floor
```

```
{ x := 4.000000, y := 3.000000 }
```

In this case, `TARGET` represents `fourAndThree`, while `ARG1` is `Float.floor`.
This is because the target of the accessor notation is used as the first argument in which the type matches, not necessarily the first argument.

함수 `Point.modifyBoth`(즉, `Point` 네임스페이스에 정의된 `modifyBoth`)는 `Point`의 두 필드에 함수를 적용합니다.

`Point` 인수가 함수 인수 뒤에 오지만, 점 표기법과도 함께 사용할 수 있습니다.

이 경우, `TARGET`은 `fourAndThree`를 나타내고, `ARG1`은 `Float.floor`입니다.
이는 접근자 표기법의 대상이 반드시 첫 번째 인수가 아니라 타입이 일치하는 첫 번째 인수로 사용되기 때문입니다.

## 1.4.3. Exercises

* Define a structure named `RectangularPrism` that contains the height, width, and depth of a rectangular prism, each as a `Float`.
* Define a function named `volume : RectangularPrism → Float` that computes the volume of a rectangular prism.
* Define a structure named `Segment` that represents a line segment by its endpoints, and define a function `length : Segment → Float` that computes the length of a line segment. `Segment` should have at most two fields.
* Which names are introduced by the declaration of `RectangularPrism`?
* Which names are introduced by the following declarations of `Hamster` and `Book`? What are their types?

  ```lean
  structure Hamster where
    name : String
    fluffy : Bool
  ```

  ```lean
  structure Book where
    makeBook ::
    title : String
    author : String
    price : Float
  ```

## 1.4.3. 연습문제

* `RectangularPrism`이라는 구조체를 정의하세요. 이 구조체는 직육면체의 높이, 너비, 깊이를 포함하며, 각각 `Float`입니다.
* `volume : RectangularPrism → Float`라는 함수를 정의하세요. 이 함수는 직육면체의 부피를 계산합니다.
* `Segment`라는 구조체를 정의하세요. 이 구조체는 끝점으로 선분을 나타내며, `length : Segment → Float` 함수를 정의하여 선분의 길이를 계산합니다. `Segment`는 최대 두 개의 필드를 가져야 합니다.
* `RectangularPrism` 선언으로 도입되는 이름들은 무엇입니까?
* 다음 `Hamster`와 `Book` 선언으로 도입되는 이름들은 무엇입니까? 각각의 타입은 무엇입니까?

  ```lean
  structure Hamster where
    name : String
    fluffy : Bool
  ```

  ```lean
  structure Book where
    makeBook ::
    title : String
    author : String
    price : Float
  ```
