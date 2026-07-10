---
title: "6.1. IO와 리더 결합하기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "IO와 리더 결합하기"
---

# 6.1. Combining IO and Reader

One case where a reader monad can be useful is when there is some notion of the “current configuration” of the application that is passed through many recursive calls.
An example of such a program is `tree`, which recursively prints the files in the current directory and its subdirectories, indicating their tree structure using characters.
The version of `tree` in this chapter, called `doug` after the mighty Douglas Fir tree that adorns the west coast of North America, provides the option of Unicode box-drawing characters or their ASCII equivalents when indicating directory structure.

Reader Monad가 유용한 경우 중 하나는 애플리케이션의 “현재 구성”이라는 개념이 많은 재귀 호출을 통해 전달될 때입니다. 그러한 프로그램의 예는 `tree`로, 현재 디렉토리 및 해당 하위 디렉토리의 파일을 재귀적으로 인쇄하며 문자를 사용하여 트리 구조를 나타냅니다. 이 장의 `tree` 버전은 북미 서해안을 장식하는 거대한 Douglas Fir 나무의 이름을 딴 `doug`이며, 디렉토리 구조를 나타낼 때 Unicode 상자 그리기 문자 또는 그에 해당하는 ASCII 문자를 선택할 수 있습니다.

For example, the following commands create a directory structure and some empty files in a directory called `doug-demo`:

```
cd doug-demo
mkdir -p a/b/c
mkdir -p a/d
mkdir -p a/e/f
touch a/b/hello
touch a/d/another-file
touch a/e/still-another-file-again
```

Running `doug` results in the following:

```
doug
```

```
├── doug-demo/
│   ├── a/
│   │   ├── b/
│   │   │   ├── c/
│   │   │   ├── hello
│   │   ├── d/
│   │   │   ├── another-file
│   │   ├── e/
│   │   │   ├── f/
│   │   │   ├── still-another-file-again
```

## 6.1.1. Implementation

Internally, `doug` passes a configuration value downwards as it recursively traverses the directory structure.
This configuration contains two fields: `useASCII` determines whether to use Unicode box-drawing characters or ASCII vertical line and dash characters to indicate structure, and `currentPrefix` contains a string to prepend to each line of output.
As the current directory deepens, the prefix string accumulates indicators of being in a directory.
The configuration is a structure:

내부적으로 `doug`은 디렉토리 구조를 재귀적으로 순회할 때 구성 값을 아래로 전달합니다. 이 구성에는 두 개의 필드가 있습니다: `useASCII`는 구조를 나타낼 때 Unicode 상자 그리기 문자를 사용할지 ASCII 세로 줄과 대시 문자를 사용할지를 결정하고, `currentPrefix`는 출력의 각 줄 앞에 붙일 문자열을 포함합니다. 현재 디렉토리가 깊어질수록 접두사 문자열은 디렉토리에 있다는 표시기를 누적합니다. 구성은 다음과 같은 구조입니다:

```lean
structure Config where
  useASCII : Bool := false
  currentPrefix : String := ""
```

This structure has default definitions for both fields.
The default `Config` uses Unicode display with no prefix.

이 구조는 두 필드 모두에 대한 기본 정의를 가지고 있습니다. 기본 `Config`는 접두사 없이 Unicode 디스플레이를 사용합니다.

Users who invoke `doug` will need to be able to provide command-line arguments.
The usage information is as follows:

`doug`을 호출하는 사용자는 명령줄 인수를 제공할 수 있어야 합니다. 사용 정보는 다음과 같습니다:

```lean
def usage : String :=
  "Usage: doug [--ascii]
Options:
\t--ascii\tUse ASCII characters to display the directory structure"
```

Accordingly, a configuration can be constructed by examining a list of command-line arguments:

`main` 함수는 구성을 사용하여 디렉토리의 내용을 표시하는 `dirTree`라는 내부 작업자 주변의 래퍼입니다. `dirTree`를 호출하기 전에 `main`은 명령줄 인수 처리를 담당합니다. 또한 운영 체제에 적절한 종료 코드를 반환해야 합니다:

```lean
def configFromArgs : List String → Option Config
  | [] => some {} -- both fields default
  | ["--ascii"] => some {useASCII := true}
  | _ => none
```

