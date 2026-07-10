---
title: "10. 타입 클래스"
date: 2026-07-10T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "theorem-proving", "type-theory"]
categories: ["programming"]
description: "타입 클래스를 이용한 애드혹 다형성, 인스턴스 체이닝과 강제 변환(coercion)을 다룹니다."
---

Type classes were introduced as a principled way of enabling
ad-hoc polymorphism in functional programming languages. We first observe that it
would be easy to implement an ad-hoc polymorphic function (such as addition) if the
function simply took the type-specific implementation of addition as an argument
and then called that implementation on the remaining arguments. For example,
suppose we declare a structure in Lean to hold implementations of addition.

타입 클래스는 함수형 프로그래밍 언어에서 임시 다형성(ad-hoc polymorphism)을 가능하게 하는 체계적인 방법으로 도입되었습니다. 먼저 덧셈과 같은 임시 다형 함수를 구현하기 위해 타입별 덧셈 구현을 인자로 받고 그 구현을 나머지 인자에 대해 호출하면 쉽게 구현할 수 있다는 것을 관찰합니다. 예를 들어, Lean에서 덧셈의 구현을 보유하기 위한 구조를 선언한다고 가정해봅시다.

```
structure Add (α : Type) where
add : α → α → α
#check @Add.add
```

```
@Add.add : {α : Type} → Add α → α → α → α
```

In the above Lean code, the field `add` has type
`Add.add : {α : Type} → Add α → α → α → α`
where the curly braces around the type `α` mean that it is an implicit argument.
We could implement `double` by:

위의 Lean 코드에서 `add` 필드의 타입은 `Add.add : {α : Type} → Add α → α → α → α`입니다. 여기서 타입 `α` 주위의 중괄호는 암시적 인자임을 의미합니다. 우리는 `double`을 다음과 같이 구현할 수 있습니다:

```
def double (s : Add α) (x : α) : α :=
s.add x x
#eval double { add := Nat.add } 10
```

```
20
```

```
#eval double { add := Nat.mul } 10
```

```
100
```

```
#eval double { add := Int.add } 10
```

```
20
```

Note that you can double a natural number `n` by `double { add := Nat.add } n`.
Of course, it would be highly cumbersome for users to manually pass the
implementations around in this way.
Indeed, it would defeat most of the potential benefits of ad-hoc
polymorphism.

`double { add := Nat.add } n`으로 자연수 `n`을 두 배로 만들 수 있음을 주목하세요. 물론, 사용자가 이런 식으로 구현을 수동으로 전달하는 것은 매우 번거로울 것입니다. 실제로, 이 방식은 임시 다형성의 대부분의 잠재적 이점을 무효화할 것입니다.

The main idea behind type classes is to make arguments such as `Add α` implicit,
and to use a database of user-defined instances to synthesize the desired instances
automatically through a process known as typeclass resolution. In Lean, by changing
`structure` to `class` in the example above, the type of `Add.add` becomes:

타입 클래스의 주요 아이디어는 `Add α`와 같은 인자를 암시적으로 만들고, 타입 클래스 해석(typeclass resolution)이라는 과정을 통해 사용자 정의 인스턴스의 데이터베이스를 사용하여 원하는 인스턴스를 자동으로 생성하는 것입니다. Lean에서는 위의 예제에서 `structure`를 `class`로 변경하면 `Add.add`의 타입이 다음과 같이 됩니다:

```
class Add (α : Type) where
add : α → α → α
#check @Add.add
```

```
@Add.add : {α : Type} → [self : Add α] → α → α → α
```

where the square brackets indicate that the argument of type `Add α` is *instance implicit*,
i.e. that it should be synthesized using typeclass resolution. This version of
`add` is the Lean analogue of the Haskell term `add :: Add a => a -> a -> a`.
Similarly, we can register instances by:

여기서 대괄호는 `Add α` 타입의 인자가 *인스턴스 암시적*임을 나타냅니다. 즉, 타입 클래스 해석을 사용하여 생성되어야 합니다. 이 버전의 `add`는 Haskell 항 `add :: Add a => a -> a -> a`에 해당하는 Lean입니다. 마찬가지로 우리는 인스턴스를 등록할 수 있습니다:

```
instance : Add Nat where
add := Nat.add
instance : Add Int where
add := Int.add
instance : Add Float where
add := Float.add
```

Then for `n : Nat` and `m : Nat`, the term `Add.add n m` triggers typeclass resolution with
the goal of `Add Nat`, and typeclass resolution will synthesize the instance for `Nat` above.
We can now reimplement `double` using an instance implicit by:

그 다음 `n : Nat`과 `m : Nat`에 대해, 항 `Add.add n m`은 `Add Nat`의 목표를 가지고 타입 클래스 해석을 트리거하고, 타입 클래스 해석은 위의 `Nat`에 대한 인스턴스를 생성합니다. 이제 우리는 인스턴스 암시적을 사용하여 `double`을 다시 구현할 수 있습니다:

```
def double [Add α] (x : α) : α :=
Add.add x x
#check @double
```

```
@double : {α : Type} → [Add α] → α → α
```

```
#eval double 10
```

```
20
```

```
#eval double (10 : Int)
```

```
20
```

```
#eval double (7 : Float)
```

```
14.000000
```

```
#eval double (239.0 + 2)
```

```
482.000000
```

In general, instances may depend on other instances in complicated ways. For example,
you can declare an instance stating that if `α` has addition, then `Array α`
has addition:

일반적으로 인스턴스는 복잡한 방식으로 다른 인스턴스에 의존할 수 있습니다. 예를 들어, `α`가 덧셈을 가지면 `Array α`도 덧셈을 가진다는 것을 나타내는 인스턴스를 선언할 수 있습니다:

```
instance [Add α] : Add (Array α) where
add x y := Array.zipWith (· + ·) x y
#eval Add.add #[1, 2] #[3, 4]
```

```
#[4, 6]
```

```
#eval #[1, 2] + #[3, 4]
```

```
#[4, 6]
```

Note that `(· + ·)` is notation for `fun x y => x + y` in Lean.

The example above demonstrates how type classes are used to overload notation.
Now, we explore another application. We often need an arbitrary element of a given type.
Recall that types may not have any elements in Lean.
It often happens that we would like a definition to return an arbitrary element in a “corner case.”
For example, we may like the expression `head xs` to be of type `α` when `xs` is of type `List α`.
Similarly, many theorems hold under the additional assumption that a type is not empty.
For example, if `α` is a type, `∃ x : α, x = x` is true only if `α` is not empty.
The standard library defines a type class `Inhabited` to enable type class inference to infer a
“default” element of an inhabited type.
Let us start with the first step of the program above, declaring an appropriate class:

위의 예제는 타입 클래스가 어떻게 표기법을 오버로드하는 데 사용되는지 보여줍니다. 이제 다른 응용을 탐색해봅시다. 우리는 종종 주어진 타입의 임의 원소가 필요합니다. Lean에서 타입이 어떤 원소도 가지지 않을 수 있다는 것을 기억하세요. 정의가 “특수한 경우”에 임의 원소를 반환하기를 원하는 경우가 종종 있습니다. 예를 들어, `xs`가 `List α` 타입일 때 `head xs` 표현식이 `α` 타입이 되기를 원할 수 있습니다. 마찬가지로 많은 정리들이 타입이 공집합이 아니라는 추가 가정 하에서 성립합니다. 예를 들어, `α`가 타입이면 `∃ x : α, x = x`는 `α`가 공집합이 아닐 때만 참입니다. 표준 라이브러리는 타입 클래스 추론이 inhabited 타입(공집합이 아닌 타입)의 “기본” 원소를 추론하도록 하기 위해 `Inhabited` 타입 클래스를 정의합니다. 위의 프로그램의 첫 번째 단계부터 시작하여 적절한 클래스를 선언해봅시다:

```
class Inhabited (α : Type u) where
default : α
#check @Inhabited.default
```

```
@Inhabited.default : {α : Type u_1} → [self : Inhabited α] → α
```

Note `Inhabited.default` doesn't have any explicit arguments.

An element of the class `Inhabited α` is simply an expression of the form `Inhabited.mk x`, for some element `x : α`.
The projection `Inhabited.default` will allow us to “extract” such an element of `α` from an element of `Inhabited α`.
Now we populate the class with some instances:

`Inhabited α` 클래스의 원소는 단순히 어떤 원소 `x : α`에 대해 `Inhabited.mk x` 형태의 표현식입니다. 투영 `Inhabited.default`는 `Inhabited α`의 원소에서 `α`의 이러한 원소를 “추출”할 수 있게 해줍니다. 이제 이 클래스를 일부 인스턴스로 채워봅시다:

```
instance : Inhabited Bool where
default := true
instance : Inhabited Nat where
default := 0
instance : Inhabited Unit where
default := ()
instance : Inhabited Prop where
default := True
#eval (Inhabited.default : Nat)
```

```
0
```

```
#eval (Inhabited.default : Bool)
```

```
true
```

You can use the command `export` to create the alias `default` for `Inhabited.default`.

```
export Inhabited (default)
#eval (default : Nat)
```

```
0
```

```
#eval (default : Bool)
```

```
true
```

## 10.1. Chaining Instances

If that were the extent of type class inference, it would not be all that impressive;
it would be simply a mechanism of storing a list of instances for the elaborator to find in a lookup table.
What makes type class inference powerful is that one can *chain* instances. That is,
an instance declaration can in turn depend on an implicit instance of a type class.
This causes class inference to chain through instances recursively, backtracking when necessary, in a Prolog-like search.

만약 이것이 타입 클래스 추론의 전부라면 그다지 인상적이지 않을 것입니다. 단순히 엘래버레이터가 조회 테이블에서 찾을 수 있도록 인스턴스 목록을 저장하는 메커니즘일 뿐일 것입니다. 타입 클래스 추론을 강력하게 만드는 것은 인스턴스를 *연결*할 수 있다는 것입니다. 즉, 인스턴스 선언은 타입 클래스의 암시적 인스턴스에 의존할 수 있습니다. 따라서 타입 클래스 추론은 인스턴스를 재귀적으로 연결하며, 필요시 역추적하는 Prolog 유사 검색을 수행합니다.

For example, the following definition shows that if two types `α` and `β` are inhabited, then so is their product:

예를 들어, 다음 정의는 두 타입 `α`과 `β`가 inhabited이면(공집합이 아니면) 그들의 곱도 inhabited이라는 것을 보여줍니다:

```
instance [Inhabited α] [Inhabited β] : Inhabited (α × β) where
default := (default, default)
```

With this added to the earlier instance declarations, type class instance can infer, for example, a default element of `Nat × Bool`:

이를 이전의 인스턴스 선언에 추가하면, 타입 클래스 인스턴스는 예를 들어 `Nat × Bool`의 기본 원소를 추론할 수 있습니다:

```
instance [Inhabited α] [Inhabited β] : Inhabited (α × β) where
default := (default, default)
#eval (default : Nat × Bool)
```

```
(0, true)
```

Similarly, we can inhabit type function with suitable constant functions:

마찬가지로 우리는 적절한 상수 함수를 사용하여 함수 타입을 inhabited로 만들 수 있습니다:

```
instance [Inhabited β] : Inhabited (α → β) where
default := fun _ => default
```

As an exercise, try defining default instances for other types, such as `List` and `Sum` types.

연습으로 `List`과 `Sum` 타입과 같은 다른 타입들에 대해 기본 인스턴스를 정의해보세요.

The Lean standard library contains the definition `inferInstance`. It has type `{α : Sort u} → [i : α] → α`,
and is useful for triggering the type class resolution procedure when the expected type is an instance.

Lean 표준 라이브러리는 `inferInstance`의 정의를 포함합니다. 해당 함수는 `{α : Sort u} → [i : α] → α` 타입을 가지며, 예상 타입이 인스턴스일 때 타입 클래스 해석 절차를 트리거하는 데 유용합니다.

```
#check (inferInstance : Inhabited Nat)
```

```
inferInstance : Inhabited Nat
```

```
def foo : Inhabited (Nat × Nat) :=
inferInstance
theorem ex : foo.default = (default, default) :=
rfl
```

You can use the command `#print` to inspect how simple `inferInstance` is.

```
#print inferInstance
```

```
@[reducible] def inferInstance.{u} : {α : Sort u} → [i : α] → α :=
fun {α} [i : α] => i
```

## 10.2. ToString

The polymorphic method `toString` has type `{α : Type u} → [ToString α] → α → String`. You implement the instance
for your own types and use chaining to convert complex values into strings. Lean comes with `ToString` instances
for most builtin types.

다형 메서드 `toString`은 `{α : Type u} → [ToString α] → α → String` 타입을 가집니다. 당신은 자신의 타입에 대해 인스턴스를 구현하고 연결을 사용하여 복잡한 값을 문자열로 변환합니다. Lean은 대부분의 내장 타입에 대해 `ToString` 인스턴스를 제공합니다.

```
structure Person where
name : String
age : Nat
instance : ToString Person where
toString p := p.name ++ "@" ++ toString p.age
#eval toString { name := "Leo", age := 542 : Person }
```

```
"Leo@542"
```

```
#eval toString ({ name := "Daniel", age := 18 : Person }, "hello")
```

```
"(Daniel@18, hello)"
```

## 10.3. Numerals

Numerals are polymorphic in Lean. You can use a numeral (e.g., `2`) to denote an element of any type that implements
the type class `OfNat`.

숫자는 Lean에서 다형적입니다. `OfNat` 타입 클래스를 구현하는 모든 타입의 원소를 나타내기 위해 숫자(예: `2`)를 사용할 수 있습니다.

```
structure Rational where
num : Int
den : Nat
inv : den ≠ 0
instance : OfNat Rational n where
ofNat := { num := n, den := 1, inv := by decide }
instance : ToString Rational where
toString r := s!"{r.num}/{r.den}"
#eval (2 : Rational)
```

```
2/1
```

```
#check (2 : Rational)
```

```
2 : Rational
```

```
#check (2 : Nat)
```

```
2 : Nat
```

Lean elaborates the terms `(2 : Nat)` and `(2 : Rational)` as
`@OfNat.ofNat Nat 2 (@instOfNatNat 2)` and
`@OfNat.ofNat Rational 2 (@instOfNatRational 2)` respectively.
We say the numerals `2` occurring in the elaborated terms are *raw* natural numbers.
You can input the raw natural number `2` using the macro `nat_lit 2`.

Lean은 항 `(2 : Nat)`과 `(2 : Rational)`을 각각 `@OfNat.ofNat Nat 2 (@instOfNatNat 2)`과 `@OfNat.ofNat Rational 2 (@instOfNatRational 2)`로 엘래버레이트합니다. 엘래버레이트된 항에 나타나는 숫자 `2`를 *원시* 자연수라고 합니다. `nat_lit 2` 매크로를 사용하여 원시 자연수 `2`를 입력할 수 있습니다.

```
#check nat_lit 2
```

```
2 : Nat
```

Raw natural numbers are *not* polymorphic.

