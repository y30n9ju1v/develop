---
title: "2.3. 프로젝트 시작하기"
date: 2026-07-09T00:00:00+09:00
draft: false
tags: ["lean", "lean4", "functional-programming"]
categories: ["programming"]
description: "Lake를 사용하여 Lean 프로젝트를 생성하고 빌드하는 방법"
---

# 2.3. Starting a Project

As a program written in Lean becomes more serious, an ahead-of-time compiler-based workflow that results in an executable becomes more attractive.
Like other languages, Lean has tools for building multiple-file packages and managing dependencies.
The standard Lean build tool is called Lake (short for “Lean Make”).
Lake is typically configured using a TOML file that declaratively specifies dependencies and describes what is to be built.
For advanced use cases, Lake can also be configured in Lean itself.

Lean으로 작성된 프로그램이 더 복잡해질수록, 실행 파일을 생성하는 사전 컴파일 기반 워크플로우가 더 매력적이 됩니다.
다른 언어처럼 Lean도 다중 파일 패키지를 빌드하고 의존성을 관리하기 위한 도구를 가지고 있습니다.
표준 Lean 빌드 도구를 Lake(짧게 “Lean Make”)라고 합니다.
Lake는 일반적으로 의존성을 선언적으로 지정하고 빌드할 대상을 설명하는 TOML 파일을 사용하여 구성됩니다.
고급 사용 사례의 경우 Lake는 Lean 자체로도 구성할 수 있습니다.

## 2.3.1. First steps

To get started with a project that uses Lake, use the command `lake new greeting` in a directory that does not already contain a file or directory called `greeting`.
This creates a directory called `greeting` that contains the following files:

Lake를 사용하는 프로젝트를 시작하려면, 이미 `greeting`이라는 파일이나 디렉토리를 포함하지 않는 디렉토리에서 `lake new greeting` 명령을 사용합니다.
이는 다음 파일들을 포함하는 `greeting`이라는 디렉토리를 만듭니다:

* `Main.lean` is the file in which the Lean compiler will look for the `main` action.
* `Greeting.lean` and `Greeting/Basic.lean` are the scaffolding of a support library for the program.
* `lakefile.toml` contains the configuration that `lake` needs to build the application.
* `lean-toolchain` contains an identifier for the specific version of Lean that is used for the project.

* `Main.lean`은 Lean 컴파일러가 `main` 액션을 찾는 파일입니다.
* `Greeting.lean`과 `Greeting/Basic.lean`은 프로그램의 지원 라이브러리의 기본 구조입니다.
* `lakefile.toml`은 애플리케이션을 빌드하기 위해 `lake`가 필요로 하는 구성을 포함합니다.
* `lean-toolchain`은 프로젝트에 사용되는 Lean의 특정 버전에 대한 식별자를 포함합니다.

Additionally, `lake new` initializes the project as a Git repository and configures its `.gitignore` file to ignore intermediate build products.
Typically, the majority of the application logic will be in a collection of libraries for the program, while `Main.lean` will contain a small wrapper around these pieces that does things like parsing command lines and executing the central application logic.
To create a project in an already-existing directory, run `lake init` instead of `lake new`.

또한 `lake new`는 프로젝트를 Git 저장소로 초기화하고 중간 빌드 산물을 무시하도록 `.gitignore` 파일을 구성합니다.
일반적으로 애플리케이션 로직의 대부분은 프로그램의 라이브러리 모음에 있고, `Main.lean`은 명령줄 구문 분석 및 중앙 애플리케이션 논리 실행과 같은 작업을 수행하는 이러한 부분들 주위의 작은 래퍼를 포함합니다.
기존 디렉토리에 프로젝트를 만들려면 `lake new` 대신 `lake init`을 실행합니다.

By default, the library file `Greeting/Basic.lean` contains a single definition:

기본적으로 라이브러리 파일 `Greeting/Basic.lean`은 단일 정의를 포함합니다.

File: `Greeting/Basic.lean`

```lean
def hello := "world"
```

The library file `Greeting.lean` imports `Greeting/Basic.lean`:

라이브러리 파일 `Greeting.lean`은 `Greeting/Basic.lean`을 import합니다.

File: `Greeting.lean`

```lean
-- This module serves as the root of the `Greeting` library.
-- Import modules here that should be built as part of the library.
import Greeting.Basic
```

This means that everything defined in `Greeting/Basic.lean` is also available to files that import `Greeting.lean`.
In `import` statements, dots are interpreted as directories on disk.

즉, `Greeting/Basic.lean`에서 정의된 모든 것이 `Greeting.lean`을 import하는 파일에도 사용 가능합니다.
`import` 문에서 점은 디스크의 디렉토리로 해석됩니다.

The executable source `Main.lean` contains:

실행 파일 소스 `Main.lean`은 다음을 포함합니다.

File: `Main.lean`

```lean
import Greeting

def main : IO Unit :=
  IO.println s!"Hello, {hello}!"
```