```lean
def main (args : List String) : IO UInt32 := do
  match configFromArgs args with
  | some config =>
    dirTree config (← IO.currentDir)
    pure 0
  | none =>
    IO.eprintln s!"Didn't understand argument(s) {" ".separate args}\n"
    IO.eprintln usage
    pure 1
```

The `main` function is a wrapper around an inner worker, called `dirTree`, that shows the contents of a directory using a configuration.
Before calling `dirTree`, `main` is responsible for processing command-line arguments.
It must also return the appropriate exit code to the operating system:

`IO.eprintln` is a version of `IO.println` that outputs to standard error.

`IO.eprintln`은 표준 오류로 출력하는 `IO.println`의 버전입니다.

Not all paths should be shown in the directory tree.
In particular, files named `.` or `..` should be skipped, as they are actually features used for navigation rather than files *per se*.
Of those files that should be shown, there are two kinds: ordinary files and directories:

모든 경로가 디렉토리 트리에 표시되어야 하는 것은 아닙니다. 특히 `.` 또는 `..`라는 이름의 파일은 실제로 파일이 아니라 네비게이션에 사용되는 기능이므로 건너뛰어야 합니다. 표시되어야 하는 파일 중에는 일반 파일과 디렉토리의 두 가지 종류가 있습니다:

```lean
inductive Entry where
  | file : String → Entry
  | dir : String → Entry
```

To determine whether a file should be shown, along with which kind of entry it is, `doug` uses `toEntry`:

파일을 표시할지 여부와 어떤 종류의 항목인지 결정하기 위해 `doug`은 `toEntry`를 사용합니다:

```lean
def toEntry (path : System.FilePath) : IO (Option Entry) := do
  match path.components.getLast? with
  | none => pure (some (.dir ""))
  | some "." | some ".." => pure none
  | some name =>
    pure (some (if (← path.isDir) then .dir name else .file name))
```

`System.FilePath.components` converts a path into a list of path components, splitting the name at directory separators.
If there is no last component, then the path is the root directory.
If the last component is a special navigation file (`.` or `..`), then the file should be excluded.
Otherwise, directories and files are wrapped in the corresponding constructors.

`System.FilePath.components`는 경로를 경로 구성 요소 목록으로 변환하여 디렉토리 구분자에서 이름을 분할합니다. 마지막 구성 요소가 없으면 경로는 루트 디렉토리입니다. 마지막 구성 요소가 특수 네비게이션 파일(`.` 또는 `..`)인 경우 파일을 제외해야 합니다. 그렇지 않으면 디렉토리와 파일이 해당 생성자로 래핑됩니다.

Lean's logic has no way to know that directory trees are finite.
Indeed, some systems allow the construction of circular directory structures.
Thus, `dirTree` is declared `partial`:

Lean의 로직은 디렉토리 트리가 유한하다는 것을 알 수 있는 방법이 없습니다. 실제로 일부 시스템은 원형 디렉토리 구조의 구성을 허용합니다. 따라서 `dirTree`는 `partial`로 선언됩니다:

```lean
partial def dirTree (cfg : Config) (path : System.FilePath) : IO Unit := do
  match ← toEntry path with
  | none => pure ()
  | some (.file name) => showFileName cfg name
  | some (.dir name) =>
    showDirName cfg name
    let contents ← path.readDir
    let newConfig := cfg.inDirectory
    doList (contents.qsort dirLT).toList fun d =>
      dirTree newConfig d.path
```

The call to `toEntry` is a [nested action](../ch02/)—the parentheses are optional in positions where the arrow couldn't have any other meaning, such as `match`.
When the filename doesn't correspond to an entry in the tree (e.g. because it is `..`), `dirTree` does nothing.
When the filename points to an ordinary file, `dirTree` calls a helper to show it with the current configuration.
When the filename points to a directory, it is shown with a helper, and then its contents are recursively shown in a new configuration in which the prefix has been extended to account for being in a new directory.
The contents of the directory are sorted in order to make the output deterministic, compared according to `dirLT`.