The `OfNat` instance is parametric on the numeral. So, you can define instances for particular numerals.
The second argument is often a variable as in the example above, or a *raw* natural number.

`OfNat` 인스턴스는 숫자에 대해 매개변수화되어 있습니다. 따라서 특정 숫자에 대해 인스턴스를 정의할 수 있습니다. 두 번째 인자는 위의 예제에서 처럼 변수이거나 *원시* 자연수입니다.

```
class Monoid (α : Type u) where
unit : α
op : α → α → α
instance [s : Monoid α] : OfNat α (nat_lit 1) where
ofNat := s.unit
def getUnit [Monoid α] : α :=
1
```

## 10.4. Output Parameters

By default, Lean only tries to synthesize an instance `Inhabited T` when the term `T` is known and does not
contain missing parts. The following command produces the error
`typeclass instance problem is stuck, it is often due to metavariables` because the type has a missing part (i.e., the `_`).

기본적으로 Lean은 항 `T`가 알려져 있고 누락된 부분이 없을 때만 인스턴스 `Inhabited T`를 생성하려고 합니다. 다음 명령은 타입이 누락된 부분을 가지고 있기 때문에(즉, `_`) `typeclass instance problem is stuck, it is often due to metavariables` 오류를 생성합니다.

```
/--
error: typeclass instance problem is stuck, it is often due to metavariables
  Inhabited (Nat × ?m.2)
-/
#guard_msgs (error) in
#eval (inferInstance : Inhabited (Nat × _))
```

You can view the parameter of the type class `Inhabited` as an *input* value for the type class synthesizer.
When a type class has multiple parameters, you can mark some of them as *output parameters*.
Lean will start type class synthesizer even when these parameters have missing parts.
In the following example, we use output parameters to define a *heterogeneous* polymorphic
multiplication.

타입 클래스 `Inhabited`의 매개변수를 타입 클래스 합성자의 *입력* 값으로 볼 수 있습니다. 타입 클래스가 여러 매개변수를 가질 때, 일부를 *출력 매개변수*로 표시할 수 있습니다. Lean은 이러한 매개변수가 누락된 부분을 가지고 있을 때도 타입 클래스 합성자를 시작합니다. 다음 예제에서 우리는 출력 매개변수를 사용하여 *이종* 다형 곱셈을 정의합니다.

```
class HMul (α : Type u) (β : Type v) (γ : outParam (Type w)) where
hMul : α → β → γ
export HMul (hMul)
instance : HMul Nat Nat Nat where
hMul := Nat.mul
instance : HMul Nat (Array Nat) (Array Nat) where
hMul a bs := bs.map (fun b => hMul a b)
#eval hMul 4 3
```

```
12
```

```
#eval hMul 4 #[2, 3, 4]
```

```
#[8, 12, 16]
```

The parameters `α` and `β` are considered input parameters and `γ` an output one.
Given an application `hMul a b`, after the types of `a` and `b` are known, the type class
synthesizer is invoked, and the resulting type is obtained from the output parameter `γ`.
In the example above, we defined two instances. The first one is the homogeneous
multiplication for natural numbers. The second is the scalar multiplication for arrays.
Note that you chain instances and generalize the second instance.

매개변수 `α`과 `β`는 입력 매개변수로 간주되고 `γ`는 출력 매개변수입니다. 응용 `hMul a b`가 주어졌을 때, `a`와 `b`의 타입이 알려진 후, 타입 클래스 합성자가 호출되고, 결과 타입은 출력 매개변수 `γ`에서 얻어집니다. 위의 예제에서 우리는 두 개의 인스턴스를 정의했습니다. 첫 번째는 자연수에 대한 동일 곱셈입니다. 두 번째는 배열에 대한 스칼라 곱셈입니다. 인스턴스를 연결하고 두 번째 인스턴스를 일반화할 수 있음을 주목하세요.

```
class HMul (α : Type u) (β : Type v) (γ : outParam (Type w)) where
hMul : α → β → γ
export HMul (hMul)
instance : HMul Nat Nat Nat where
hMul := Nat.mul
instance : HMul Int Int Int where
hMul := Int.mul
instance [HMul α β γ] : HMul α (Array β) (Array γ) where
hMul a bs := bs.map (fun b => hMul a b)
#eval hMul 4 3
```

```
12
```

```
#eval hMul 4 #[2, 3, 4]
```

```
#[8, 12, 16]
```

```
#eval hMul (-2) #[3, -1, 4]
```

```
#[-6, 2, -8]
```

```
#eval hMul 2 #[#[2, 3], #[0, 4]]
```

```
#[#[4, 6], #[0, 8]]
```

You can use our new scalar array multiplication instance on arrays of type `Array β`
with a scalar of type `α` whenever you have an instance `HMul α β γ`.
In the last `#eval`, note that the instance was used twice on an array of arrays.

인스턴스 `HMul α β γ`가 있을 때마다 타입 `α`의 스칼라를 가지고 `Array β` 타입의 배열에 대해 우리의 새로운 스칼라 배열 곱셈 인스턴스를 사용할 수 있습니다. 마지막 `#eval`에서 인스턴스가 배열 배열에서 두 번 사용되었음을 주목하세요.

Output parameters are ignored during instance synthesis. Even when instance synthesis occurs in a
context in which the values of output parameters are already determined, their values are ignored.
Once an instance is found using its input parameters, Lean ensures that the already-known values of
the output parameters match those which were found.

출력 매개변수는 인스턴스 합성 중에 무시됩니다. 인스턴스 합성이 출력 매개변수의 값이 이미 결정된 컨텍스트에서 발생하더라도 그들의 값은 무시됩니다. 입력 매개변수를 사용하여 인스턴스를 찾은 후, Lean은 출력 매개변수의 이미 알려진 값이 찾은 값과 일치하는지 확인합니다.

Lean also features *semi-output parameters*, which have some features of input parameters
and some features of output parameters. Like input parameters, semi-output parameters are considered
when selecting instances. Like output parameters, they can be used to instantiate unknown values.
However, they do not do so uniquely. Instance synthesis with semi-output parameters can be more difficult
to predict, because the order in which instances are considered can determine which is selected, but it is
also more flexible.

Lean은 또한 입력 매개변수의 일부 기능과 출력 매개변수의 일부 기능을 가진 *준-출력 매개변수*를 특징으로 합니다. 입력 매개변수처럼 준-출력 매개변수는 인스턴스를 선택할 때 고려됩니다. 출력 매개변수처럼 미지의 값을 구체화하는 데 사용할 수 있습니다. 그러나 그들은 고유하게 그렇게 하지 않습니다. 준-출력 매개변수를 사용한 인스턴스 합성은 인스턴스가 고려되는 순서가 어느 것이 선택되는지 결정할 수 있기 때문에 예측하기가 더 어려울 수 있지만 더 유연합니다.

## 10.5. Default Instances

In the class `HMul`, the parameters `α` and `β` are treated as input values.
Thus, type class synthesis only starts after these two types are known. This may often
be too restrictive.

클래스 `HMul`에서 매개변수 `α`과 `β`는 입력 값으로 취급됩니다. 따라서 타입 클래스 합성은 이 두 타입이 알려진 후에만 시작됩니다. 이는 종종 너무 제한적일 수 있습니다.