Because `Main.lean` imports `Greeting.lean` and `Greeting.lean` imports `Greeting/Basic.lean`, the definition of `hello` is available in `main`.

`Main.lean`이 `Greeting.lean`을 import하고 `Greeting.lean`이 `Greeting/Basic.lean`을 import하기 때문에, `hello`의 정의는 `main`에서 사용 가능합니다.

To build the package, run the command `lake build`.
After a number of build commands scroll by, the resulting binary has been placed in `.lake/build/bin`.
Running `./.lake/build/bin/greeting` results in `Hello, world!`.
Instead of running the binary directly, the command `lake exe` can be used to build the binary if necessary and then run it.
Running `lake exe greeting` also results in `Hello, world!`.

패키지를 빌드하려면 `lake build` 명령을 실행합니다.
여러 빌드 명령이 표시된 후 결과 바이너리는 `.lake/build/bin`에 배치됩니다.
`./.lake/build/bin/greeting`을 실행하면 `Hello, world!`가 출력됩니다.
바이너리를 직접 실행하는 대신 `lake exe` 명령을 사용하여 필요한 경우 바이너리를 빌드한 후 실행할 수 있습니다.
`lake exe greeting`을 실행해도 `Hello, world!`가 출력됩니다.

## 2.3.2. Lakefiles