`toEntry`에 대한 호출은 [중첩된 액션](../ch02/)입니다. 괄호는 `match`와 같이 화살표가 다른 의미를 가질 수 없는 위치에서 선택 사항입니다. 파일 이름이 트리의 항목에 해당하지 않을 때 (예: `..`이기 때문에), `dirTree`는 아무것도 하지 않습니다. 파일 이름이 일반 파일을 가리킬 때 `dirTree`는 현재 구성으로 표시할 도우미를 호출합니다. 파일 이름이 디렉토리를 가리킬 때 도우미로 표시되고, 그 내용은 새 디렉토리에 있음을 설명하기 위해 접두사가 확장된 새로운 구성에서 재귀적으로 표시됩니다. 디렉토리의 내용은 출력을 결정적으로 만들기 위해 정렬되며 `dirLT`에 따라 비교됩니다.

```lean
def dirLT (e1 : IO.FS.DirEntry) (e2 : IO.FS.DirEntry) : Bool :=
  e1.fileName < e2.fileName
```

Showing the names of files and directories is achieved with `showFileName` and `showDirName`:

파일 및 디렉토리 이름을 표시하는 것은 `showFileName` 및 `showDirName`으로 달성됩니다:

```lean
def showFileName (cfg : Config) (file : String) : IO Unit := do
  IO.println (cfg.fileName file)
def showDirName (cfg : Config) (dir : String) : IO Unit := do
  IO.println (cfg.dirName dir)
```

Both of these helpers delegate to functions on `Config` that take the ASCII vs Unicode setting into account:

이 두 도우미 모두 ASCII 대 Unicode 설정을 고려하는 `Config`의 함수에 위임합니다:

```lean
def Config.preFile (cfg : Config) :=
  if cfg.useASCII then "|--" else "├──"
def Config.preDir (cfg : Config) :=
  if cfg.useASCII then "| " else "│ "
def Config.fileName (cfg : Config) (file : String) : String :=
  s!"{cfg.currentPrefix}{cfg.preFile} {file}"
def Config.dirName (cfg : Config) (dir : String) : String :=
  s!"{cfg.currentPrefix}{cfg.preFile} {dir}/"
```

Similarly, `Config.inDirectory` extends the prefix with a directory marker:

유사하게 `Config.inDirectory`는 디렉토리 마커로 접두사를 확장합니다:

```lean
def Config.inDirectory (cfg : Config) : Config :=
  {cfg with currentPrefix := cfg.preDir ++ " " ++ cfg.currentPrefix}
```

Iterating an IO action over a list of directory contents is achieved using `doList`.
Because `doList` carries out all the actions in a list and does not base control-flow decisions on the values returned by any of the actions, the full power of `Monad` is not necessary, and it will work for any `Applicative`:

디렉토리 내용 목록에 대해 IO 작업을 반복하는 것은 `doList`를 사용하여 달성됩니다. `doList`는 목록의 모든 작업을 수행하고 어떤 작업이든 반환 값을 기반으로 제어 흐름 결정을 하지 않으므로 `Monad`의 전체 기능이 필요하지 않으며 모든 `Applicative`에서 작동합니다:

```lean
def doList [Applicative f] : List α → (α → f Unit) → f Unit
  | [], _ => pure ()
  | x :: xs, action =>
    action x *>
    doList xs action
```

## 6.1.2. Using a Custom Monad

While this implementation of `doug` works, manually passing the configuration around is verbose and error-prone.
The type system will not catch it if the wrong configuration is passed downwards, for instance.
A reader effect ensures that the same configuration is passed to all recursive calls, unless it is manually overridden, and it helps make the code less verbose.

이 `doug` 구현이 작동하지만 구성을 수동으로 전달하는 것은 장황하고 오류가 발생하기 쉽습니다. 예를 들어 잘못된 구성이 아래로 전달되면 타입 시스템은 이를 감지하지 못합니다. Reader 효과는 동일한 구성이 수동으로 재정의되지 않는 한 모든 재귀 호출에 전달되도록 보장하며 코드를 덜 장황하게 만드는 데 도움이 됩니다.

To create a version of `IO` that is also a reader of `Config`, first define the type and its `Monad` instance, following the recipe from [the evaluator example](../ch04/):

`Config`의 Reader이기도 한 `IO`의 버전을 만들려면 [평가자 예제](../ch04/)의 레시피를 따르면서 먼저 타입과 `Monad` 인스턴스를 정의합니다:

```lean
def ConfigIO (α : Type) : Type :=
  Config → IO α

instance : Monad ConfigIO where
  pure x := fun _ => pure x
  bind result next := fun cfg => do
    let v ← result cfg
    next v cfg
```

The difference between this `Monad` instance and the one for `Reader` is that this one uses `do`-notation in the `IO` monad as the body of the function that `bind` returns, rather than applying `next` directly to the value returned from `result`.
Any `IO` effects performed by `result` must occur before `next` is invoked, which is ensured by the `IO` monad's `bind` operator.
`ConfigIO` is not universe polymorphic because the underlying `IO` type is also not universe polymorphic.

이 `Monad` 인스턴스와 `Reader`의 인스턴스 간의 차이는 `bind`이 반환하는 함수의 본문으로 `result`에서 반환된 값에 `next`를 직접 적용하는 대신 `IO` Monad에서 `do` 표기법을 사용한다는 것입니다. `result`에 의해 수행된 모든 `IO` 효과는 `next`를 호출하기 전에 발생해야 하며, 이는 `IO` Monad의 `bind` 연산자에 의해 보장됩니다. `ConfigIO`는 기본 `IO` 타입도 universe 다형이 아니기 때문에 universe 다형이 아닙니다.

Running a `ConfigIO` action involves transforming it into an `IO` action by providing it with a configuration:

`ConfigIO` 작업을 실행하는 것은 구성을 제공하여 `IO` 작업으로 변환하는 것을 포함합니다:

```lean
def ConfigIO.run (action : ConfigIO α) (cfg : Config) : IO α :=
  action cfg
```

This function is not really necessary, as a caller could simply provide the configuration directly.
However, naming the operation can make it easier to see which parts of the code are intended to run in which monad.

이 함수는 호출자가 단순히 구성을 직접 제공할 수 있으므로 실제로 필요하지 않습니다. 그러나 작업의 이름을 지정하면 코드의 어느 부분이 어느 Monad에서 실행되도록 의도되었는지 더 쉽게 볼 수 있습니다.

The next step is to define a means of accessing the current configuration as part of `ConfigIO`:

다음 단계는 `ConfigIO`의 일부로 현재 구성에 액세스하는 방법을 정의하는 것입니다:

```lean
def currentConfig : ConfigIO Config :=
  fun cfg => pure cfg
```

This is just like `read` from [the evaluator example](../ch04/), except it uses `IO`'s `pure` to return its value rather than doing so directly.
Because entering a directory modifies the current configuration for the scope of a recursive call, it will be necessary to have a way to override a configuration:

이것은 [평가자 예제](../ch04/)의 `read`와 유사하지만 직접 반환하는 대신 `IO`의 `pure`을 사용하여 값을 반환합니다. 디렉토리 입장이 재귀 호출의 범위에 대한 현재 구성을 수정하기 때문에 구성을 재정의하는 방법이 필요합니다:

```lean
def locally (change : Config → Config) (action : ConfigIO α) : ConfigIO α :=
  fun cfg => action (change cfg)
```

Much of the code used in `doug` has no need for configurations, and `doug` calls ordinary Lean `IO` actions from the standard library that certainly don't need a `Config`.
Ordinary `IO` actions can be run using `runIO`, which ignores the configuration argument:

`doug`에서 사용되는 많은 코드는 구성이 필요하지 않으며, `doug`은 확실히 `Config`가 필요하지 않은 표준 라이브러리의 일반적인 Lean `IO` 작업을 호출합니다. 일반적인 `IO` 작업은 구성 인수를 무시하는 `runIO`를 사용하여 실행할 수 있습니다:

```lean
def runIO (action : IO α) : ConfigIO α :=
  fun _ => action
```

With these components, `showFileName` and `showDirName` can be updated to take their configuration arguments implicitly through the `ConfigIO` monad.
They use [nested actions](../ch02/) to retrieve the configuration, and `runIO` to actually execute the call to `IO.println`:

이러한 구성 요소를 사용하면 `showFileName` 및 `showDirName`을 업데이트하여 `ConfigIO` Monad를 통해 암묵적으로 구성 인수를 받을 수 있습니다. [중첩된 액션](../ch02/)을 사용하여 구성을 검색하고 `runIO`를 사용하여 실제로 `IO.println`에 대한 호출을 실행합니다:

```lean
def showFileName (file : String) : ConfigIO Unit := do
  runIO (IO.println ((← currentConfig).fileName file))
def showDirName (dir : String) : ConfigIO Unit := do
  runIO (IO.println ((← currentConfig).dirName dir))
```

In the new version of `dirTree`, the calls to `toEntry` and `readDir` are wrapped in `runIO`.
Additionally, instead of building a new configuration and then requiring the programmer to keep track of which one to pass to recursive calls, it uses `locally` to naturally delimit the modified configuration to only a small region of the program, in which it is the *only* valid configuration:

새로운 `dirTree` 버전에서 `toEntry` 및 `readDir`에 대한 호출은 `runIO`로 래핑됩니다. 또한 새로운 구성을 빌드한 다음 프로그래머가 재귀 호출에 전달할 구성을 추적하도록 요구하는 대신 `locally`를 사용하여 수정된 구성을 프로그램의 작은 영역으로만 자연스럽게 구분하며, 이것이 *유일한* 유효한 구성입니다:

```lean
partial def dirTree (path : System.FilePath) : ConfigIO Unit := do
  match ← runIO (toEntry path) with
  | none => pure ()
  | some (.file name) => showFileName name
  | some (.dir name) =>
    showDirName name
    let contents ← runIO path.readDir
    locally (·.inDirectory)
      (doList (contents.qsort dirLT).toList fun d =>
        dirTree d.path)
```

The new version of `main` uses `ConfigIO.run` to invoke `dirTree` with the initial configuration:

새로운 `main` 버전은 `ConfigIO.run`을 사용하여 초기 구성으로 `dirTree`를 호출합니다:

```lean
def main (args : List String) : IO UInt32 := do
  match configFromArgs args with
  | some config =>
    (dirTree (← IO.currentDir)).run config
    pure 0
  | none =>
    IO.eprintln s!"Didn't understand argument(s) {" ".separate args}\n"
    IO.eprintln usage
    pure 1
```

This custom monad has a number of advantages over passing configurations manually:

이 사용자 정의 Monad는 수동으로 구성을 전달하는 것에 비해 여러 장점이 있습니다:

1. It is easier to ensure that configurations are passed down unchanged, except when changes are desired
2. The concern of passing the configuration onwards is more clearly separated from the concern of printing directory contents
3. As the program grows, there will be more and more intermediate layers that do nothing with configurations except propagate them, and these layers don't need to be rewritten as the configuration logic changes

1. 변경이 원할 때를 제외하고는 구성이 변경되지 않은 채로 전달되도록 하기 더 쉽습니다.
2. 구성을 전달하는 것에 대한 관심이 디렉토리 내용을 인쇄하는 것에 대한 관심과 더 명확하게 분리됩니다.
3. 프로그램이 커질수록 구성을 전파하는 것 외에는 아무것도 하지 않는 중간 계층이 점점 더 많아질 것이며, 이러한 계층들은 구성 로직이 변경될 때 다시 작성될 필요가 없습니다.

However, there are also some clear downsides:

그러나 몇 가지 명확한 단점도 있습니다:

1. As the program evolves and the monad requires more features, each of the basic operators such as `locally` and `currentConfig` will need to be updated
2. Wrapping ordinary `IO` actions in `runIO` is noisy and distracts from the flow of the program
3. Writing monads instances by hand is repetitive, and the technique for adding a reader effect to another monad is a design pattern that requires documentation and communication overhead

1. 프로그램이 진화하고 Monad가 더 많은 기능이 필요함에 따라 `locally` 및 `currentConfig`와 같은 각각의 기본 연산자들을 업데이트해야 합니다.
2. 일반적인 `IO` 작업을 `runIO`로 래핑하는 것은 시끄럽고 프로그램의 흐름에서 주의를 분산시킵니다.
3. Monad 인스턴스를 손으로 작성하는 것은 반복적이며, 다른 Monad에 Reader 효과를 추가하는 기술은 문서화 및 커뮤니케이션 오버헤드가 필요한 디자인 패턴입니다.

Using a technique called *monad transformers*, all of these downsides can be addressed.
A monad transformer takes a monad as an argument and returns a new monad.
Monad transformers consist of:

*Monad transformer*라는 기술을 사용하면 이러한 모든 단점을 해결할 수 있습니다. Monad transformer는 Monad를 인수로 받아서 새로운 Monad를 반환합니다. Monad transformer는 다음으로 구성됩니다:

1. A definition of the transformer itself, which is typically a function from types to types
2. A `Monad` instance that assumes the inner type is already a monad
3. An operator to “lift” an action from the inner monad to the transformed monad, akin to `runIO`

1. Transformer 자체의 정의로, 일반적으로 타입에서 타입으로의 함수입니다.
2. 내부 타입이 이미 Monad라고 가정하는 `Monad` 인스턴스입니다.
3. `runIO`와 유사하게 내부 Monad에서 변환된 Monad로 액션을 “올리는” 연산자입니다.

## 6.1.3. Adding a Reader to Any Monad

Adding a reader effect to `IO` was accomplished in `ConfigIO` by wrapping `IO α` in a function type.
The Lean standard library contains a function that can do this to *any* polymorphic type, called `ReaderT`:

`ConfigIO`에서 `IO`에 Reader 효과를 추가하는 것은 `IO α`를 함수 타입으로 래핑하여 달성되었습니다. Lean 표준 라이브러리는 `ReaderT`라고 불리는 *모든* 다형 타입에 이를 수행할 수 있는 함수를 포함합니다:

```lean
def ReaderT (ρ : Type u) (m : Type u → Type v) (α : Type u) :
    Type (max u v) :=
  ρ → m α
```

Its arguments are as follows:

인수는 다음과 같습니다:

* `ρ` is the environment that is accessible to the reader
* `m` is the monad that is being transformed, such as `IO`
* `α` is the type of values being returned by the monadic computation
  Both `α` and `ρ` are in the same universe because the operator that retrieves the environment in the monad will have type `m ρ`.

* `ρ`는 Reader에 액세스할 수 있는 환경입니다.
* `m`은 `IO`와 같이 변환되고 있는 Monad입니다.
* `α`는 Monadic 계산에 의해 반환되는 값의 타입입니다.
  Monad의 환경을 검색하는 연산자의 타입이 `m ρ`이기 때문에 `α`와 `ρ` 모두 동일한 universe에 있습니다.

With `ReaderT`, `ConfigIO` becomes:

```lean
abbrev ConfigIO (α : Type) : Type := ReaderT Config IO α
```

It is an `abbrev` because `ReaderT` has many useful features defined in the standard library that a non-reducible definition would hide.
Rather than taking responsibility for making these work directly for `ConfigIO`, it's easier to simply have `ConfigIO` behave identically to `ReaderT Config IO`.

`ReaderT`를 사용하면 `ConfigIO`는 다음과 같이 됩니다.

`ReaderT`는 표준 라이브러리에 정의된 많은 유용한 기능을 가지고 있기 때문에 축약형(abbrev)입니다. 이러한 것들을 `ConfigIO`에 대해 직접 작동시키는 책임을 지기 보다는 `ConfigIO`가 `ReaderT Config IO`와 동일하게 동작하도록 하는 것이 더 쉽습니다.

The manually-written `currentConfig` obtained the environment out of the reader.
This effect can be defined in a generic form for all uses of `ReaderT`, under the name `read`:

```lean
def read [Monad m] : ReaderT ρ m ρ :=
  fun env => pure env
```

However, not every monad that provides a reader effect is built with `ReaderT`.
The type class `MonadReader` allows any monad to provide a `read` operator:

수동으로 작성된 `currentConfig`는 Reader에서 환경을 얻었습니다. 이 효과는 `read`라는 이름으로 `ReaderT`의 모든 사용에 대해 일반적인 형식으로 정의될 수 있습니다.

그러나 Reader 효과를 제공하는 모든 Monad가 `ReaderT`로 구성되는 것은 아닙니다. `MonadReader` 타입 클래스는 모든 Monad가 `read` 연산자를 제공할 수 있게 합니다:

```lean
class MonadReader (ρ : outParam (Type u)) (m : Type u → Type v) :
    Type (max (u + 1) v) where
  read : m ρ

instance [Monad m] : MonadReader ρ (ReaderT ρ m) where
  read := fun env => pure env

export MonadReader (read)
```