```
class HMul (α : Type u) (β : Type v) (γ : outParam (Type w)) where
hMul : α → β → γ
export HMul (hMul)
instance : HMul Int Int Int where
hMul := Int.mul
def xs : List Int := [1, 2, 3]
/--
error: typeclass instance problem is stuck
  HMul Int ?m.2 (?m.11 y)

Note: Lean will not try to resolve this typeclass instance problem because the second type argument to `HMul` is a metavariable. This argument must be fully determined before Lean will try to resolve the typeclass.

Hint: Adding type annotations and supplying implicit arguments to functions can give Lean more information for typeclass resolution. For example, if you have a variable `x` that you intend to be a `Nat`, but Lean reports it as having an unresolved type like `?m`, replacing `x` with `(x : Nat)` can get typeclass resolution un-stuck.
-/
#guard_msgs (error) in
#eval fun y => xs.map (fun x => hMul x y)
```

The instance `HMul` is not synthesized by Lean because the type of `y` has not been provided.
However, it is natural to assume that the type of `y` and `x` should be the same in
this kind of situation. We can achieve exactly that using *default instances*.

인스턴스 `HMul`은 `y`의 타입이 제공되지 않았기 때문에 Lean에 의해 생성되지 않습니다. 그러나 이런 상황에서 `y`의 타입과 `x`의 타입이 같아야 한다고 가정하는 것이 자연스럽습니다. 우리는 *기본 인스턴스*를 사용하여 정확히 그것을 달성할 수 있습니다.

```
class HMul (α : Type u) (β : Type v) (γ : outParam (Type w)) where
hMul : α → β → γ
export HMul (hMul)
@[default_instance]
instance : HMul Int Int Int where
hMul := Int.mul
def xs : List Int := [1, 2, 3]
#check fun y => xs.map (fun x => hMul x y)
```

```
fun y => List.map (fun x => hMul x y) xs : Int → List Int
```

By tagging the instance above with the attribute `[default_instance]`, we are instructing Lean
to use this instance on pending type class synthesis problems.
The actual Lean implementation defines homogeneous and heterogeneous classes for arithmetical operators.
Moreover, `a + b`, `a * b`, `a - b`, `a / b`, and `a % b` are notations for the heterogeneous versions.
The instance `OfNat Nat n` is the default instance (with priority 100) for the `OfNat` class. This is why the numeral
`2` has type `Nat` when the expected type is not known. You can define default instances with higher
priority to override the builtin ones.

위의 인스턴스를 속성 `[default_instance]`으로 태그하여 우리는 Lean에 대기 중인 타입 클래스 합성 문제에 이 인스턴스를 사용하도록 지시합니다. 실제 Lean 구현은 산술 연산자에 대한 동일 및 이종 클래스를 정의합니다. 또한 `a + b`, `a * b`, `a - b`, `a / b`, `a % b`는 이종 버전의 표기법입니다. 인스턴스 `OfNat Nat n`은 `OfNat` 클래스의 기본 인스턴스입니다(우선순위 100). 이것이 바로 예상 타입이 알려지지 않았을 때 숫자 `2`가 `Nat` 타입을 갖는 이유입니다. 기본 인스턴스보다 높은 우선순위로 정의하여 내장 인스턴스를 재정의할 수 있습니다.

```
structure Rational where
num : Int
den : Nat
inv : den ≠ 0
@[default_instance 200]
instance : OfNat Rational n where
ofNat := { num := n, den := 1, inv := by decide }
instance : ToString Rational where
toString r := s!"{r.num}/{r.den}"
#check 2
```

```
2 : Rational
```

Priorities are also useful to control the interaction between different default instances.
For example, suppose `xs` has type `List α`. When elaborating `xs.map (fun x => 2 * x)`, we want the homogeneous instance for multiplication
to have higher priority than the default instance for `OfNat α 2`. This is particularly important when we have implemented only the instance
`HMul α α α`, and did not implement `HMul Nat α α`.

우선순위는 또한 다른 기본 인스턴스 간의 상호 작용을 제어하는 데 유용합니다. 예를 들어, `xs`가 `List α` 타입을 가진다고 가정하세요. `xs.map (fun x => 2 * x)`를 엘래버레이트할 때, 우리는 곱셈의 동일 인스턴스가 `OfNat α 2`의 기본 인스턴스보다 높은 우선순위를 갖기를 원합니다. 이는 특히 인스턴스 `HMul α α α`만 구현했고 `HMul Nat α α`는 구현하지 않았을 때 중요합니다.

이제 우리는 표기법 `a * b`가 Lean에서 어떻게 정의되는지를 밝혀냅니다.

```
class OfNat (α : Type u) (n : Nat) where
ofNat : α
@[default_instance]
instance (n : Nat) : OfNat Nat n where
ofNat := n
class HMul (α : Type u) (β : Type v) (γ : outParam (Type w)) where
hMul : α → β → γ
class Mul (α : Type u) where
mul : α → α → α
@[default_instance 10]
instance [Mul α] : HMul α α α where
hMul a b := Mul.mul a b
infixl:70 " * " => HMul.hMul
```

The `Mul` class is convenient for types that only implement the homogeneous multiplication.

`Mul` 클래스는 동일 곱셈만 구현하는 타입에 편리합니다.

## 10.6. Local Instances

Type classes are implemented using attributes in Lean. Thus, you can
use the `local` modifier to indicate that they only have effect until
the current `section` or `namespace` is closed, or until the end
of the current file.

타입 클래스는 Lean에서 속성을 사용하여 구현됩니다. 따라서 `local` 수정자를 사용하여 현재 `section` 또는 `namespace`가 닫힐 때까지 또는 현재 파일의 끝까지만 효과가 있음을 나타낼 수 있습니다.

```
structure Point where
x : Nat
y : Nat
section
local instance : Add Point where
add a b := { x := a.x + b.x, y := a.y + b.y }
def double (p : Point) :=
p + p
end -- instance `Add Point` is not active anymore

/--
error: failed to synthesize
  HAdd Point Point ?m.5

Hint: Additional diagnostic information may be available using
the `set_option diagnostics true` command.
-/
#guard_msgs in
def triple (p : Point) :=
p + p + p
```

You can also temporarily disable an instance using the `attribute` command
until the current `section` or `namespace` is closed, or until the end
of the current file.

현재 `section` 또는 `namespace`가 닫힐 때까지 또는 현재 파일의 끝까지 `attribute` 명령을 사용하여 인스턴스를 임시로 비활성화할 수 있습니다.

```
structure Point where
x : Nat
y : Nat
instance addPoint : Add Point where
add a b := { x := a.x + b.x, y := a.y + b.y }
def double (p : Point) :=
p + p
attribute [-instance] addPoint
/--
error: failed to synthesize
  HAdd Point Point ?m.5

Hint: Additional diagnostic information may be available using
the `set_option diagnostics true` command.
-/
#guard_msgs in
def triple (p : Point) :=
p + p + p  -- Error: failed to synthesize instance
```

We recommend you only use this command to diagnose problems.

우리는 문제를 진단하기 위해서만 이 명령을 사용할 것을 권고합니다.

## 10.7. Scoped Instances

You can also declare scoped instances in namespaces. This kind of instance is
only active when you are inside of the namespace or open the namespace.

```
structure Point where
x : Nat
y : Nat
namespace Point
scoped instance : Add Point where
add a b := { x := a.x + b.x, y := a.y + b.y }
def double (p : Point) :=
p + p
end Point
-- instance `Add Point` is not active anymore

/--
error: failed to synthesize
  HAdd Point Point ?m.3

Hint: Additional diagnostic information may be available using
the `set_option diagnostics true` command.
-/
#guard_msgs (error) in
#check fun (p : Point) => p + p + p
```

```
fun p => sorry : (p : Point) → ?m.6 p
```

```
namespace Point
-- instance `Add Point` is active again
#check fun (p : Point) => p + p + p
```

```
fun p => p + p + p : Point → Point
```

```
end Point
open Point -- activates instance `Add Point`
#check fun (p : Point) => p + p + p
```

