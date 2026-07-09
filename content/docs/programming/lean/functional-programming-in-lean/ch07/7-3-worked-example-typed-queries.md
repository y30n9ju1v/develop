---
title: "예제로 배우기: 타입이 있는 쿼리 (Worked Example: Typed Queries)"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "예제로 배우기: 타입이 있는 쿼리 (Worked Example: Typed Queries)"
---

# Worked Example: Typed Queries

Indexed families are very useful when building an API that is supposed to resemble some other language.
They can be used to write a library of HTML constructors that don't permit generating invalid HTML, to encode the specific rules of a configuration file format, or to model complicated business constraints.
This section describes an encoding of a subset of relational algebra in Lean using indexed families, as a simpler demonstration of techniques that can be used to build a more powerful database query language.

Indexed families은 다른 언어와 유사하도록 의도된 API를 구축할 때 매우 유용합니다.
잘못된 HTML 생성을 허용하지 않는 HTML 생성자의 라이브러리를 작성하거나, 구성 파일 형식의 특정 규칙을 인코딩하거나, 복잡한 비즈니스 제약을 모델링하는 데 사용될 수 있습니다.
이 섹션은 더 강력한 데이터베이스 쿼리 언어를 구축하는 데 사용할 수 있는 기술의 더 간단한 시연으로서, indexed families을 사용하여 Lean에서 relational algebra의 부분집합을 인코딩하는 것을 설명합니다.

This subset uses the type system to enforce requirements such as disjointness of field names, and it uses type-level computation to reflect the schema into the types of values that are returned from a query.
It is not a realistic system, however—databases are represented as linked lists of linked lists, the type system is much simpler than that of SQL, and the operators of relational algebra don't really match those of SQL.
However, it is large enough to demonstrate useful principles and techniques.

이 부분은 field name의 disjointness와 같은 요구사항을 강화하기 위해 type system을 사용하며, type-level computation을 사용하여 schema를 query에서 반환되는 값들의 type으로 반영합니다.
하지만 이것은 현실적인 시스템은 아닙니다. 데이터베이스는 linked list의 linked list로 표현되며, type system은 SQL의 것보다 훨씬 단순하고, relational algebra의 operator들은 SQL의 것과 정말로 일치하지 않습니다.
그러나 이것은 유용한 원칙과 기술을 시연하기에 충분할 정도로 큽니다.

## 7.3.1. A Universe of Data

In this relational algebra, the base data that can be held in columns can have types `Int`, `String`, and `Bool` and are described by the universe `DBType`:

```lean
inductive DBType where
| int | string | bool
abbrev DBType.asType : DBType → Type
| .int => Int
| .string => String
| .bool => Bool
```

Using `DBType.asType` allows these codes to be used for types.
For example:

```lean
#eval ("Mount Hood" : DBType.string.asType)
```

```
"Mount Hood"
```

It is possible to compare the values described by any of the three database types for equality.
Explaining this to Lean, however, requires a bit of work.

세 가지 database type 중 하나로 설명된 값들을 동등성에 대해 비교할 수 있습니다.
하지만 이를 Lean에 설명하려면 약간의 작업이 필요합니다.
Simply using `BEq` directly fails:

```lean
def DBType.beq (t : DBType) (x y : t.asType) : Bool :=
  x == y
```

```
failed to synthesize
  BEq t.asType

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.
```

Just as in the nested pairs universe, type class search doesn't automatically check each possibility for `t`'s value
The solution is to use pattern matching to refine the types of `x` and `y`:

nested pairs universe에서처럼, type class search는 `t`의 값에 대한 각 가능성을 자동으로 확인하지 않습니다.
해결 방법은 pattern matching을 사용하여 `x`와 `y`의 type을 refine하는 것입니다.

```lean
def DBType.beq (t : DBType) (x y : t.asType) : Bool :=
  match t with
  | .int => x == y
  | .string => x == y
  | .bool => x == y
```

In this version of the function, `x` and `y` have types `Int`, `String`, and `Bool` in the three respective cases, and these types all have `BEq` instances.

이 버전의 함수에서 `x`와 `y`는 세 가지 각각의 경우에 `Int`, `String`, `Bool` type을 가지며, 이 type들 모두는 `BEq` instance를 가집니다.
The definition of `DBType.beq` can be used to define a `BEq` instance for the types that are coded for by `DBType`:

```lean
instance {t : DBType} : BEq t.asType where
  beq := t.beq
```

This is not the same as an instance for the codes:

```lean
instance : BEq DBType where
  beq
    | .int, .int => true
    | .string, .string => true
    | .bool, .bool => true
    | _, _ => false
```

The former instance allows comparison of values drawn from the types described by the codes, while the latter allows comparison of the codes themselves.

전자의 instance는 code들로 설명되는 type에서 가져온 값들의 비교를 허용하는 반면, 후자는 code 자체의 비교를 허용합니다.

A `Repr` instance can be written using the same technique.
The method of the `Repr` class is called `reprPrec` because it is designed to take things like operator precedence into account when displaying values.
Refining the type through dependent pattern matching allows the `reprPrec` methods from the `Repr` instances for `Int`, `String`, and `Bool` to be used:

`Repr` instance도 동일한 기술을 사용하여 작성할 수 있습니다.
`Repr` class의 method는 `reprPrec`이라고 불리는데, 이는 값을 표시할 때 operator precedence와 같은 것들을 고려하도록 설계되었기 때문입니다.
dependent pattern matching을 통해 type을 refine하면 `Int`, `String`, `Bool`에 대한 `Repr` instance의 `reprPrec` method를 사용할 수 있습니다.

```lean
instance {t : DBType} : Repr t.asType where
  reprPrec :=
    match t with
    | .int => reprPrec
    | .string => reprPrec
    | .bool => reprPrec
```

## 7.3.2. Schemas and Tables

A schema describes the name and type of each column in a database:

Schema는 데이터베이스의 각 column의 name과 type을 설명합니다.

```lean
structure Column where
  name : String
  contains : DBType
abbrev Schema := List Column
```

In fact, a schema can be seen as a universe that describes rows in a table.
The empty schema describes the unit type, a schema with a single column describes that value on its own, and a schema with at least two columns is represented by a tuple:

실제로, schema는 table의 row를 설명하는 universe로 볼 수 있습니다.
빈 schema는 unit type을 설명하고, 단일 column을 가진 schema는 해당 값 자체를 설명하며, 최소한 두 개의 column을 가진 schema는 tuple로 표현됩니다.

```lean
abbrev Row : Schema → Type
  | [] => Unit
  | [col] => col.contains.asType
  | col1 :: col2 :: cols => col1.contains.asType × Row (col2::cols)
```

As described in [the initial section on product types](../ch01/), Lean's product type and tuples are right-associative.
This means that nested pairs are equivalent to ordinary flat tuples.

[product type에 대한 초기 섹션](../ch01/)에서 설명했듯이, Lean의 product type과 tuple은 right-associative입니다.
즉, nested pair가 ordinary flat tuple과 동등함입니다.

