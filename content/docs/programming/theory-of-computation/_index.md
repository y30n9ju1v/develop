---
title: "계산 이론"
date: 2026-07-12T00:00:00+09:00
draft: false
tags: ["theory-of-computation", "automata", "complexity-theory"]
categories: ["programming"]
description: "MIT 18.404 Theory of Computation 강의를 요약 정리하고, 컴퓨터가 풀 수 있는 문제와 그 한계에 대해 다룹니다."
---

MIT 18.404J Theory of Computation(Michael Sipser 교수) 강의 노트를 기반으로 작성한 계산 이론 요약 시리즈입니다.

## 시리즈 목록

- **[1. 유한 오토마타와 정규 언어](01-introduction-finite-automata-regular-expressions/)** — 가장 단순한 컴퓨터 모델인 유한 오토마타, 5-Tuple 수학적 정의, 정규 연산과 합집합 닫힘성 증명
- **[2. 비결정론(Nondeterminism)과 정규 표현식의 NFA 변환](02-nondeterminism-closure-properties-regular-expressions-to-finite-automata/)** — 비결정적 유한 오토마타(NFA)의 개념과 수학적 정의, NFA와 DFA의 동등성 증명(Subset Construction), NFA를 이용한 정규 표현식 조립
- **[3. 펌핑 렘마(Pumping Lemma)와 문맥 자유 문법(CFG)](03-the-regular-pumping-lemma-finite-automata-to-regular-expressions-cfgs/)** — DFA를 정규 표현식으로 바꾸는 GNFA 변환 알고리즘, 정규 언어 여부를 판별하는 펌핑 렘마(Pumping Lemma) 증명, 문맥 자유 문법(CFG)의 개념
- **[4. 푸시다운 오토마타(PDA)와 문맥 자유 언어(CFL)](04-pushdown-automata-cfg-to-and-from-pda/)** — 문맥 자유 문법(CFG)의 수학적 형식 정의와 모호성(Ambiguity), 스택 메모리를 탑재한 푸시다운 오토마타(PDA)의 정의 및 CFG와 PDA 동등성 증명 알고리즘
- **[5. CFL 펌핑 렘마와 계산 이론의 종착지, 튜링 머신(Turing Machine)](05-the-cf-pumping-lemma-turing-machines/)** — 문맥 자유 언어(CFL)의 펌핑 렘마 증명, CFL 교집합 닫힘성 예외, 무제한 테이프 메모리를 가진 튜링 머신(Turing Machine)의 기하학적 정의 및 인식 가능(Recognizable)/판정 가능(Decidable) 구분
- **[6. 튜링 머신의 변형들과 처치-튜링 명제(Church-Turing Thesis)](06-tm-variants-the-church-turing-thesis/)** — 다중 테이프 TM, 비결정적 TM, 열거기(Enumerator) 시뮬레이션 및 알고리즘의 본질을 밝히는 처치-튜링 명제, 디오판토스 방정식의 판정 불가성을 입증한 힐베르트의 10번째 문제
- **[7. 오토마타와 문법의 판정성(Decidability) 및 유니버설 튜링 머신(UTM)](07-decision-problems-for-automata-and-grammars/)** — DFA, NFA, CFG의 수락성/공백성/동치성 판정 가능성 및 촘스키 정규형(CNF) 활용, 현대 내장 프로그램 컴퓨터의 모태가 된 유니버설 튜링 머신(UTM)의 작동 원리
- **[8. 대각선 논법과 정지 문제(Halting Problem)의 판정 불가능성](08-undecidability/)** — 무한의 크기를 규명하는 게오르크 칸토어의 대각선 논법(Diagonalization), 프로그램의 개수적 한계 증명, 수락 문제($A_{\text{TM}}$) 및 정지 문제(Halting Problem)의 판정 불가능성(Undecidability) 증명
- **[9. 매핑 환원(Mapping Reducibility)과 프로그램 분석의 한계](09-reducibility/)** — 환원 개념의 형식 수학 정의인 매핑 환원($\le_m$), 튜링 머신 공백성 문제($E_{\text{TM}}$)의 판정/인식 불가능 증명, 그리고 두 프로그램의 일치성을 판별할 수 없는 동치성 문제($EQ_{\text{TM}}$)의 비인식성 증명
- **[10. 계산 이력 방법(Computation History)과 LBA·PCP·CFG의 난제들](10-the-computation-history-method/)** — 실행 로그를 사용하는 계산 이력 방법의 원리, LBA 공백성 문제($E_{\text{LBA}}$)의 판정 불가능 증명, 도미노 매칭 퍼즐인 포스트 대응 문제(PCP)의 불가능성 증명 및 CFG 전역 매칭 문제($ALL_{\text{CFG}}$)의 판정 불가능 증명
- **[11. 재귀 정리(Recursion Theorem)와 괴델의 불완전성 정리](11-the-recursion-theorem-and-logic/)** — 프로그램이 자기 설계도를 읽어들이는 클레이니 재귀 정리, 콰인(Quine)의 구성, 고정점 정리(Fixed-point Theorem) 및 괴델의 제1불완전성 정리 증명
- **[12. 시간 복잡도(Time Complexity)와 다항 시간 클래스 P](12-time-complexity/)** — 계산 복잡도 이론 개요 및 Big-O 표기법, 하드웨어 모델에 따른 연산 시간 분석 및 다항식적 관계(Polynomial overhead), 그리고 다항 시간 해결 가능 문제 집합인 클래스 P(Class P)의 정의와 PATH vs HAMPATH 문제 소개
- **[14. 클래스 NP와 SAT 문제, 그리고 다항 시간 환원(Polynomial-time Reducibility)](14-p-and-np-sat-poly-time-reducibility/)** — 비결정적 다항 시간 클래스 NP와 정답 인증서(Certificate), 동적 계획법(DP)을 사용한 $A_{\text{CFG}} \in \text{P}$ 증명, 논리 만족 가능성 문제(SAT), 그리고 복잡도 하한선을 입증하는 다항 시간 환원($\le_{\text{P}}$)의 정의
- **[15. NP-완전성(NP-Completeness)과 Clique, HamPath 문제](15-np-completeness/)** — NP 클래스 내에서 가장 어려운 핵심 문제인 NP-완전성의 수학적 정의와 의의, 최초의 NP-완전 문제인 SAT와 이를 응용해 3SAT 문제를 CLIQUE 및 HAMPATH로 다항 시간 환원(Reduction)하는 상세 증명과 그 의의
- **[16. 쿡-레빈 정리(Cook-Levin Theorem)와 SAT 문제의 NP-완전성 증명](16-cook-levin-theorem/)** — 최초의 NP-완전(NP-Complete) 문제인 SAT의 쿡-레빈 정리 증명 과정, NTM 연산을 논리식 격자판으로 시뮬레이션하는 태블로(Tableau) 및 2x3 윈도우 합법성 규칙, 그리고 3SAT의 NP-완전성 증명
- **[17. 공간 복잡도(Space Complexity)와 다항 공간 클래스 PSPACE, Savitch 정리](17-space-complexity/)** — 메모리 공간을 기준으로 하는 공간 복잡도 개요, 시간 복잡도와의 관계, 다항 공간 클래스 PSPACE 및 TQBF 문제 분석, 그리고 비결정적 공간을 결정론적으로 시뮬레이션하여 NPSPACE = PSPACE를 입증한 Savitch 정리와 그 작동 원리
- **[18. 공간 복잡도(Space Complexity)와 새비치 정리, 그리고 TQBF의 PSPACE-완전성](18-pspace-completeness/)** — PSPACE = NPSPACE 임을 증명하는 새비치 정리(Savitch's Theorem), PSPACE-완전성(PSPACE-Completeness) 및 다항 시간 환원의 의의, 그리고 TQBF의 PSPACE-완전성 증명 과정에서 식의 길이를 줄이는 양화사 융합 트릭
- **[19. 게임, 일반화된 지리(Generalized Geography) 및 로그 공간(Logspace) 복잡도](19-games-generalized-geography/)** — QBF 논리식을 두 플레이어의 대결로 묘사하는 포뮬러 게임(Formula Game)을 통해 게임과 복잡도의 관계를 이해하고, Generalized Geography의 PSPACE-완전성 증명 및 입력 외에 O(log n) 작업 메모리만 사용하는 로그 공간 복잡도(L, NL)의 다양한 성질을 학습
- **[20. 로그 공간 복잡도 클래스 L과 NL, 그리고 NL = coNL의 기적](20-l-and-nl-nl-conl/)** — 입력 데이터를 상수 개수 포인터로 나타내는 로그 공간(L, NL) 개념, 설정 그래프를 활용한 L, NL ⊆ P 유도, 로그 공간 환원 및 PATH의 NL-완전성 입증, 그리고 NL = coNL(임머만-셀레프체니 정리)의 완벽 증명
- **[21. 계층 정리(Hierarchy Theorems)와 NL = coNL 정리의 완결](21-hierarchy-theorems/)** — 도달 가능한 노드 수 카운팅 기법을 통한 NL = coNL(임머만-셀레프체니 정리) 증명 완결, 더 많은 시간과 공간이 주어지면 더 복잡한 문제를 풀 수 있음을 대각선 논법으로 보이는 시간 및 공간 계층 정리(Time/Space Hierarchy Theorems)의 상세 분석