The type `ρ` is an output parameter because any given monad typically only provides a single type of environment through a reader, so automatically selecting it when the monad is known makes programs more convenient to write.

`ρ` 타입은 출력 매개변수입니다. 왜냐하면 주어진 모든 Monad는 일반적으로 Reader를 통해 단일 타입의 환경만을 제공하기 때문에 Monad가 알려졌을 때 자동으로 선택하면 프로그램을 더 편리하게 작성할 수 있습니다.

The `Monad` instance for `ReaderT` is essentially the same as the `Monad` instance for `ConfigIO`, except `IO` has been replaced by some arbitrary monad argument `m`:

`ReaderT`의 `Monad` 인스턴스는 본질적으로 `ConfigIO`의 `Monad` 인스턴스와 동일하지만 `IO`는 임의의 Monad 인수 `m`으로 대체되었습니다:

```lean
instance [Monad m] : Monad (ReaderT ρ m) where
  pure x := fun _ => pure x
  bind result next := fun env => do
    let v ← result env
    next v env
```

The next step is to eliminate uses of `runIO`.
When Lean encounters a mismatch in monad types, it automatically attempts to use a type class called `MonadLift` to transform the actual monad into the expected monad.
This process is similar to the use of coercions.
`MonadLift` is defined as follows:

다음 단계는 `runIO` 사용을 제거하는 것입니다. Lean이 Monad 타입의 불일치를 만날 때 실제 Monad를 예상된 Monad로 변환하기 위해 `MonadLift`라는 타입 클래스를 사용하려고 자동으로 시도합니다. 이 프로세스는 강제 변환(coercion)의 사용과 유사합니다. `MonadLift`는 다음과 같이 정의됩니다:

```lean
class MonadLift (m : Type u → Type v) (n : Type u → Type w) where
  monadLift : {α : Type u} → m α → n α
```

The method `monadLift` translates from the monad `m` to the monad `n`.
The process is called “lifting” because it takes an action in the embedded monad and makes it into an action in the surrounding monad.
In this case, it will be used to “lift” from `IO` to `ReaderT Config IO`, though the instance works for *any* inner monad `m`:

`monadLift` 메서드는 Monad `m`에서 Monad `n`으로 변환합니다. 이 프로세스를 “lifting”이라고 부르는 이유는 임베드된 Monad의 액션을 주변 Monad의 액션으로 만들기 때문입니다. 이 경우 `IO`에서 `ReaderT Config IO`로 “lift”하는 데 사용되지만 인스턴스는 *모든* 내부 Monad `m`에 대해 작동합니다:

```lean
instance : MonadLift m (ReaderT ρ m) where
  monadLift action := fun _ => action
```

The implementation of `monadLift` is very similar to that of `runIO`.
Indeed, it is enough to define `showFileName` and `showDirName` without using `runIO`:

`monadLift`의 구현은 `runIO`의 구현과 매우 유사합니다. 실제로 `runIO`를 사용하지 않고 `showFileName` 및 `showDirName`을 정의하는 것으로 충분합니다:

```lean
def showFileName (file : String) : ConfigIO Unit := do
  IO.println s!"{(← read).currentPrefix} {file}"
def showDirName (dir : String) : ConfigIO Unit := do
  IO.println s!"{(← read).currentPrefix} {dir}/"
```

One final operation from the original `ConfigIO` remains to be translated to a use of `ReaderT`: `locally`.
The definition can be translated directly to `ReaderT`, but the Lean standard library provides a more general version.
The standard version is called `withReader`, and it is part of a type class called `MonadWithReader`:

원래 `ConfigIO`의 마지막 작업은 `ReaderT` 사용으로 번역되어야 합니다: `locally`. 정의는 직접 `ReaderT`로 번역될 수 있지만 Lean 표준 라이브러리는 더 일반적인 버전을 제공합니다. 표준 버전은 `withReader`라고 불리며 `MonadWithReader`라는 타입 클래스의 일부입니다:

```lean
class MonadWithReader (ρ : outParam (Type u)) (m : Type u → Type v) where
  withReader {α : Type u} : (ρ → ρ) → m α → m α
```

Just as in `MonadReader`, the environment `ρ` is an `outParam`.
The `withReader` operation is exported, so that it doesn't need to be written with the type class name before it:

`MonadReader`와 마찬가지로 환경 `ρ`는 `outParam`입니다. `withReader` 작업은 내보내지므로 앞에 타입 클래스 이름을 작성할 필요가 없습니다:

```lean
export MonadWithReader (withReader)
```

The instance for `ReaderT` is essentially the same as the definition of `locally`:

`ReaderT`의 인스턴스는 본질적으로 `locally`의 정의와 동일합니다:

```lean
instance : MonadWithReader ρ (ReaderT ρ m) where
  withReader change action :=
    fun cfg => action (change cfg)
```

With these definitions in place, the new version of `dirTree` can be written:

이러한 정의가 배치되면 새로운 `dirTree` 버전을 작성할 수 있습니다:

```lean
partial def dirTree (path : System.FilePath) : ConfigIO Unit := do
  match ← toEntry path with
  | none => pure ()
  | some (.file name) => showFileName name
  | some (.dir name) =>
    showDirName name
    let contents ← path.readDir
    withReader (·.inDirectory)
      (doList (contents.qsort dirLT).toList fun d =>
        dirTree d.path)
```

Aside from replacing `locally` with `withReader`, it is the same as before.

Replacing the custom `ConfigIO` type with `ReaderT` did not save a large number of lines of code in this section.
However, rewriting the code using components from the standard library does have long-term benefits.
First, readers who know about `ReaderT` don't need to take time to understand the `Monad` instance for `ConfigIO`, working backwards to the meaning of monad itself.
Instead, they can be confident in their initial understanding.
Next, adding further effects to the monad (such as a state effect to count the files in each directory and display a count at the end) requires far fewer changes to the code, because the monad transformers and `MonadLift` instances provided in the library work well together.
Finally, using a set of type classes included in the standard library, polymorphic code can be written in such a way that it can work with a variety of monads without having to care about details like the order in which the monad transformers were applied.
Just as some functions work in any monad, others can work in any monad that provides a certain type of state, or a certain type of exceptions, without having to specifically describe the *way* in which a particular concrete monad provides the state or exceptions.

`locally`를 `withReader`로 바꾸는 것을 제외하고는 이전과 동일합니다.

사용자 정의 `ConfigIO` 타입을 `ReaderT`로 바꾸는 것은 이 섹션에서 코드의 많은 줄을 절약하지 못했습니다. 그러나 표준 라이브러리의 구성 요소를 사용하여 코드를 다시 작성하면 장기적인 이점이 있습니다. 첫째, `ReaderT`에 대해 아는 독자들은 `ConfigIO`의 `Monad` 인스턴스를 이해하는 데 시간을 들일 필요가 없으며, Monad 자체의 의미로 돌아갈 필요가 없습니다. 대신 초기 이해에 자신감을 가질 수 있습니다. 둘째, Monad에 추가 효과를 추가하는 것 (예: 각 디렉토리의 파일을 세고 마지막에 개수를 표시하는 상태 효과)은 라이브러리에서 제공하는 Monad Transformer와 `MonadLift` 인스턴스가 잘 함께 작동하기 때문에 코드에 훨씬 더 적은 변경이 필요합니다. 마지막으로 표준 라이브러리에 포함된 타입 클래스 집합을 사용하여 Monad Transformer가 적용된 순서와 같은 세부 사항을 신경 쓰지 않고 다양한 Monad에서 작동할 수 있는 방식으로 다형 코드를 작성할 수 있습니다. 일부 함수가 모든 Monad에서 작동하는 것처럼 다른 함수는 특정 유형의 상태를 제공하는 모든 Monad 또는 특정 유형의 예외를 제공하는 모든 Monad에서 작동할 수 있으며, 특정 구체적인 Monad가 상태나 예외를 제공하는 *방식*을 구체적으로 설명할 필요가 없습니다.

## 6.1.4. Exercises

### 6.1.4.1. Controlling the Display of Dotfiles

Files whose names begin with a dot character (`'.'`) typically represent files that should usually be hidden, such as source-control metadata and configuration files.
Modify `doug` with an option to show or hide filenames that begin with a dot.
This option should be controlled with a `-a` command-line option.

### 6.1.4.2. Starting Directory as Argument

Modify `doug` so that it takes a starting directory as an additional command-line argument.