A table is a list of rows that share a schema:

Table은 schema를 공유하는 row들의 list입니다.

```lean
abbrev Table (s : Schema) := List (Row s)
```

For example, a diary of visits to mountain peaks can be represented with the schema `peak`:

예를 들어, 산봉우리 방문 일기는 schema `peak`로 표현할 수 있습니다.

```lean
abbrev peak : Schema := [
  ⟨"name", .string⟩,
  ⟨"location", .string⟩,
  ⟨"elevation", .int⟩,
  ⟨"lastVisited", .int⟩
]
```

A selection of peaks visited by the author of this book appears as an ordinary list of tuples:

이 책의 저자가 방문한 산봉우리들의 선택은 ordinary list of tuple로 나타납니다.

```lean
def mountainDiary : Table peak := [
  ("Mount Nebo", "USA", 3637, 2013),
  ("Moscow Mountain", "USA", 1519, 2015),
  ("Himmelbjerget", "Denmark", 147, 2004),
  ("Mount St. Helens", "USA", 2549, 2010)
]
```

Another example consists of waterfalls and a diary of visits to them:

또 다른 예는 폭포와 그곳 방문 일기로 구성됩니다.

```lean
abbrev waterfall : Schema := [
  ⟨"name", .string⟩,
  ⟨"location", .string⟩,
  ⟨"lastVisited", .int⟩
]
```

```lean
def waterfallDiary : Table waterfall := [
  ("Multnomah Falls", "USA", 2018),
  ("Shoshone Falls", "USA", 2014)
]
```

### 7.3.2.1. Recursion and Universes, Revisited

The convenient structuring of rows as tuples comes at a cost: the fact that `Row` treats its two base cases separately means that functions that use `Row` in their types and are defined recursively over the codes (that, is the schema) need to make the same distinctions.

row를 tuple로 편리하게 구조화하는 것에는 대가가 따릅니다. `Row`가 두 개의 base case를 따로 취급한다는 사실은, 자신의 type에 `Row`를 사용하고 code (즉, schema)에 대해 recursively 정의된 함수들이 동일한 구분을 해야 함을 의미합니다.
One example of a case where this matters is an equality check that uses recursion over the schema to define a function that checks rows for equality.
This example does not pass Lean's type checker:

```lean
def Row.bEq (r1 r2 : Row s) : Bool :=
  match s with
  | [] => true
  | col::cols =>
    match r1, r2 with
    | (v1, r1'), (v2, r2') =>
      v1 == v2 && bEq r1' r2'
```

```
Type mismatch
  (v1, r1')
has type
  ?m.10 × ?m.11
but is expected to have type
  Row (col :: cols)
```

The problem is that the pattern `col :: cols` does not sufficiently refine the type of the rows.
This is because Lean cannot yet tell whether the singleton pattern `[col]` or the `col1 :: col2 :: cols` pattern in the definition of `Row` was matched, so the call to `Row` does not compute down to a pair type.

문제는 pattern `col :: cols`가 row의 type을 충분히 refine하지 않는다는 것입니다.
이는 Lean이 `Row`의 정의에서 singleton pattern `[col]`인지 아니면 `col1 :: col2 :: cols` pattern인지 아직 구분할 수 없기 때문에, `Row`에 대한 호출이 pair type으로 계산되지 않습니다.
The solution is to mirror the structure of `Row` in the definition of `Row.bEq`:

```lean
def Row.bEq (r1 r2 : Row s) : Bool :=
  match s with
  | [] => true
  | [_] => r1 == r2
  | _::_::_ =>
    match r1, r2 with
    | (v1, r1'), (v2, r2') =>
      v1 == v2 && bEq r1' r2'

instance : BEq (Row s) where
  beq := Row.bEq
```

Unlike in other contexts, functions that occur in types cannot be considered only in terms of their input/output behavior.
Programs that use these types will find themselves forced to mirror the algorithm used in the type-level function so that their structure matches the pattern-matching and recursive behavior of the type.
A big part of the skill of programming with dependent types is the selection of appropriate type-level functions with the right computational behavior.

다른 문맥과 달리, type에서 나타나는 함수들은 input/output 행동의 관점에서만 고려될 수 없습니다.
이러한 type을 사용하는 프로그램은 자신의 구조가 type의 pattern-matching과 recursive 행동과 일치하도록 type-level function에서 사용되는 algorithm을 mirror하도록 강제됩니다.
dependent type으로 프로그래밍하는 기술의 큰 부분은 올바른 computational behavior를 가진 적절한 type-level function의 선택입니다.

### 7.3.2.2. Column Pointers

Some queries only make sense if a schema contains a particular column.
For example, a query that returns mountains with an elevation greater than 1000 meters only makes sense in the context of a schema with an `"elevation"` column that contains integers.
One way to indicate that a column is contained in a schema is to provide a pointer directly to it, and defining the pointer as an indexed family makes it possible to rule out invalid pointers.

일부 query는 schema에 특정 column이 포함되어 있을 때만 의미가 있습니다.
예를 들어, elevation이 1000미터 이상인 산들을 반환하는 query는 정수를 포함하는 `"elevation"` column을 가진 schema의 문맥에서만 의미가 있습니다.
column이 schema에 포함되어 있음을 나타내는 한 가지 방법은 이를 직접 pointer로 제공하는 것이며, pointer를 indexed family로 정의하면 invalid pointer를 배제할 수 있습니다.

There are two ways that a column can be present in a schema: either it is at the beginning of the schema, or it is somewhere later in the schema.
Eventually, if a column is later in a schema, then it will be the beginning of some tail of the schema.

column이 schema에 존재할 수 있는 두 가지 방법이 있습니다. schema의 시작 부분에 있거나, schema의 어딘가 뒤의 위치에 있습니다.
결국, column이 schema의 뒤에 있다면, schema의 어떤 tail의 시작이 될 것입니다.

The indexed family `HasCol` is a translation of the specification into Lean code:

```lean
inductive HasCol : Schema → String → DBType → Type where
  | here : HasCol (⟨name, t⟩ :: _) name t
  | there : HasCol s name t → HasCol (_ :: s) name t
```

The family's three arguments are the schema, the column name, and its type.
All three are indices, but re-ordering the arguments to place the schema after the column name and type would allow the name and type to be parameters.

family의 세 가지 인자는 schema, column name, 그리고 type입니다.
세 가지 모두 index이지만, schema를 column name과 type 뒤에 배치하도록 인자를 재정렬하면 name과 type이 parameter가 될 수 있습니다.
The constructor `here` can be used when the schema begins with the column `⟨name, t⟩`; it is thus a pointer to the first column in the schema that can only be used when the first column has the desired name and type.
The constructor `there` transforms a pointer into a smaller schema into a pointer into a schema with one more column on it.

