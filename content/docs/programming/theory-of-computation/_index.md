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