```
fun p => p + p + p : Point → Point
```

You can use the command `open scoped`` <namespace>` to activate scoped attributes but will not “open” the names from the namespace.

네임스페이스에서 범위 인스턴스를 선언할 수도 있습니다. 이 종류의 인스턴스는 네임스페이스 내부에 있을 때 또는 네임스페이스를 열 때만 활성화됩니다.

명령 `open scoped` `<namespace>`를 사용하여 범위 속성을 활성화할 수 있지만 네임스페이스에서 이름을 “열지” 않습니다.

```
structure Point where
x : Nat
y : Nat
namespace Point
scoped instance : Add Point where
add a b := { x := a.x + b.x, y := a.y + b.y }
def double (p : Point) :=
p + p
end Point
open scoped Point -- activates instance `Add Point`
#check fun (p : Point) => p + p + p
```

```
fun p => p + p + p : Point → Point
```

```
/--
error: Unknown identifier `double`
-/
#guard_msgs (error) in
#check fun (p : Point) => double p
```

```
fun p => sorry : (p : Point) → ?m.2 p
```

## 10.8. Decidable Propositions

Let us consider another example of a type class defined in the
standard library, namely the type class of `Decidable`
propositions. Roughly speaking, an element of `Prop` is said to be
decidable if we can decide whether it is true or false. The
distinction is only useful in constructive mathematics; classically,
every proposition is decidable. But if we use the classical principle,
say, to define a function by cases, that function will not be
computable. Algorithmically speaking, the `Decidable` type class can
be used to infer a procedure that effectively determines whether or
not the proposition is true. As a result, the type class supports such
computational definitions when they are possible while at the same
time allowing a smooth transition to the use of classical definitions
and classical reasoning.

표준 라이브러리에 정의된 타입 클래스의 또 다른 예인 `Decidable`(결정가능) 명제의 타입 클래스를 고려해봅시다. 대략적으로 말해서, `Prop`의 원소는 참 또는 거짓인지 결정할 수 있으면 결정 가능하다고 합니다. 이 구별은 구성적 수학에서만 유용합니다. 고전적으로는 모든 명제가 결정 가능합니다. 하지만 고전 원리를 사용하여, 예를 들어 함수를 경우로 정의하면 그 함수는 계산 가능하지 않을 것입니다. 알고리즘 관점에서 `Decidable` 타입 클래스는 명제가 참인지 거짓인지를 효과적으로 결정하는 절차를 추론하는 데 사용할 수 있습니다. 결과적으로 타입 클래스는 가능할 때 이러한 계산적 정의를 지원하면서 동시에 고전 정의와 고전 추론의 사용으로 매끄럽게 전환할 수 있도록 합니다.

In the standard library, `Decidable` is defined formally as follows:

표준 라이브러리에서 `Decidable`은 공식적으로 다음과 같이 정의됩니다:

```
class inductive Decidable (p : Prop) where
| isFalse (h : ¬p) : Decidable p
| isTrue (h : p) : Decidable p
```

Logically speaking, having an element `t : Decidable p` is stronger
than having an element `t' : p ∨ ¬p`; it enables us to define values
of an arbitrary type depending on the truth value of `p`. For
example, for the expression `if p then a else b` to make sense, we
need to know that `p` is decidable. That expression is syntactic
sugar for `ite p a b`, where `ite` is defined as follows:

논리적으로 말해서, 원소 `t : Decidable p`를 가지는 것은 원소 `t' : p ∨ ¬p`를 가지는 것보다 더 강합니다. 이는 `p`의 참 거짓 값에 따라 임의 타입의 값을 정의할 수 있도록 합니다. 예를 들어, 표현식 `if p then a else b`가 의미가 있으려면 `p`가 결정 가능함을 알아야 합니다. 그 표현식은 `ite p a b`의 문법 설탕이며, 여기서 `ite`는 다음과 같이 정의됩니다:

```
def ite {α : Sort u}
(c : Prop) [h : Decidable c]
(t e : α) : α :=
h.casesOn (motive := fun _ => α) (fun _ => e) (fun _ => t)
```

The standard library also contains a variant of `ite` called
`dite`, the dependent if-then-else expression. It is defined as
follows:

```
def dite {α : Sort u}
(c : Prop) [h : Decidable c]
(t : c → α) (e : Not c → α) : α :=
Decidable.casesOn (motive := fun _ => α) h e t
```

That is, in `dite c t e`, we can assume `hc : c` in the “then”
branch, and `hnc : ¬c` in the “else” branch. To make `dite` more
convenient to use, Lean allows us to write `if h : c then t else e`
instead of `dite c (fun h : c => t h) (fun h : ¬c => e h)`.

즉, `dite c t e`에서 우리는 “then” 분기에서 `hc : c`를 가정할 수 있고, “else” 분기에서 `hnc : ¬c`를 가정할 수 있습니다. `dite`를 더 편리하게 사용하기 위해 Lean은 `dite c (fun h : c => t h) (fun h : ¬c => e h)` 대신 `if h : c then t else e`를 쓸 수 있게 합니다.

Without classical logic, we cannot prove that every proposition is
decidable. But we can prove that *certain* propositions are
decidable. For example, we can prove the decidability of basic
operations like equality and comparisons on the natural numbers and
the integers. Moreover, decidability is preserved under propositional
connectives:

고전 논리 없이 모든 명제가 결정 가능하다는 것을 증명할 수 없습니다. 하지만 우리는 *특정* 명제가 결정 가능하다는 것을 증명할 수 있습니다. 예를 들어, 자연수와 정수에 대한 동일 및 비교와 같은 기본 연산의 결정 가능성을 증명할 수 있습니다. 더욱이 결정 가능성은 명제 연결 아래에서 보존됩니다:

```
#check @instDecidableAnd
```

```
@instDecidableAnd : {p q : Prop} → [dp : Decidable p] → [dq : Decidable q] → Decidable (p ∧ q)
```

```
#check @instDecidableOr
```

```
@instDecidableOr : {p q : Prop} → [dp : Decidable p] → [dq : Decidable q] → Decidable (p ∨ q)
```

```
#check @instDecidableNot
```

```
@instDecidableNot : {p : Prop} → [dp : Decidable p] → Decidable ¬p
```

Thus we can carry out definitions by cases on decidable predicates on
the natural numbers:

따라서 우리는 자연수에 대해 결정 가능한 술어로 경우별 정의를 수행할 수 있습니다:

```
def step (a b x : Nat) : Nat :=
if x < a ∨ x > b then 0 else 1
set_option pp.explicit true
#print step
```

```
def step : Nat → Nat → Nat → Nat :=
fun a b x =>
  @ite Nat (Or (@LT.lt Nat instLTNat x a) (@GT.gt Nat instLTNat x b))
    (@instDecidableOr (@LT.lt Nat instLTNat x a) (@GT.gt Nat instLTNat x b) (Nat.decLt x a) (Nat.decLt b x))
    (@OfNat.ofNat Nat (nat_lit 0) (instOfNatNat (nat_lit 0))) (@OfNat.ofNat Nat (nat_lit 1) (instOfNatNat (nat_lit 1)))
```

Turning on implicit arguments shows that the elaborator has inferred
the decidability of the proposition `x < a ∨ x > b`, simply by
applying appropriate instances.

암시적 인자를 켜면 엘래버레이터가 적절한 인스턴스를 적용하여 명제 `x < a ∨ x > b`의 결정 가능성을 추론했음을 보여줍니다.

With the classical axioms, we can prove that every proposition is
decidable. You can import the classical axioms and make the generic
instance of decidability available by opening the `Classical` namespace.