A `lakefile.toml` describes a *package*, which is a coherent collection of Lean code for distribution, analogous to an `npm` or `nuget` package or a Rust crate.
A package may contain any number of libraries or executables.
The [documentation for Lake](https://lean-lang.org/doc/reference/latest/find/?domain=Verso.Genre.Manual.section&name=lake-config-toml) describes the available options in a Lake configuration.
The generated `lakefile.toml` contains the following:

`lakefile.toml`은 배포를 위한 일관된 Lean 코드 모음인 *패키지*를 설명하며, 이는 `npm` 또는 `nuget` 패키지나 Rust crate와 유사합니다.
패키지는 임의의 수의 라이브러리 또는 실행 파일을 포함할 수 있습니다.
[Lake 문서](https://lean-lang.org/doc/reference/latest/find/?domain=Verso.Genre.Manual.section&name=lake-config-toml)는 Lake 구성에서 사용 가능한 옵션을 설명합니다.
생성된 `lakefile.toml`은 다음을 포함합니다.

File: `lakefile.toml`

```toml
name = "greeting"
version = "0.1.0"
defaultTargets = ["greeting"]

[[lean_lib]]
name = "Greeting"

[[lean_exe]]
name = "greeting"
root = "Main"
```

This initial Lake configuration consists of three items:

이 초기 Lake 구성은 세 개의 항목으로 구성됩니다:

* *package* settings, at the top of the file,
* a *library* declaration, named `Greeting`, and
* an *executable*, named `greeting`.

* 파일의 맨 위에 있는 *패키지* 설정,
* `Greeting`이라는 이름의 *라이브러리* 선언, 그리고
* `greeting`이라는 이름의 *실행 파일*.

Each Lake configuration file will contain exactly one package, but any number of dependencies, libraries, or executables.
By convention, package and executable names begin with a lowercase letter, while libraries begin with an uppercase letter.
Dependencies are declarations of other Lean packages (either locally or from remote Git repositories)
The items in the Lake configuration file allow things like source file locations, module hierarchies, and compiler flags to be configured.
Generally speaking, however, the defaults are reasonable.
Lake configuration files written in the Lean format may additionally contain *external libraries*, which are libraries not written in Lean to be statically linked with the resulting executable, *custom targets*, which are build targets that don't fit naturally into the library/executable taxonomy, and *scripts*, which are essentially `IO` actions (similar to `main`), but that additionally have access to metadata about the package configuration.

각 Lake 구성 파일은 정확히 하나의 패키지를 포함하지만 임의의 수의 의존성, 라이브러리 또는 실행 파일을 포함할 수 있습니다.
관례상 패키지와 실행 파일의 이름은 소문자로 시작하고, 라이브러리는 대문자로 시작합니다.
의존성은 다른 Lean 패키지(로컬 또는 원격 Git 저장소에서)의 선언입니다.
Lake 구성 파일의 항목은 소스 파일 위치, 모듈 계층 구조, 컴파일러 플래그 등을 구성할 수 있습니다.
일반적으로 기본값은 합리적입니다.
Lean 형식으로 작성된 Lake 구성 파일은 추가로 *외부 라이브러리*(결과 실행 파일과 정적으로 연결되는 Lean 이외의 언어로 작성된 라이브러리), *사용자 정의 대상*(라이브러리/실행 파일 분류에 자연스럽게 맞지 않는 빌드 대상), 그리고 *스크립트*(본질적으로 `IO` 액션(main과 유사)이지만 패키지 구성에 대한 메타데이터에 대한 추가 접근 권한이 있음)를 포함할 수 있습니다.

Libraries, executables, and custom targets are all called *targets*.
By default, `lake build` builds those targets that are specified in the `defaultTargets` list.
To build a target that is not a default target, specify the target's name as an argument after `lake build`.

라이브러리, 실행 파일, 사용자 정의 대상은 모두 *대상(targets)*라고 합니다.
기본적으로 `lake build`는 `defaultTargets` 목록에 지정된 대상을 빌드합니다.
기본 대상이 아닌 대상을 빌드하려면 `lake build` 뒤에 인수로 대상의 이름을 지정합니다.

## 2.3.3. Libraries and Imports

A Lean library consists of a hierarchically organized collection of source files from which names can be imported, called *modules*.
By default, a library has a single root file that matches its name.
In this case, the root file for the library `Greeting` is `Greeting.lean`.
The first line of `Main.lean`, which is `import Greeting`, makes the contents of `Greeting.lean` available in `Main.lean`.

Lean 라이브러리는 *모듈(modules)*이라고 불리는 이름을 import할 수 있는 계층적으로 구성된 소스 파일의 모음입니다.
기본적으로 라이브러리는 그 이름과 일치하는 단일 루트 파일을 가집니다.
이 경우 라이브러리 `Greeting`의 루트 파일은 `Greeting.lean`입니다.
`Main.lean`의 첫 번째 줄인 `import Greeting`은 `Greeting.lean`의 내용을 `Main.lean`에서 사용 가능하게 만듭니다.

Additional module files may be added to the library by creating a directory called `Greeting` and placing them inside.
These names can be imported by replacing the directory separator with a dot.
For instance, creating the file `Greeting/Smile.lean` with the contents:

추가 모듈 파일은 `Greeting`이라는 디렉토리를 만들고 그 안에 배치하여 라이브러리에 추가할 수 있습니다.
이 이름들은 디렉토리 구분자를 점으로 바꾸어 import할 수 있습니다.
예를 들어, 다음 내용으로 `Greeting/Smile.lean` 파일을 만드는 경우.

File: `Greeting/Smile.lean`

File: `Greeting/Smile.lean`

```lean
def Expression.happy : String := "a big smile"
```

```lean
def Expression.happy : String := "a big smile"
```

means that `Main.lean` can use the definition as follows:

`Main.lean`이 다음과 같이 정의를 사용할 수 있음을 의미합니다.

File: `Main.lean`

File: `Main.lean`

```lean
import Greeting
import Greeting.Smile

open Expression

def main : IO Unit :=
  IO.println s!"Hello, {hello}, with {happy}!"
```

```lean
import Greeting
import Greeting.Smile

open Expression

def main : IO Unit :=
  IO.println s!"Hello, {hello}, with {happy}!"
```

The module name hierarchy is decoupled from the namespace hierarchy.
In Lean, modules are units of code distribution, while namespaces are units of code organization.
That is, names defined in the module `Greeting.Smile` are not automatically in a corresponding namespace `Greeting.Smile`.
In particular, `happy` is in the `Expression` namespace.
Modules may place names into any namespace they like, and the code that imports them may `open` the namespace or not.
`import` is used to make the contents of a source file available, while `open` makes names from a namespace available in the current context without prefixes.

모듈 이름 계층 구조는 네임스페이스 계층 구조와 분리되어 있습니다.
Lean에서 모듈은 코드 배포의 단위인 반면 네임스페이스는 코드 구성의 단위입니다.
즉, 모듈 `Greeting.Smile`에서 정의된 이름들이 자동으로 해당 네임스페이스 `Greeting.Smile`에 있지 않습니다.
특히 `happy`는 `Expression` 네임스페이스에 있습니다.
모듈은 이름을 원하는 모든 네임스페이스에 넣을 수 있으며, 이를 import하는 코드는 네임스페이스를 `open`할 수도 있고 하지 않을 수도 있습니다.
`import`는 소스 파일의 내용을 사용 가능하게 만드는 데 사용되는 반면, `open`은 현재 컨텍스트에서 네임스페이스의 이름을 접두사 없이 사용 가능하게 만듭니다.

The line `open Expression` makes the name `Expression.happy` accessible as `happy` in `main`.
Namespaces may also be opened *selectively*, making only some of their names available without explicit prefixes.
This is done by writing the desired names in parentheses.
For example, `Nat.toFloat` converts a natural number to a `Float`.
It can be made available as `toFloat` using `open Nat (toFloat)`.

`open Expression` 라인은 `main`에서 이름 `Expression.happy`를 `happy`로 접근 가능하게 만듭니다.
네임스페이스는 또한 *선택적으로* 열릴 수 있으며, 일부 이름만 명시적 접두사 없이 사용 가능하게 만듭니다.
이는 원하는 이름을 괄호 안에 작성하여 수행됩니다.
예를 들어 `Nat.toFloat`은 자연수를 `Float`으로 변환합니다.
`open Nat (toFloat)`를 사용하여 `toFloat`로 사용 가능하게 만들 수 있습니다.