Because `"elevation"` is the third column in `peak`, it can be found by looking past the first two columns with `there`, after which it is the first column.
In other words, to satisfy the type `HasCol peak "elevation" .int`, use the expression `.there (.there .here)`.
One way to think about `HasCol` is as a kind of decorated `Nat`—`zero` corresponds to `here`, and `succ` corresponds to `there`.
The extra type information makes it impossible to have off-by-one errors.

`"elevation"`은 `peak`의 세 번째 column이므로, `there`로 처음 두 column을 지난 후 첫 번째 column이 됩니다.
다시 말해, `HasCol peak "elevation" .int` type을 만족시키려면 `.there (.there .here)` expression을 사용합니다.
`HasCol`을 생각하는 한 가지 방법은 decorated `Nat`의 일종입니다. `zero`는 `here`에 대응하고, `succ`는 `there`에 대응합니다.
추가 type 정보는 off-by-one error를 불가능하게 만듭니다.

A pointer to a particular column in a schema can be used to extract that column's value from a row:

schema의 특정 column에 대한 pointer는 row에서 해당 column의 값을 추출하는 데 사용할 수 있습니다.

```lean
def Row.get (row : Row s) (col : HasCol s n t) : t.asType :=
  match s, col, row with
  | [_], .here, v => v
  | _::_::_, .here, (v, _) => v
  | _::_::_, .there next, (_, r) => get r next
```

The first step is to pattern match on the schema, because this determines whether the row is a tuple or a single value.
No case is needed for the empty schema because there is a `HasCol` available, and both constructors of `HasCol` specify non-empty schemas.
If the schema has just a single column, then the pointer must point to it, so only the `here` constructor of `HasCol` need be matched.
If the schema has two or more columns, then there must be a case for `here`, in which case the value is the first one in the row, and one for `there`, in which case a recursive call is used.
Because the `HasCol` type guarantees that the column exists in the row, `Row.get` does not need to return an `Option`.

첫 번째 단계는 schema에서 pattern matching을 하는 것입니다. 이는 row가 tuple인지 single value인지를 결정하기 때문입니다.
`HasCol`을 사용할 수 있고, `HasCol`의 두 constructor 모두 non-empty schema를 지정하기 때문에 empty schema에는 case가 필요하지 않습니다.
schema가 단 하나의 column을 가지고 있다면, pointer는 이를 가리켜야 하므로, `HasCol`의 `here` constructor만 matching되면 됩니다.
schema에 두 개 이상의 column이 있다면, `here`의 case가 있어야 하며, 이 경우 값은 row의 첫 번째이고, `there`의 case가 있어야 하며, 이 경우 recursive call이 사용됩니다.
`HasCol` type은 column이 row에 존재함을 보장하기 때문에, `Row.get`은 `Option`을 반환할 필요가 없습니다.

`HasCol` plays two roles:

1. It serves as *evidence* that a column with a particular name and type exists in a schema.
2. It serves as *data* that can be used to find the value associated with the column in a row.

The first role, that of evidence, is similar to way that propositions are used.
The definition of the indexed family `HasCol` can be read as a specification of what counts as evidence that a given column exists.
Unlike propositions, however, it matters which constructor of `HasCol` was used.
In the second role, the constructors are used like `Nat`s to find data in a collection.
Programming with indexed families often requires the ability to switch fluently between both perspectives.

`HasCol`은 두 가지 역할을 합니다:

1. 특정 name과 type을 가진 column이 schema에 존재한다는 *evidence*로 작용합니다.
2. row에서 column과 연결된 값을 찾는 데 사용할 수 있는 *data*로 작용합니다.

첫 번째 역할인 evidence는 proposition이 사용되는 방식과 유사합니다.
indexed family `HasCol`의 정의는 주어진 column이 존재한다는 evidence로 간주되는 것에 대한 specification으로 읽을 수 있습니다.
그러나 proposition과 달리, 어떤 `HasCol` constructor가 사용되었는지가 중요합니다.
두 번째 역할에서 constructor는 collection에서 data를 찾기 위해 `Nat`처럼 사용됩니다.
indexed family로 프로그래밍하려면 종종 두 관점 모두를 유창하게 전환할 수 있는 능력이 필요합니다.

### 7.3.2.3. Subschemas

One important operation in relational algebra is to *project* a table or row into a smaller schema.
Every column not present in the smaller schema is forgotten.
In order for projection to make sense, the smaller schema must be a subschema of the larger schema, which means that every column in the smaller schema must be present in the larger schema.
Just as `HasCol` makes it possible to write a single-column lookup in a row that cannot fail, a representation of the subschema relationship as an indexed family makes it possible to write a projection function that cannot fail.

relational algebra에서 중요한 operation 중 하나는 table이나 row를 더 작은 schema로 *project*하는 것입니다.
더 작은 schema에 없는 모든 column은 잊혀집니다.
projection이 의미를 가지려면, 더 작은 schema는 더 큰 schema의 subschema여야 하며, 즉, 더 작은 schema의 모든 column이 더 큰 schema에 존재해야 함입니다.
`HasCol`이 실패할 수 없는 단일 column lookup을 row에 작성하는 것을 가능하게 만들듯이, indexed family로서의 subschema 관계의 표현은 실패할 수 없는 projection function을 작성하는 것을 가능하게 만듭니다.

The ways in which one schema can be a subschema of another can be defined as an indexed family.
The basic idea is that a smaller schema is a subschema of a bigger schema if every column in the smaller schema occurs in the bigger schema.
If the smaller schema is empty, then it's certainly a subschema of the bigger schema, represented by the constructor `nil`.
If the smaller schema has a column, then that column must be in the bigger schema, and all the rest of the columns in the subschema must also be a subschema of the bigger schema.
This is represented by the constructor `cons`.

한 schema가 다른 schema의 subschema가 되는 방식은 indexed family로 정의할 수 있습니다.
기본 아이디어는 더 작은 schema가 더 큰 schema의 subschema인 경우는 더 작은 schema의 모든 column이 더 큰 schema에 나타날 때입니다.
더 작은 schema가 비어 있다면, 그것은 확실히 더 큰 schema의 subschema이며, constructor `nil`로 표현됩니다.
더 작은 schema가 column을 가지고 있다면, 그 column은 더 큰 schema에 있어야 하고, subschema의 나머지 모든 column도 더 큰 schema의 subschema여야 합니다.
이는 constructor `cons`로 표현됩니다.

```lean
inductive Subschema : Schema → Schema → Type where
  | nil : Subschema [] bigger
  | cons :
    HasCol bigger n t →
    Subschema smaller bigger →
    Subschema (⟨n, t⟩ :: smaller) bigger
```

In other words, `Subschema` assigns each column of the smaller schema a `HasCol` that points to its location in the larger schema.

다시 말해, `Subschema`는 더 작은 schema의 각 column에 더 큰 schema의 위치를 가리키는 `HasCol`을 할당합니다.

The schema `travelDiary` represents the fields that are common to both `peak` and `waterfall`:

schema `travelDiary`는 `peak`과 `waterfall` 모두에 공통인 field를 나타냅니다.