```
open Classical
```

Thereafter `Decidable p` has an instance for every `p`.
Thus all theorems in the library
that rely on decidability assumptions are freely available when you
want to reason classically. In [Axioms and Computation](../12-axioms-and-computation/#axioms-and-computation),
we will see that using the law of the
excluded middle to define functions can prevent them from being used
computationally. Thus, the standard library assigns a low priority to
the `propDecidable` instance.

```
open Classical
noncomputable scoped
instance (priority := low) propDecidable (a : Prop) : Decidable a :=
choice <| match em a with
| Or.inl h => ⟨isTrue h⟩
| Or.inr h => ⟨isFalse h⟩
```

This guarantees that Lean will favor other instances and fall back on
`propDecidable` only after other attempts to infer decidability have
failed.

고전 공리를 사용하여 모든 명제가 결정 가능하다는 것을 증명할 수 있습니다. 고전 공리를 임포트하고 `Classical` 네임스페이스를 열어 결정 가능성의 일반 인스턴스를 사용 가능하게 할 수 있습니다.

그 후 `Decidable p`는 모든 `p`에 대해 인스턴스를 가집니다. 따라서 결정 가능성 가정에 의존하는 라이브러리의 모든 정리는 고전적으로 추론하려고 할 때 자유롭게 사용할 수 있습니다. [Axioms and Computation](../12-axioms-and-computation/#axioms-and-computation)에서 우리는 배제 중간 법칙을 사용하여 함수를 정의하는 것이 그들이 계산적으로 사용되는 것을 방지할 수 있다는 것을 알 것입니다. 따라서 표준 라이브러리는 `propDecidable` 인스턴스에 낮은 우선순위를 할당합니다.

이는 Lean이 다른 인스턴스를 선호하고 결정 가능성을 추론하기 위한 다른 시도가 실패한 후에만 `propDecidable`로 돌아갈 것을 보장합니다.

The `Decidable` type class also provides a bit of small-scale
automation for proving theorems. The standard library introduces the
tactic `decide` that uses the `Decidable` instance to solve simple goals,
as well as a function `decide` that uses a `Decidable` instance to compute the
corresponding `Bool`.

```
example : 10 < 5 ∨ 1 > 0 := by
decide
example : ¬(True ∧ False) := by
decide
example : 10 * 20 = 200 := by
decide
theorem ex : True ∧ 2 = 1 + 1 := by
decide
#print ex
```

```
theorem ex : True ∧ 2 = 1 + 1 :=
of_decide_eq_true (id (Eq.refl true))
```

```
#check @of_decide_eq_true
```

```
@of_decide_eq_true : ∀ {p : Prop} [inst : Decidable p], decide p = true → p
```

```
#check @decide
```

```
decide : (p : Prop) → [h : Decidable p] → Bool
```

They work as follows. The expression `decide p` tries to infer a
decision procedure for `p`, and, if it is successful, evaluates to
either `true` or `false`. In particular, if `p` is a true closed
expression, `decide p` will reduce definitionally to the Boolean `true`.
On the assumption that `decide p = true` holds, `of_decide_eq_true`
produces a proof of `p`. The tactic `decide` puts it all together to
prove a target `p`. By the previous observations,
`decide` will succeed any time the inferred decision procedure
for `p` has enough information to evaluate, definitionally, to the `isTrue` case.

`Decidable` 타입 클래스는 또한 정리 증명을 위한 약간의 소규모 자동화를 제공합니다. 표준 라이브러리는 `Decidable` 인스턴스를 사용하여 간단한 목표를 해결하는 전술 `decide`와 `Decidable` 인스턴스를 사용하여 해당 `Bool`을 계산하는 함수 `decide`를 도입합니다.

그들은 다음과 같이 작동합니다. 표현식 `decide p`는 `p`에 대한 결정 절차를 추론하려고 시도하고, 성공하면 `true` 또는 `false`로 평가됩니다. 특히, `p`가 참인 닫힌 표현식이면 `decide p`는 불린 `true`로 정의적으로 축약됩니다. `decide p = true`가 성립한다는 가정 하에서 `of_decide_eq_true`는 `p`의 증명을 생성합니다. 전술 `decide`는 이들을 모두 함께 모아 대상 `p`를 증명합니다. 이전의 관찰에 의해 `decide`는 `p`에 대한 추론된 결정 절차가 `isTrue` 경우로 정의적으로 평가할 충분한 정보를 가질 때마다 성공할 것입니다.

## 10.9. Managing Type Class Inference

If you are ever in a situation where you need to supply an expression
that Lean can infer by type class inference, you can ask Lean to carry
out the inference using `inferInstance`:

타입 클래스 추론으로 Lean이 추론할 수 있는 표현식을 제공해야 하는 상황에 처하면 `inferInstance`를 사용하여 Lean이 추론을 수행하도록 요청할 수 있습니다:

```
def foo : Add Nat := inferInstance
def bar : Inhabited (Nat → Nat) := inferInstance
#check @inferInstance
```

```
@inferInstance : {α : Sort u_1} → [i : α] → α
```

In fact, you can use Lean's `(t : T)` notation to specify the class whose instance you are looking for,
in a concise manner:

실제로 Lean의 `(t : T)` 표기법을 사용하여 찾고 있는 인스턴스의 클래스를 간결하게 지정할 수 있습니다:

```
#check (inferInstance : Add Nat)
```

```
inferInstance : Add Nat
```

You can also use the auxiliary definition `inferInstanceAs`:

보조 정의 `inferInstanceAs`도 사용할 수 있습니다:

```
#check inferInstanceAs (Add Nat)
```

```
inferInstanceAs (Add Nat) : Add Nat
```

```
#check @inferInstanceAs
```

```
inferInstanceAs : (α : Sort u_1) → [i : α] → α
```

Sometimes Lean can't find an instance because the class is buried
under a definition. For example, Lean cannot
find an instance of `Inhabited (Set α)`. We can declare one
explicitly:

때때로 Lean은 클래스가 정의 아래에 숨어 있기 때문에 인스턴스를 찾을 수 없습니다. 예를 들어, Lean은 `Inhabited (Set α)`의 인스턴스를 찾을 수 없습니다. 우리는 하나를 명시적으로 선언할 수 있습니다:

```
def Set (α : Type u) := α → Prop
/--
error: failed to synthesize
  Inhabited (Set α)

Hint: Additional diagnostic information may be available using
the `set_option diagnostics true` command.
-/
#guard_msgs in
example : Inhabited (Set α) :=
inferInstance
instance : Inhabited (Set α) :=
inferInstanceAs (Inhabited (α → Prop))
```

At times, you may find that the type class inference fails to find an
expected instance, or, worse, falls into an infinite loop and times
out. To help debug in these situations, Lean enables you to request a
trace of the search:

때때로 타입 클래스 추론이 예상된 인스턴스를 찾지 못하거나, 더 나쁜 경우 무한 루프에 빠져 시간 초과가 될 수 있습니다. 이러한 상황에서 디버그하기 위해 Lean은 검색의 추적을 요청할 수 있도록 합니다:

```
set_option trace.Meta.synthInstance true
```

If you are using VS Code, you can read the results by hovering over
the relevant theorem or definition, or opening the messages window
with `CtrlShiftEnter`.

You can also limit the search using the following options:

```
set_option synthInstance.maxHeartbeats 10000
set_option synthInstance.maxSize 400
```

Option `synthInstance.maxHeartbeats` specifies the maximum amount of
heartbeats per typeclass resolution problem. A heartbeat is the number of
(small) memory allocations (in thousands), 0 means there is no limit.
Option `synthInstance.maxSize` is the maximum number of instances used
to construct a solution in the type class instance synthesis procedure.

Remember also that in both the VS Code and Emacs editor modes, tab
completion works in `set_option`, to help you find suitable options.

VS Code를 사용하고 있다면 관련 정리 또는 정의 위에 마우스를 올려 결과를 읽거나 `CtrlShiftEnter`로 메시지 창을 열 수 있습니다.

다음 옵션을 사용하여 검색을 제한할 수도 있습니다:

옵션 `synthInstance.maxHeartbeats`는 타입 클래스 해석 문제당 최대 하트비트를 지정합니다. 하트비트는 (작은) 메모리 할당의 수(천 단위)이고, 0은 제한이 없음을 의미합니다. 옵션 `synthInstance.maxSize`는 타입 클래스 인스턴스 합성 절차에서 솔루션을 구성하는 데 사용되는 최대 인스턴스 수입니다.

또한 VS Code와 Emacs 편집기 모드 모두에서 `set_option`에 탭 완성이 작동하여 적합한 옵션을 찾는 데 도움이 됨을 기억하세요.

As noted above, the type class instances in a given context represent
a Prolog-like program, which gives rise to a backtracking search. Both
the efficiency of the program and the solutions that are found can
depend on the order in which the system tries the instance. Instances
which are declared last are tried first. Moreover, if instances are
declared in other modules, the order in which they are tried depends
on the order in which namespaces are opened. Instances declared in
namespaces which are opened later are tried earlier.

위에서 언급했듯이, 주어진 컨텍스트의 타입 클래스 인스턴스는 Prolog과 유사한 프로그램을 나타내고, 이는 역추적 검색을 발생시킵니다. 프로그램의 효율성과 찾은 솔루션 모두 시스템이 인스턴스를 시도하는 순서에 따라 달라질 수 있습니다. 마지막에 선언된 인스턴스가 먼저 시도됩니다. 더욱이 인스턴스가 다른 모듈에서 선언되면, 그들이 시도되는 순서는 네임스페이스가 열리는 순서에 따라 달라집니다. 나중에 열린 네임스페이스에서 선언된 인스턴스가 더 일찍 시도됩니다.

You can change the order that type class instances are tried by
assigning them a *priority*. When an instance is declared, it is
assigned a default priority value. You can assign other priorities
when defining an instance. The following example illustrates how this
is done:

*우선순위*를 할당하여 타입 클래스 인스턴스가 시도되는 순서를 변경할 수 있습니다. 인스턴스가 선언될 때, 기본 우선순위 값이 할당됩니다. 인스턴스를 정의할 때 다른 우선순위를 할당할 수 있습니다. 다음 예제는 이것이 어떻게 수행되는지를 보여줍니다:

```
class Foo where
a : Nat
b : Nat
instance (priority := default + 1) i1 : Foo where
a := 1
b := 1
instance i2 : Foo where
a := 2
b := 2
example : Foo.a = 1 :=
rfl
instance (priority := default + 2) i3 : Foo where
a := 3
b := 3
example : Foo.a = 3 :=
rfl
```

## 10.10. Coercions using Type Classes

The most basic type of coercion maps elements of one type to another. For example, a coercion from `Nat` to `Int` allows us to view any element `n : Nat` as an element of `Int`. But some coercions depend on parameters; for example, for any type `α`, we can view any element `as : List α` as an element of `Set α`, namely, the set of elements occurring in the list. The corresponding coercion is defined on the “family” of types `List α`, parameterized by `α`.

가장 기본적인 강제 유형은 한 타입의 원소를 다른 타입으로 매핑합니다. 예를 들어, `Nat`에서 `Int`로의 강제는 모든 원소 `n : Nat`을 `Int`의 원소로 볼 수 있게 합니다. 하지만 일부 강제는 매개변수에 따라 다릅니다. 예를 들어, 모든 타입 `α`에 대해 모든 원소 `as : List α`을 `Set α`의 원소로 볼 수 있습니다. 즉, 목록에 나타나는 원소의 집합입니다. 해당 강제는 `α`로 매개변수화된 타입 `List α`의 “제족”에서 정의됩니다.

Lean allows us to declare three kinds of coercions:

from a family of types to another family of types
* from a family of types to the class of sorts
* from a family of types to the class of function types

from a family of types to the class of sorts

from a family of types to the class of function types

The first kind of coercion allows us to view any element of a member of the source family as an element of a corresponding member of the target family. The second kind of coercion allows us to view any element of a member of the source family as a type. The third kind of coercion allows us to view any element of the source family as a function. Let us consider each of these in turn.

Lean은 세 가지 종류의 강제를 선언할 수 있게 합니다:

* 타입의 한 제족에서 다른 제족으로의 강제

* 타입의 제족에서 정렬 클래스로의 강제

* 타입의 제족에서 함수 타입 클래스로의 강제

첫 번째 종류의 강제는 원본 제족의 구성원의 모든 원소를 대상 제족의 해당 구성원의 원소로 볼 수 있게 합니다. 두 번째 종류의 강제는 원본 제족의 구성원의 모든 원소를 타입으로 볼 수 있게 합니다. 세 번째 종류의 강제는 원본 제족의 모든 원소를 함수로 볼 수 있게 합니다. 이들 각각을 차례대로 고려해봅시다.

In Lean, coercions are implemented on top of the type class resolution framework. We define a coercion from `α` to `β` by declaring an instance of `Coe α β`. For example, we can define a coercion from `Bool` to `Prop` as follows:

Lean에서 강제는 타입 클래스 해석 프레임워크 위에 구현됩니다. `Coe α β`의 인스턴스를 선언하여 `α`에서 `β`로의 강제를 정의합니다. 예를 들어, `Bool`에서 `Prop`으로의 강제를 다음과 같이 정의할 수 있습니다:

```
instance : Coe Bool Prop where
coe b := b = true
```

This enables us to use boolean terms in `if`-`then`-`else` expressions:

이것은 `if`-`then`-`else` 표현식에서 불린 항을 사용할 수 있게 합니다:

```
#eval if true then 5 else 3
```

```
5
```

```
#eval if false then 5 else 3
```

```
3
```

We can define a coercion from `List α` to `Set α` as follows:

`List α`에서 `Set α`로의 강제를 다음과 같이 정의할 수 있습니다:

```
def List.toSet : List α → Set α
| [] => Set.empty
| a::as => {a} ∪ as.toSet
instance : Coe (List α) (Set α) where
coe a := a.toSet
def s : Set Nat := {1}
#check s ∪ [2, 3]
```

```
s ∪ [2, 3].toSet : Set Nat
```

We can use the notation `↑` to force a coercion to be introduced in a particular place. It is also helpful to make our intent clear, and work around limitations of the coercion resolution system.

표기법 `↑`을 사용하여 특정 위치에서 강제를 도입하도록 강제할 수 있습니다. 또한 우리의 의도를 명확히 하고 강제 해석 시스템의 한계를 극복하는 데 도움이 됩니다.

```
def s : Set Nat := {1}
#check let x := ↑[2, 3]; s ∪ x
```

```
let x := [2, 3].toSet;
s ∪ x : Set Nat
```

```
#check let x := [2, 3]; s ∪ x
```

```
let x := [2, 3];
s ∪ x.toSet : Set Nat
```

Lean also supports dependent coercions using the type class `CoeDep`. For example, we cannot coerce arbitrary propositions to `Bool`, only the ones that implement the `Decidable` typeclass.

```
instance (p : Prop) [Decidable p] : CoeDep Prop p Bool where
coe := decide p
```

Lean will also chain (non-dependent) coercions as necessary. Actually, the type class `CoeT` is the transitive closure of `Coe`.

Lean은 또한 타입 클래스 `CoeDep`을 사용하여 종속 강제를 지원합니다. 예를 들어, 우리는 임의의 명제를 `Bool`로 강제할 수 없으며, `Decidable` 타입 클래스를 구현하는 것들만 강제할 수 있습니다.

Lean은 필요에 따라 (비-종속) 강제를 연결합니다. 실제로 타입 클래스 `CoeT`는 `Coe`의 이행적 폐포입니다.

Let us now consider the second kind of coercion. By the *class of sorts*, we mean the collection of universes `Type u`. A coercion of the second kind is of the form:

where `F` is a family of types as above. This allows us to write `s : t` whenever `t` is of type `F a₁ ... aₙ`. In other words, the coercion allows us to view the elements of `F a₁ ... aₙ` as types. This is very useful when defining algebraic structures in which one component, the carrier of the structure, is a `Type`. For example, we can define a semigroup as follows:

이제 두 번째 종류의 강제를 고려해봅시다. *정렬의 클래스*라고 할 때, 우리는 우주 `Type u`의 모음을 의미합니다. 두 번째 종류의 강제는 다음의 형태입니다:

여기서 `F`는 위의 타입의 제족입니다. 이것은 `t`가 `F a₁ ... aₙ` 타입일 때마다 `s : t`를 쓸 수 있게 합니다. 다시 말해, 강제는 `F a₁ ... aₙ`의 원소를 타입으로 볼 수 있게 합니다. 이것은 구조의 운반자인 하나의 구성 요소가 `Type`인 대수적 구조를 정의할 때 매우 유용합니다. 예를 들어, 다음과 같이 반군을 정의할 수 있습니다:

```
structure Semigroup where
carrier : Type u
mul : carrier → carrier → carrier
mul_assoc (a b c : carrier) : mul (mul a b) c = mul a (mul b c)
instance (S : Semigroup) : Mul S.carrier where
mul a b := S.mul a b
```

In other words, a semigroup consists of a type, `carrier`, and a multiplication, `mul`, with the property that the multiplication is associative. The `instance` command allows us to write `a * b` instead of `Semigroup.mul S a b` whenever we have `a b : S.carrier`; notice that Lean can infer the argument `S` from the types of `a` and `b`. The function `Semigroup.carrier` maps the class `Semigroup` to the sort `Type u`:

다시 말해, 반군은 타입 `carrier`와 곱셈이 결합적이라는 성질을 가진 곱셈 `mul`로 구성됩니다. `instance` 명령은 `a b : S.carrier`를 가질 때마다 `Semigroup.mul S a b` 대신 `a * b`를 쓸 수 있게 합니다. Lean은 `a`와 `b`의 타입에서 인자 `S`를 추론할 수 있음을 주목하세요. 함수 `Semigroup.carrier`는 클래스 `Semigroup`을 정렬 `Type u`로 매핑합니다:

```
#check Semigroup.carrier
```

```
Semigroup.carrier.{u} (self : Semigroup) : Type u
```

If we declare this function to be a coercion, then whenever we have a semigroup `S : Semigroup`, we can write `a : S` instead of `a : S.carrier`:

이 함수를 강제로 선언하면, 반군 `S : Semigroup`을 가질 때마다 `a : S.carrier` 대신 `a : S`를 쓸 수 있습니다:

```
instance : CoeSort Semigroup (Type u) where
coe s := s.carrier
example (S : Semigroup) (a b c : S) : (a * b) * c = a * (b * c) :=
Semigroup.mul_assoc _ a b c
```

It is the coercion that makes it possible to write `(a b c : S)`. Note that, we define an instance of `CoeSort Semigroup (Type u)` instead of `Coe Semigroup (Type u)`.

`(a b c : S)`를 쓸 수 있게 하는 것은 강제입니다. `Coe Semigroup (Type u)` 대신 `CoeSort Semigroup (Type u)`의 인스턴스를 정의함을 주목하세요.

By the *class of function types*, we mean the collection of Pi types `(z : B) → C`. The third kind of coercion has the form:

where `F` is again a family of types and `B` and `C` can depend on `x₁, ..., xₙ, y`. This makes it possible to write `t s` whenever `t` is an element of `F a₁ ... aₙ`. In other words, the coercion enables us to view elements of `F a₁ ... aₙ` as functions. Continuing the example above, we can define the notion of a morphism between semigroups `S1` and `S2`. That is, a function from the carrier of `S1` to the carrier of `S2` (note the implicit coercion) that respects the multiplication. The projection `Morphism.mor` takes a morphism to the underlying function:

*함수 타입의 클래스*라고 할 때, 우리는 Pi 타입 `(z : B) → C`의 모음을 의미합니다. 세 번째 종류의 강제는 다음의 형태입니다:

여기서 `F`는 다시 타입의 제족이고 `B`와 `C`는 `x₁, ..., xₙ, y`에 따라 달라질 수 있습니다. 이것은 `t`가 `F a₁ ... aₙ`의 원소일 때마다 `t s`를 쓸 수 있게 합니다. 다시 말해, 강제는 `F a₁ ... aₙ`의 원소를 함수로 볼 수 있게 합니다. 위의 예제를 계속하여, 우리는 반군 `S1`과 `S2` 간의 동형사상의 개념을 정의할 수 있습니다. 즉, `S1`의 운반자에서 `S2`의 운반자로의 함수(암시적 강제를 주목)로 곱셈을 존중합니다. 투영 `Morphism.mor`은 동형사상을 기본 함수로 가집니다:

```
structure Morphism (S1 S2 : Semigroup) where
mor : S1 → S2
resp_mul : ∀ a b : S1, mor (a * b) = (mor a) * (mor b)
#check @Morphism.mor
```

```
@Morphism.mor : {S1 : Semigroup} → {S2 : Semigroup} → Morphism S1 S2 → S1.carrier → S2.carrier
```

As a result, it is a prime candidate for the third type of coercion.

결과적으로 이것은 세 번째 종류의 강제의 주요 후보입니다.

```
instance (S1 S2 : Semigroup) :
CoeFun (Morphism S1 S2) (fun _ => S1 → S2) where
coe m := m.mor
theorem resp_mul {S1 S2 : Semigroup} (f : Morphism S1 S2) (a b : S1)
: f (a * b) = f a * f b :=
f.resp_mul a b
example (S1 S2 : Semigroup) (f : Morphism S1 S2) (a : S1) :
f (a * a * a) = f a * f a * f a :=
calc f (a * a * a)
_ = f (a * a) * f a := by rw [resp_mul f]
_ = f a * f a * f a := by rw [resp_mul f]
```

With the coercion in place, we can write `f (a * a * a)` instead of `f.mor (a * a * a)`. When the `Morphism`, `f`, is used where a function is expected, Lean inserts the coercion. Similar to `CoeSort`, we have yet another class `CoeFun` for this class of coercions. The parameter `γ` is used to specify the function type we are coercing to. This type may depend on the type we are coercing from.

강제가 제 위치에 있으면 `f.mor (a * a * a)` 대신 `f (a * a * a)`를 쓸 수 있습니다. `Morphism` `f`가 함수가 예상되는 곳에서 사용될 때, Lean은 강제를 삽입합니다. `CoeSort`와 유사하게 우리는 이 클래스의 강제를 위한 또 다른 클래스 `CoeFun`을 가지고 있습니다. 매개변수 `γ`는 우리가 강제하는 함수 타입을 지정하는 데 사용됩니다. 이 타입은 우리가 강제하는 타입에 따라 달라질 수 있습니다.