```lean
abbrev travelDiary : Schema :=
  [⟨"name", .string⟩, ⟨"location", .string⟩, ⟨"lastVisited", .int⟩]
```

It is certainly a subschema of `peak`, as shown by this example:

그것은 확실히 `peak`의 subschema입니다. 이 예제에서 보여지듯이:

```lean
example : Subschema travelDiary peak :=
  .cons .here
  (.cons (.there .here)
  (.cons (.there (.there (.there .here))) .nil))
```

However, code like this is difficult to read and difficult to maintain.
One way to improve it is to instruct Lean to write the `Subschema` and `HasCol` constructors automatically.
This can be done using the tactic feature that was introduced in [the Interlude on propositions and proofs](Interlude___-Propositions___-Proofs___-and-Indexing/#props-proofs-indexing).
That interlude uses `by decide` and `by simp` to provide evidence of various propositions.

하지만 이와 같은 코드는 읽기 어렵고 유지하기 어렵습니다.
개선하는 한 가지 방법은 Lean이 `Subschema`와 `HasCol` constructor를 자동으로 작성하도록 지시하는 것입니다.
이는 [proposition과 proof에 대한 Interlude](Interlude___-Propositions___-Proofs___-and-Indexing/#props-proofs-indexing)에서 소개된 tactic feature를 사용하여 수행할 수 있습니다.
해당 interlude는 다양한 proposition의 evidence를 제공하기 위해 `by decide`와 `by simp`를 사용합니다.

In this context, two tactics are useful:

* The `constructor` tactic instructs Lean to solve the problem using the constructor of a datatype.
* The `repeat` tactic instructs Lean to repeat a tactic over and over until it either fails or the proof is finished.

In the next example, `by constructor` has the same effect as just writing `.nil` would have:

```lean
example : Subschema [] peak := by
  constructor
```

```
⊢ Subschema [] peak
constructor
All goals completed! 🐙
```

However, attempting that same tactic with a slightly more complicated type fails:

```lean
example : Subschema [⟨"location", .string⟩] peak := by
  constructor
```

```
unsolved goals
a⊢ HasCol peak "location" DBType.string

a⊢ Subschema [] peak
```

Errors that begin with `unsolved goals` describe tactics that failed to completely build the expressions that they were supposed to.
In Lean's tactic language, a *goal* is a type that a tactic is to fulfill by constructing an appropriate expression behind the scenes.
In this case, `constructor` caused `Subschema.cons` to be applied, and the two goals represent the two arguments expected by `cons`.
Adding another instance of `constructor` causes the first goal (`HasCol peak "location" DBType.string`) to be addressed with `HasCol.there`, because `peak`'s first column is not `"location"`:

`unsolved goals`로 시작하는 오류는 완전히 구축해야 할 expression을 완전히 구축하지 못한 tactic을 설명합니다.
Lean의 tactic language에서, *goal*은 tactic이 뒤에서 적절한 expression을 구성하여 충족해야 하는 type입니다.
이 경우, `constructor`는 `Subschema.cons`를 적용하게 했고, 두 개의 goal은 `cons`에 의해 예상되는 두 개의 인자를 나타냅니다.
`constructor`의 또 다른 instance를 추가하면 첫 번째 goal (`HasCol peak "location" DBType.string`)이 `HasCol.there`로 처리되게 하는데, 이는 `peak`의 첫 번째 column이 `"location"`이 아니기 때문입니다.

```lean
example : Subschema [⟨"location", .string⟩] peak := by
  constructor
  constructor
```

```
unsolved goals
a.a⊢ HasCol
  [{ name := "location", contains := DBType.string }, { name := "elevation", contains := DBType.int },
    { name := "lastVisited", contains := DBType.int }]
  "location" DBType.string

a⊢ Subschema [] peak
```

However, adding a third `constructor` results in the first goal being solved, because `HasCol.here` is applicable:

```lean
example : Subschema [⟨"location", .string⟩] peak := by
  constructor
  constructor
  constructor
```

```
unsolved goals
a⊢ Subschema [] peak
```

A fourth instance of `constructor` solves the `Subschema peak []` goal:

```lean
example : Subschema [⟨"location", .string⟩] peak := by
  constructor
  constructor
  constructor
  constructor
```

```
All goals completed! 🐙
```

Indeed, a version written without the use of tactics has four constructors:

```lean
example : Subschema [⟨"location", .string⟩] peak :=
  .cons (.there .here) .nil
```

Instead of experimenting to find the right number of times to write `constructor`, the `repeat` tactic can be used to ask Lean to just keep trying `constructor` as long as it keeps making progress:

```lean
example : Subschema [⟨"location", .string⟩] peak := by
  repeat constructor
```

```
All goals completed! 🐙
```

This more flexible version also works for more interesting `Subschema` problems:

```lean
example : Subschema travelDiary peak := by
  repeat constructor

example : Subschema travelDiary waterfall := by
  repeat constructor
```

```
All goals completed! 🐙
```

The approach of blindly trying constructors until something works is not very useful for types like `Nat` or `List Bool`.
Just because an expression has type `Nat` doesn't mean that it's the *correct* `Nat`, after all.
But types like `HasCol` and `Subschema` are sufficiently constrained by their indices that only one constructor will ever be applicable, which means that the contents of the program itself are less interesting, and a computer can pick the correct one.

뭔가 작동할 때까지 blind하게 constructor를 시도하는 접근 방식은 `Nat`이나 `List Bool`과 같은 type에 대해서는 그리 유용하지 않습니다.
expression이 `Nat` type을 가진다고 해서 그것이 *correct* `Nat`이라는 의미는 아니기 때문입니다.
하지만 `HasCol`과 `Subschema`와 같은 type은 자신의 index에 의해 충분히 제한되어 있으므로 오직 하나의 constructor만 항상 적용 가능하며, 이는 프로그램 자체의 내용이 덜 흥미롭다는 것을 의미하고, 컴퓨터가 올바른 것을 선택할 수 있습니다.

If one schema is a subschema of another, then it is also a subschema of the larger schema extended with an additional column.
This fact can be captured as a function definition.
`Subschema.addColumn` takes evidence that `smaller` is a subschema of `bigger`, and then returns evidence that `smaller` is a subschema of `c :: bigger`, that is, `bigger` with one additional column:

만약 한 schema가 다른 schema의 subschema라면, 그것은 또한 추가 column으로 확장된 더 큰 schema의 subschema입니다.
이 사실은 function definition으로 캡처될 수 있습니다.
`Subschema.addColumn`은 `smaller`이 `bigger`의 subschema임을 나타내는 evidence를 받고, `smaller`이 `c :: bigger` 즉, 추가 column이 있는 `bigger`의 subschema임을 나타내는 evidence를 반환합니다.

```lean
def Subschema.addColumn :
    Subschema smaller bigger →
    Subschema smaller (c :: bigger)
  | .nil => .nil
  | .cons col sub' => .cons (.there col) sub'.addColumn
```

A subschema describes where to find each column from the smaller schema in the larger schema.
`Subschema.addColumn` must translate these descriptions from the original larger schema into the extended larger schema.
In the `nil` case, the smaller schema is `[]`, and `nil` is also evidence that `[]` is a subschema of `c :: bigger`.
In the `cons` case, which describes how to place one column from `smaller` into `bigger`, the placement of the column needs to be adjusted with `there` to account for the new column `c`, and a recursive call adjusts the rest of the columns.

subschema는 더 작은 schema의 각 column을 더 큰 schema에서 어디서 찾을지를 설명합니다.
`Subschema.addColumn`은 원본 더 큰 schema에서 확장된 더 큰 schema로 이러한 설명을 변환해야 합니다.
`nil` case에서 더 작은 schema는 `[]`이고, `nil`은 또한 `[]`이 `c :: bigger`의 subschema임을 나타내는 evidence입니다.
`smaller`에서 하나의 column을 `bigger`에 배치하는 방법을 설명하는 `cons` case에서, column의 배치는 새로운 column `c`를 계정하기 위해 `there`로 조정되어야 하고, recursive call은 나머지 column을 조정합니다.

Another way to think about `Subschema` is that it defines a *relation* between two schemas—the existence of an expression with type `Subschema smaller bigger` means that `(smaller, bigger)` is in the relation.
This relation is reflexive, meaning that every schema is a subschema of itself:

`Subschema`를 생각하는 또 다른 방법은 두 schema 사이의 *relation*을 정의한다는 것입니다. `Subschema smaller bigger` type을 가진 expression의 존재는 `(smaller, bigger)`이 relation에 있다는 것을 의미합니다.
이 relation은 reflexive이며, 즉, 모든 schema가 자신의 subschema임입니다.

```lean
def Subschema.reflexive : (s : Schema) → Subschema s s
  | [] => .nil
  | _ :: cs => .cons .here (reflexive cs).addColumn
```

### 7.3.2.4. Projecting Rows

Given evidence that `s'` is a subschema of `s`, a row in `s` can be projected into a row in `s'`.
This is done using the evidence that `s'` is a subschema of `s`, which explains where each column of `s'` is found in `s`.
The new row in `s'` is built up one column at a time by retrieving the value from the appropriate place in the old row.

`s'`이 `s`의 subschema임을 나타내는 evidence가 주어지면, `s`의 row를 `s'`의 row로 project할 수 있습니다.
이는 `s'`이 `s`의 subschema임을 나타내는 evidence를 사용하여 수행되며, 이는 `s'`의 각 column이 `s`에서 어디서 발견되는지를 설명합니다.
`s'`의 새로운 row는 이전 row의 적절한 위치에서 값을 검색하여 한 번에 하나의 column씩 구축됩니다.

The function that performs this projection, `Row.project`, has three cases, one for each case of `Row` itself.
It uses `Row.get` together with each `HasCol` in the `Subschema` argument to construct the projected row:

이 projection을 수행하는 function `Row.project`는 `Row` 자체의 각 경우에 대해 하나씩 세 가지 case를 가집니다.
이는 projected row를 구성하기 위해 `Row.get`을 `Subschema` 인자의 각 `HasCol`과 함께 사용합니다.

```lean
def Row.project (row : Row s) : (s' : Schema) → Subschema s' s → Row s'
  | [], .nil => ()
  | [_], .cons c .nil => row.get c
  | _::_::_, .cons c cs => (row.get c, row.project _ cs)
```

## 7.3.3. Conditions and Selection

Projection removes unwanted columns from a table, but queries must also be able to remove unwanted rows.
This operation is called *selection*.
Selection relies on having a means of expressing which rows are desired.

Projection은 table에서 원하지 않는 column을 제거하지만, query는 원하지 않는 row도 제거할 수 있어야 합니다.
이 operation을 *selection*이라고 합니다.
Selection은 어떤 row가 원하는지를 표현할 수 있는 수단을 가지는 것에 의존합니다.

The example query language contains expressions, which are analogous to what can be written in a `WHERE` clause in SQL.
Expressions are represented by the indexed family `DBExpr`.
Because expressions can refer to columns from the database, but different sub-expressions all have the same schema, `DBExpr` takes the database schema as a parameter.
Additionally, each expression has a type, and these vary, making it an index:

예제 query language는 SQL의 `WHERE` clause에 쓸 수 있는 것과 유사한 expression을 포함합니다.
Expression은 indexed family `DBExpr`로 표현됩니다.
expression은 데이터베이스의 column을 참조할 수 있지만, 서로 다른 sub-expression은 모두 동일한 schema를 가지기 때문에, `DBExpr`은 database schema를 parameter로 취합니다.
또한, 각 expression은 type을 가지고 있으며, 이들이 다르므로 index가 됩니다.

```lean
inductive DBExpr (s : Schema) : DBType → Type where
  | col (n : String) (loc : HasCol s n t) : DBExpr s t
  | eq (e1 e2 : DBExpr s t) : DBExpr s .bool
  | lt (e1 e2 : DBExpr s .int) : DBExpr s .bool
  | and (e1 e2 : DBExpr s .bool) : DBExpr s .bool
  | const : t.asType → DBExpr s t
```

The `col` constructor represents a reference to a column in the database.
The `eq` constructor compares two expressions for equality, `lt` checks whether one is less than the other, `and` is Boolean conjunction, and `const` is a constant value of some type.

`col` constructor는 데이터베이스의 column에 대한 참조를 나타냅니다.
`eq` constructor는 두 expression을 동등성에 대해 비교하고, `lt`는 하나가 다른 것보다 작은지 확인하며, `and`는 Boolean conjunction이고, `const`는 어떤 type의 상수 값입니다.

For example, an expression in `peak` that checks whether the `elevation` column is greater than 1000 and the location is `"Denmark"` can be written:

예를 들어, `peak`의 `elevation` column이 1000보다 크고 location이 `"Denmark"`인지 확인하는 expression은 다음과 같이 작성할 수 있습니다.

```lean
def tallInDenmark : DBExpr peak .bool :=
  .and (.lt (.const 1000) (.col "elevation" (by repeat constructor)))
       (.eq (.col "location" (by repeat constructor)) (.const "Denmark"))
```

This is somewhat noisy.
In particular, references to columns contain boilerplate calls to `by repeat constructor`.
A Lean feature called *macros* can help make expressions easier to read by eliminating this boilerplate:

이것은 다소 noisy합니다.
특히, column에 대한 참조는 `by repeat constructor`에 대한 boilerplate 호출을 포함합니다.
*macros*라는 Lean feature는 이 boilerplate을 제거하여 expression을 읽기 쉽게 만드는 데 도움이 될 수 있습니다.

```lean
macro "c!" n:term : term => `(DBExpr.col $n (by repeat constructor))
```

This declaration adds the `c!` keyword to Lean, and instructs Lean to replace any instance of `c!` followed by an expression with the corresponding `DBExpr.col` construction.
Here, `term` stands for Lean expressions, rather than commands, tactics, or some other part of the language.
Lean macros are a bit like C preprocessor macros, except they are better integrated into the language and they automatically avoid some of the pitfalls of CPP.
In fact, they are very closely related to macros in Scheme and Racket.

이 declaration은 `c!` keyword를 Lean에 추가하고, Lean이 `c!` 뒤에 오는 expression의 모든 instance를 해당하는 `DBExpr.col` construction으로 바꾸도록 지시합니다.
여기서 `term`은 command, tactic, 또는 language의 다른 부분이 아닌 Lean expression을 나타냅니다.
Lean macro는 C preprocessor macro와 좀 비슷한데, language에 더 잘 통합되어 있고 CPP의 pitfall 중 일부를 자동으로 피합니다.
실제로, 그들은 Scheme과 Racket의 macro와 매우 밀접하게 관련되어 있습니다.

With this macro, the expression can be much easier to read:

```lean
def tallInDenmark : DBExpr peak .bool :=
  .and (.lt (.const 1000) (c! "elevation"))
       (.eq (c! "location") (.const "Denmark"))
```

Finding the value of an expression with respect to a given row uses `Row.get` to extract column references, and it delegates to Lean's operations on values for every other expression:

주어진 row에 대한 expression의 값을 찾는 것은 column 참조를 추출하기 위해 `Row.get`을 사용하고, 다른 모든 expression에 대해 Lean의 operation에 위임합니다.

```lean
def DBExpr.evaluate (row : Row s) : DBExpr s t → t.asType
  | .col _ loc => row.get loc
  | .eq e1 e2 => evaluate row e1 == evaluate row e2
  | .lt e1 e2 => evaluate row e1 < evaluate row e2
  | .and e1 e2 => evaluate row e1 && evaluate row e2
  | .const v => v
```

Evaluating the expression for Valby Bakke, the tallest hill in the Copenhagen area, yields `false` because Valby Bakke is much less than 1 km over sea level:

Copenhagen 지역의 가장 높은 언덕인 Valby Bakke에 대한 expression을 평가하면 `false`를 생성합니다. Valby Bakke는 해수면 위로 1km보다 훨씬 작기 때문입니다.

```lean
#eval tallInDenmark.evaluate ("Valby Bakke", "Denmark", 31, 2023)
```

```
false
```

Evaluating it for a fictional mountain of 1230m elevation yields `true`:

1230m elevation을 가진 fictional mountain에 대해 평가하면 `true`를 생성합니다.

```lean
#eval tallInDenmark.evaluate ("Fictional mountain", "Denmark", 1230, 2023)
```

```
true
```

Evaluating it for the highest peak in the US state of Idaho yields `false`, as Idaho is not part of Denmark:

미국 Idaho 주의 가장 높은 봉우리에 대해 평가하면 `false`를 생성합니다. Idaho는 Denmark의 일부가 아니기 때문입니다.

```lean
#eval tallInDenmark.evaluate ("Mount Borah", "USA", 3859, 1996)
```

```
false
```

## 7.3.5. Executing Queries

Executing queries requires a number of helper functions.
The result of a query is a table; this means that each operation in the query language requires a corresponding implementation that works with tables.

Query를 실행하려면 여러 helper function이 필요합니다.
query의 결과는 table입니다. 즉, query language의 각 operation이 table과 함께 작동하는 해당 implementation을 필요로 함입니다.

### 7.3.5.1. Cartesian Product

Taking the Cartesian product of two tables is done by appending each row from the first table to each row from the second.
First off, due to the structure of `Row`, adding a single column to a row requires pattern matching on its schema in order to determine whether the result will be a bare value or a tuple.
Because this is a common operation, factoring the pattern matching out into a helper is convenient:

두 table의 Cartesian product를 취하는 것은 첫 번째 table의 각 row를 두 번째 table의 각 row에 추가하여 수행됩니다.
우선, `Row`의 구조로 인해, row에 단일 column을 추가하려면 결과가 bare value인지 tuple인지를 결정하기 위해 schema에서 pattern matching이 필요합니다.
이것이 일반적인 operation이므로, pattern matching을 helper로 factor out하는 것이 편합니다.

```lean
def addVal (v : c.contains.asType) (row : Row s) : Row (c :: s) :=
  match s, row with
  | [], () => v
  | c' :: cs, v' => (v, v')
```

Appending two rows is recursive on the structure of both the first schema and the first row, because the structure of the row proceeds in lock-step with the structure of the schema.
When the first row is empty, appending returns the second row.
When the first row is a singleton, the value is added to the second row.
When the first row contains multiple columns, the first column's value is added to the result of recursion on the remainder of the row.

두 row를 append하는 것은 첫 번째 schema의 구조와 첫 번째 row의 구조 모두에 recursive이며, 이는 row의 구조가 schema의 구조와 lock-step으로 진행되기 때문입니다.
첫 번째 row가 비어 있으면, appending은 두 번째 row를 반환합니다.
첫 번째 row가 singleton이면, 값이 두 번째 row에 추가됩니다.
첫 번째 row가 여러 column을 포함하면, 첫 번째 column의 값이 row의 나머지에 대한 recursion의 결과에 추가됩니다.

```lean
def Row.append (r1 : Row s1) (r2 : Row s2) : Row (s1 ++ s2) :=
  match s1, r1 with
  | [], () => r2
  | [_], v => addVal v r2
  | _::_::_, (v, r') => (v, r'.append r2)
```

`List.flatMap`, found in the standard library, applies a function that itself returns a list to every entry in an input list, returning the result of appending the resulting lists in order:

standard library에서 찾을 수 있는 `List.flatMap`은 자신이 list를 반환하는 function을 input list의 모든 entry에 적용하며, 결과 list를 순서대로 append한 결과를 반환합니다.

```lean
def List.flatMap (f : α → List β) : (xs : List α) → List β
  | [] => []
  | x :: xs => f x ++ xs.flatMap f
```

The type signature suggests that `List.flatMap` could be used to implement a `Monad List` instance.
Indeed, together with `pure x := [x]`, `List.flatMap` does implement a monad.
However, it's not a very useful `Monad` instance.
The `List` monad is basically a version of `Many` that explores *every* possible path through the search space in advance, before users have the chance to request some number of values.
Because of this performance trap, it's usually not a good idea to define a `Monad` instance for `List`.
Here, however, the query language has no operator for restricting the number of results to be returned, so combining all possibilities is exactly what is desired:

type signature는 `List.flatMap`이 `Monad List` instance를 구현하는 데 사용될 수 있음을 시사합니다.
실제로, `pure x := [x]`와 함께, `List.flatMap`은 monad를 구현합니다.
그러나 이것은 매우 유용한 `Monad` instance가 아닙니다.
`List` monad는 기본적으로 user가 얼마나 많은 값을 요청할 기회를 가지기 전에 search space를 통한 *모든* 가능한 경로를 미리 탐색하는 `Many`의 버전입니다.
이 performance trap으로 인해, 일반적으로 `List`에 대해 `Monad` instance를 정의하는 것은 좋지 않습니다.
하지만 여기서는, query language는 반환될 결과의 수를 제한하기 위한 operator가 없으므로, 모든 가능성을 결합하는 것이 정확히 원하는 것입니다.

```lean
def Table.cartesianProduct (table1 : Table s1) (table2 : Table s2) :
    Table (s1 ++ s2) :=
  table1.flatMap fun r1 => table2.map r1.append
```

Just as with `List.product`, a loop with mutation in the identity monad can be used as an alternative implementation technique:

`List.product`와 마찬가지로, identity monad의 mutation을 가진 loop을 alternative implementation technique으로 사용할 수 있습니다.

```lean
def Table.cartesianProduct (table1 : Table s1) (table2 : Table s2) :
    Table (s1 ++ s2) := Id.run do
  let mut out : Table (s1 ++ s2) := []
  for r1 in table1 do
    for r2 in table2 do
      out := (r1.append r2) :: out
  pure out.reverse
```

### 7.3.5.2. Difference

Removing undesired rows from a table can be done using `List.filter`, which takes a list and a function that returns a `Bool`.
A new list is returned that contains only the entries for which the function returns `true`.
For instance,

table에서 원하지 않는 row를 제거하는 것은 `List.filter`를 사용하여 수행할 수 있으며, 이는 list와 `Bool`을 반환하는 function을 취합니다.
함수가 `true`를 반환하는 entry만 포함하는 새로운 list가 반환됩니다.
예를 들어,

```lean
["Willamette", "Columbia", "Sandy", "Deschutes"].filter (·.length > 8)
```

evaluates to

```
["Willamette", "Deschutes"]
```

because `"Columbia"` and `"Sandy"` have lengths less than or equal to `8`.
Removing the entries of a table can be done using the helper `List.without`:

`"Columbia"`과 `"Sandy"`는 길이가 `8` 이하이기 때문입니다.
table의 entry를 제거하는 것은 helper `List.without`을 사용하여 수행할 수 있습니다.

```lean
def List.without [BEq α] (source banned : List α) : List α :=
  source.filter fun r => !(banned.contains r)
```

This will be used with the `BEq` instance for `Row` when interpreting queries.

이것은 query를 해석할 때 `Row`에 대한 `BEq` instance와 함께 사용될 것입니다.

### 7.3.5.3. Renaming Columns

Renaming a column in a row is done with a recursive function that traverses the row until the column in question is found, at which point the column with the new name gets the same value as the column with the old name:

row의 column을 rename하는 것은 문제의 column이 발견될 때까지 row를 traverse하는 recursive function으로 수행되며, 이 시점에서 새로운 name을 가진 column은 이전 name을 가진 column과 동일한 값을 얻습니다.

```lean
def Row.rename (c : HasCol s n t) (row : Row s) :
    Row (s.renameColumn c n') :=
  match s, row, c with
  | [_], v, .here => v
  | _::_::_, (v, r), .here => (v, r)
  | _::_::_, (v, r), .there next => addVal v (r.rename next)
```

While this function changes the *type* of its argument, the actual return value contains precisely the same data as the original argument.
From a run-time perspective, `Row.rename` is nothing but a slow identity function.
One difficulty in programming with indexed families is that when performance matters, this kind of operation can get in the way.
It takes a very careful, often brittle, design to eliminate these kinds of “re-indexing” functions.

이 function은 자신의 인자의 *type*을 변경하지만, 실제 return value는 원래 인자와 정확히 동일한 data를 포함합니다.
run-time 관점에서, `Row.rename`은 단지 느린 identity function입니다.
indexed family로 프로그래밍할 때의 한 가지 어려움은 performance가 중요할 때 이런 종류의 operation이 방해가 될 수 있다는 것입니다.
이러한 종류의 “re-indexing” function을 제거하려면 매우 신중한, 종종 취약한, 설계가 필요합니다.

### 7.3.5.4. Prefixing Column Names

Adding a prefix to column names is very similar to renaming a column.
Instead of proceeding to a desired column and then returning, `prefixRow` must process all columns:

column name에 prefix를 추가하는 것은 column을 rename하는 것과 매우 유사합니다.
원하는 column으로 진행한 후 반환하는 대신, `prefixRow`는 모든 column을 처리해야 합니다.

```lean
def prefixRow (row : Row s) :
    Row (s.map fun c => {c with name := n ++ "." ++ c.name}) :=
  match s, row with
  | [], _ => ()
  | [_], v => v
  | _::_::_, (v, r) => (v, prefixRow r)
```

This can be used with `List.map` in order to add a prefix to all rows in a table.
Once again, this function only exists to change the type of a value.

이것은 table의 모든 row에 prefix를 추가하기 위해 `List.map`과 함께 사용될 수 있습니다.
다시 말해, 이 function은 value의 type을 변경하기 위해서만 존재합니다.

### 7.3.5.5. Putting the Pieces Together

With all of these helpers defined, executing a query requires only a short recursive function:

이 모든 helper가 정의되면, query를 실행하려면 단지 짧은 recursive function이 필요합니다.

```lean
def Query.exec : Query s → Table s
  | .table t => t
  | .union q1 q2 => exec q1 ++ exec q2
  | .diff q1 q2 => exec q1 |>.without (exec q2)
  | .select q e => exec q |>.filter e.evaluate
  | .project q _ sub => exec q |>.map (·.project _ sub)
  | .product q1 q2 _ => exec q1 |>.cartesianProduct (exec q2)
  | .renameColumn q c _ _ => exec q |>.map (·.rename c)
  | .prefixWith _ q => exec q |>.map prefixRow
```

Some arguments to the constructors are not used during execution.
In particular, both the constructor `project` and the function `Row.project` take the smaller schema as explicit arguments, but the type of the *evidence* that this schema is a subschema of the larger schema contains enough information for Lean to fill out the argument automatically.
Similarly, the fact that the two tables have disjoint column names that is required by the `product` constructor is not needed by `Table.cartesianProduct`.
Generally speaking, dependent types provide many opportunities to have Lean fill out arguments on behalf of the programmer.

constructor에 대한 일부 인자는 execution 중에 사용되지 않습니다.
특히, constructor `project`와 function `Row.project` 모두 더 작은 schema를 explicit argument로 취하지만, 이 schema가 더 큰 schema의 subschema임을 나타내는 *evidence*의 type은 Lean이 인자를 자동으로 채우기에 충분한 정보를 포함합니다.
유사하게, `product` constructor에 의해 요구되는 두 table이 disjoint column name을 가진다는 사실은 `Table.cartesianProduct`에 의해 필요하지 않습니다.
일반적으로, dependent type은 Lean이 programmer를 대신하여 argument를 채울 수 있는 많은 기회를 제공합니다.

Dot notation is used with the results of queries to call functions defined both in the `Table` and `List` namespaces, such `List.map`, `List.filter`, and `Table.cartesianProduct`.
This works because `Table` is defined using `abbrev`.
Just like type class search, dot notation can see through definitions created with `abbrev`.

Dot notation은 query의 결과와 함께 `Table`과 `List` namespace 모두에서 정의된 function을 호출하기 위해 사용되며, 예를 들어 `List.map`, `List.filter`, `Table.cartesianProduct`입니다.
이것은 `Table`이 `abbrev`를 사용하여 정의되기 때문에 작동합니다.
type class search처럼, dot notation은 `abbrev`로 생성된 정의를 볼 수 있습니다.

The implementation of `select` is also quite concise.
After executing the query `q`, `List.filter` is used to remove the rows that do not satisfy the expression.
`List.filter` expects a function from `Row s` to `Bool`, but `DBExpr.evaluate` has type `Row s → DBExpr s t → t.asType`.
Because the type of the `select` constructor requires that the expression have type `DBExpr s .bool`, `t.asType` is actually `Bool` in this context.

`select`의 implementation도 매우 간결합니다.
query `q`를 실행한 후, `List.filter`는 expression을 만족하지 않는 row를 제거하기 위해 사용됩니다.
`List.filter`는 `Row s`에서 `Bool`로의 function을 기대하지만, `DBExpr.evaluate`는 `Row s → DBExpr s t → t.asType` type을 가집니다.
`select` constructor의 type이 expression이 `DBExpr s .bool` type을 가지도록 요구하기 때문에, `t.asType`은 실제로 이 문맥에서 `Bool`입니다.

A query that finds the heights of all mountain peaks with an elevation greater than 500 meters can be written:

elevation이 500미터 이상인 모든 산봉우리의 높이를 찾는 query는 다음과 같이 작성할 수 있습니다.

```lean
open Query in
def example1 :=
  table mountainDiary |>.select
    (.lt (.const 500) (c! "elevation")) |>.project
    [⟨"elevation", .int⟩] (by repeat constructor)
```

Executing it returns the expected list of integers:

```lean
#eval example1.exec
```

```
[3637, 1519, 2549]
```

To plan a sightseeing tour, it may be relevant to match all pairs mountains and waterfalls in the same location.
This can be done by taking the Cartesian product of both tables, selecting only the rows in which they are equal, and then projecting out the names:

관광 여행을 계획하기 위해, 같은 위치의 모든 산과 폭포 쌍을 일치시키는 것이 관련이 있을 수 있습니다.
이것은 두 table의 Cartesian product를 취하고, 그들이 같은 row만 선택하며, 그 다음 name을 project out하여 수행할 수 있습니다.

```lean
open Query in
def example2 :=
  let mountain := table mountainDiary |>.prefixWith "mountain"
  let waterfall := table waterfallDiary |>.prefixWith "waterfall"
  mountain.product waterfall (by decide)
    |>.select (.eq (c! "mountain.location") (c! "waterfall.location"))
    |>.project [⟨"mountain.name", .string⟩, ⟨"waterfall.name", .string⟩]
      (by repeat constructor)
```

Because the example data includes only waterfalls in the USA, executing the query returns pairs of mountains and waterfalls in the US:

예제 data가 USA의 폭포만 포함하기 때문에, query를 실행하면 US의 산과 폭포 쌍이 반환됩니다.

```lean
#eval example2.exec
```

```
[("Mount Nebo", "Multnomah Falls"), ("Mount Nebo", "Shoshone Falls"), ("Moscow Mountain", "Multnomah Falls"),
  ("Moscow Mountain", "Shoshone Falls"), ("Mount St. Helens", "Multnomah Falls"),
  ("Mount St. Helens", "Shoshone Falls")]
```

### 7.3.5.6. Errors You May Meet

Many potential errors are ruled out by the definition of `Query`.
For instance, forgetting the added qualifier in `"mountain.location"` yields a compile-time error that highlights the column reference `c! "location"`:

많은 잠재적 오류가 `Query`의 정의에 의해 배제됩니다.
예를 들어, `"mountain.location"`에서 추가된 qualifier를 잊어버리면 column 참조 `c! "location"`을 강조하는 compile-time error를 생성합니다.

```lean
open Query in
def example2 :=
  let mountains := table mountainDiary |>.prefixWith "mountain"
  let waterfalls := table waterfallDiary |>.prefixWith "waterfall"
  mountains.product waterfalls (by simp)
    |>.select (.eq (c! "location") (c! "waterfall.location"))
    |>.project [⟨"mountain.name", .string⟩, ⟨"waterfall.name", .string⟩]
      (by repeat constructor)
```

This is excellent feedback!
On the other hand, the text of the error message is quite difficult to act on:

이것은 훌륭한 feedback입니다!
반면에, error message의 text는 행동하기에 꽤 어렵습니다.

```
unsolved goals
a.a.a.a.a.a.amountains:Query (List.map (fun c => { name := "mountain" ++ "." ++ c.name, contains := c.contains }) peak) := ⋯waterfalls:Query (List.map (fun c => { name := "waterfall" ++ "." ++ c.name, contains := c.contains }) waterfall) := ⋯⊢ HasCol (List.map (fun c => { name := "waterfall" ++ "." ++ c.name, contains := c.contains }) []) "location" ?m.31
```

Similarly, forgetting to add prefixes to the names of the two tables results in an error on `by decide`, which should provide evidence that the schemas are in fact disjoint:

유사하게, 두 table의 name에 prefix를 추가하는 것을 잊어버리면 `by decide`에서 error가 발생하며, 이는 schema가 실제로 disjoint임을 나타내는 evidence를 제공해야 합니다.

```lean
open Query in
def example2 :=
  let mountains := table mountainDiary
  let waterfalls := table waterfallDiary
  mountains.product waterfalls (by decide)
    |>.select (.eq (c! "mountain.location") (c! "waterfall.location"))
    |>.project [⟨"mountain.name", .string⟩, ⟨"waterfall.name", .string⟩]
      (by repeat constructor)
```

This error message is more helpful:

이 error message는 더 도움이 됩니다.

```
Tactic `decide` proved that the proposition
  disjoint (List.map Column.name peak) (List.map Column.name waterfall) = true
is false
```

Lean's macro system contains everything needed not only to provide a convenient syntax for queries, but also to arrange for the error messages to be helpful.
Unfortunately, it is beyond the scope of this book to provide a description of implementing languages with Lean macros.
An indexed family such as `Query` is probably best as the core of a typed database interaction library, rather than its user interface.

Lean의 macro system은 query를 위한 편리한 syntax를 제공할 뿐만 아니라 error message가 도움이 되도록 하는 데 필요한 모든 것을 포함합니다.
불행하게도, Lean macro로 language를 구현하는 것에 대한 설명을 제공하는 것은 이 책의 범위를 벗어납니다.
`Query`와 같은 indexed family는 아마도 user interface보다는 typed database interaction library의 core로서 가장 좋습니다.
