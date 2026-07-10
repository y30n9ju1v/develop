---
title: "Let's build GPT: from scratch 핵심 요약 및 타임라인"
date: 2026-05-14T08:04:17+09:00
draft: false
tags: ["Deep Learning", "LLM", "GPT", "PyTorch", "Transformer"]
categories: ["programming"]
description: "안드레 카파시(Andrej Karpathy)의 'Let's build GPT: from scratch' 강의 타임라인과 핵심 요약, 수식 및 코드를 포함한 상세 가이드를 정리합니다."
---

## Let's build GPT: from scratch, in code, spelled out. (Andrej Karpathy)

> 이 글은 딥러닝 기초(행렬 연산, 역전파, PyTorch 기초)에 익숙한 독자를 대상으로 합니다.

안드레 카파시(Andrej Karpathy)의 ["Let's build GPT: from scratch"](https://www.youtube.com/watch?v=kCc8FmEb1nY)는 가장 유명하고 뛰어난 언어 모델(LLM) 입문 강의 중 하나입니다. 이 영상은 트랜스포머(Transformer) 아키텍처의 핵심인 "Self-Attention"부터 시작해, 가장 단순한 빅램(Bigram) 모델을 거쳐서 최종적으로 작은 셰익스피어 데이터셋을 학습하는 생성형 트랜스포머(Generative Pretrained Transformer, GPT)를 바닥부터 구현하는 과정을 다룹니다.

이 강의의 핵심은 그가 공개한 [nanoGPT](https://github.com/karpathy/nanoGPT)의 뼈대를 어떻게 만들어가는지, 그리고 그 과정에서 수반되는 수학적/구조적 결정을 왜 내리는지를 직관적으로 설명하는 데 있습니다. 본 문서에서는 이 강의의 타임라인과 각 챕터별 핵심 개념, 수식, 그리고 코드 통찰을 상세하게 정리합니다.

---

## 타임라인 및 핵심 내용 정리

### 1. 시작 및 데이터 전처리 (00:00:00 - 00:22:10)
가장 먼저 다루는 것은 데이터를 모델이 소화할 수 있는 형태로 바꾸는 '토큰화'와 '배치 처리'입니다.
- **00:00:00 Intro:** 강의 소개, ChatGPT와 Transformer 개요, nanoGPT 프로젝트 설명.
- **00:07:52 데이터 읽기 및 탐색:** `input.txt` (tiny Shakespeare dataset, 약 100만 자)를 가져와 데이터를 관찰합니다.
- **00:09:28 Tokenization (토큰화) 및 Train/Val Split:** 텍스트를 문자로(Character-level) 나누어 토큰화합니다. OpenAI의 `tiktoken`이나 BPE(Byte-Pair Encoding) 같은 서브워드(Subword) 방식 대신, 문자 단위(Vocabulary size 약 65)를 사용하여 딥러닝 원리 그 자체를 쉽게 이해할 수 있도록 구성합니다.
  - *Tip:* `stoi`(string-to-integer)와 `itos`(integer-to-string) 딕셔너리를 직접 구현하여 인코더와 디코더를 만듭니다.

```python
chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])
```

- **00:14:27 Data Loader 구성:** 모델 학습을 위해 전체 데이터를 고정된 길이(`block_size` 또는 `context_length`)의 청크(chunk)로 나눕니다. 이 때 타겟(Target)은 입력보다 한 스텝 미래의 문자 배열이 됩니다. 이를 병렬 처리를 위해 `batch_size` 단위로 묶어 PyTorch 텐서로 변환합니다.

```python
def get_batch(split):
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    return x, y
```

### 2. 가장 단순한 형태의 언어 모델: Bigram 모델 (00:22:11 - 00:42:12)
문맥을 전혀 고려하지 않는 가장 기초적인 확률 모델을 만듭니다.
- **00:22:11 Bigram Language Model Baseline:** 직전 하나의 문자(token)만을 보고 다음 문자를 예측하는 단순한 신경망 기반 언어 모델을 설계합니다. 파이토치의 `nn.Embedding` 레이어 하나만으로 구현됩니다.
- **00:34:53 모델 학습:** 예측된 로짓(Logits)과 실제 타겟 간의 Negative Log Likelihood (Cross Entropy) Loss를 계산합니다. PyTorch의 기본 최적화 알고리즘인 `AdamW`를 사용하여 모델을 학습시킵니다.
- **00:38:00 코드 모듈화:** 노트북에 나열되어 있던 코드를 `BigramLanguageModel` 클래스 형태로 정리합니다.

### 3. Self-Attention의 기초 이해 및 고도화 (00:42:13 - 01:11:37)
이 강의의 **가장 중요한 하이라이트**입니다. 토큰들이 어떻게 서로 "소통"하는지를 점진적으로 코드로 증명합니다.

- **00:42:13 Self-Attention v1 (For loops):** 현재 토큰이 과거의 정보(문맥)를 얻기 위해, 과거 토큰들의 정보를 단순 평균(Averaging) 내는 방식을 `for`문으로 직접 구현합니다. 매우 느리고 비효율적입니다.
- **00:47:11 Self-Attention의 마법 (Matrix Multiply):** 하삼각행렬(Lower Triangular Matrix)을 곱하는 행렬 연산(`torch.tril`)의 특성을 활용하면, 복잡한 반복문 없이 한 번의 행렬 곱으로 "과거 토큰들의 가중합"을 구할 수 있음을 증명합니다.

```python
# for loop 방식 → 행렬 곱 방식으로 대체
tril = torch.tril(torch.ones(T, T))
wei = torch.zeros((T, T))
wei = wei.masked_fill(tril == 0, float('-inf'))
wei = F.softmax(wei, dim=-1)
xbow = wei @ x  # (T, T) @ (B, T, C) → (B, T, C)
```

- **00:51:54 Self-Attention v2 & v3 (Softmax):** 영행렬에 `torch.tril`을 씌우고, 미래 토큰 부분은 `-inf`로 덮어씌웁니다(`masked_fill`). 이후 Softmax를 취하면 완벽하게 과거만 참조하는 **Masked Attention**이 완성됩니다.
- **01:00:18 Positional Encoding:** 트랜스포머는 데이터를 "집합(Set)"으로 처리하므로 단어의 순서를 모릅니다. 따라서 각 토큰이 현재 위치가 어디인지 알 수 있게끔 `Token Embedding` 외에 `Position Embedding`을 명시적으로 더해줍니다.
- **01:02:00 핵심 챕터: Self-Attention v4 (Q, K, V):** 각 토큰은 단순 평균이 아니라 자신이 원하는 정보에만 집중해야 합니다.
  - **Query (Q):** "나는 지금 이런 정보를 찾고 있어."
  - **Key (K):** "나는 이런 정보를 갖고 있는 토큰이야."
  - **Value (V):** "만약 내 Key가 네 Query와 잘 맞는다면, 내가 실제로 너에게 전달할 정보(내용)는 이거야."
  - Q와 K를 내적(Dot Product)하여 어텐션 가중치(Attention Weights)를 구하고, 이를 V에 곱해 최종 정보를 추출합니다.

```python
k = self.key(x)    # (B, T, head_size)
q = self.query(x)  # (B, T, head_size)
v = self.value(x)  # (B, T, head_size)

wei = q @ k.transpose(-2, -1) * head_size**-0.5  # scaled dot-product
wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
wei = F.softmax(wei, dim=-1)
out = wei @ v
```

### 4. Attention에 대한 6가지 중요한 노트 (01:11:38 - 01:19:10)
카파시는 코드를 작성하며 다음 6가지 핵심 통찰을 짚고 넘어갑니다.

1. **Attention as communication:** 그래프 관점에서 각 노드(토큰) 간의 '정보 교환(Information routing)' 메커니즘입니다.
2. **Attention operates over sets:** 어텐션 자체는 공간이나 순서 개념이 없는 집합 연산입니다. (이것이 Positional Encoding이 필수적인 이유입니다.)
3. **No communication across batch dimension:** 하나의 배치(Batch) 내에 속한 데이터(문장들)는 섞이지 않고 철저히 독립적으로 처리됩니다.
4. **Encoder vs Decoder blocks:**
   - **Decoder (Autoregressive):** 생성 모델(GPT). 미래 정보를 보면 안 되기 때문에 하삼각행렬 마스킹(`tril`)을 사용합니다.
   - **Encoder:** 문맥 이해 모델(BERT). 마스킹을 제거하여 모든 토큰이 서로 소통하도록 합니다.
5. **Self-Attention vs Cross-Attention:** Q, K, V의 출처가 동일한 시퀀스에서 오면 Self-Attention, K와 V가 외부(예: 번역할 원본 문장)에서 오고 Q만 내 시퀀스에서 오면 Cross-Attention입니다.
6. **Scaled Dot-Product Attention:** 모델의 Embedding Dimension($d_k$)이 커질수록 Q와 K 내적 값의 분산이 커져 Softmax가 포화(Saturate)되는 문제가 생깁니다. 이를 막기 위해 $\sqrt{d_k}$ 로 나누어 분산을 1로 맞추는 스케일링 기법입니다.
   $$ \text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V $$

### 5. Transformer Architecture 완성 (01:19:11 - 01:37:37)
단일 어텐션을 확장하여 완전한 트랜스포머 블록을 만듭니다.

- **01:19:11 Multi-head Attention:** 단일 Attention 연산을 여러 개(`n_head`)로 쪼개어 병렬(Parallel)로 수행한 뒤 결과를 이어 붙여(concatenate) 반환합니다. 이를 통해 모델이 문맥의 "다양한 특징"을 동시에 잡아내도록 합니다.
- **01:22:46 Feedforward Layer:** Attention 블록에서 토큰 간의 '정보 교환'이 끝났으므로, 이제 각 토큰이 교환받은 정보를 개별적으로 곱씹어 볼(Compute) 수 있도록 비선형성을 띤 2층 선형 신경망(MLP) 레이어를 추가합니다.
- **01:24:25 Residual Connections (Skip Connections):** 딥러닝에서 모델이 깊어질수록 발생하는 기울기 소실(Vanishing Gradient)을 방지합니다. `x = x + self.attention(x)` 형태로 원래의 입력을 그대로 전달하는 고속도로(Shortcut)를 뚫어주어, 학습 초기에는 원본 데이터가 흐르다 점차 잔차(Residual) 위주로 학습되게 합니다.

```python
class Block(nn.Module):
    def __init__(self, n_embd, n_head):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedForward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))    # Residual + Pre-Norm
        x = x + self.ffwd(self.ln2(x))  # Residual + Pre-Norm
        return x
```

- **01:28:09 Layer Normalization:** 각 토큰(행) 단위로 정규화를 수행하여 학습 안정성을 극대화합니다. 최신 GPT 구조에서는 LayerNorm이 Attention과 FeedForward **이전**에 적용되는 Pre-Norm 구조를 띕니다.
- **01:32:09 Scaling Up:** 모델의 구조가 완성되었으므로, 레이어 깊이(`n_layer`), 임베딩 차원 수(`n_embd`) 등을 늘려 모델 크기를 본격적으로 키웁니다.
- **01:34:53 Dropout:** 과적합(Overfitting)을 막기 위해 훈련 과정에서 랜덤하게 일부 뉴런의 연결을 끊는 Dropout을 정규화 기법으로 추가합니다.

최종적으로 이 모델이 셰익스피어 문체와 유사한 그럴싸한 텍스트를 무한정 생성하는 능력을 보여줍니다.

### 6. ChatGPT 훈련 방식에 대한 개요 (01:37:38 - 01:58:48)
현재 우리가 아는 "ChatGPT"가 되기까지의 전체 파이프라인을 짚어줍니다.

- **Pre-training (사전 학습):** 본 강의에서 직접 코딩한 단계입니다. 인터넷의 방대한 텍스트 데이터를 긁어모아 '단순히 다음 단어를 잘 예측'하는 거대한 언어 모델(Base model)을 만듭니다.
- **Fine-tuning (미세 조정):** 베이스 모델은 인터넷 문서를 "이어쓰기"만 할 뿐, 사람의 질문에 "대답"하는 챗봇이 아닙니다. SFT(Supervised Fine-Tuning)를 통해 질문-답변 형태의 양질의 데이터를 학습시키고, RLHF(Reinforcement Learning from Human Feedback)로 인간의 선호도에 맞춰 보상을 줌으로써 최종적인 어시스턴트(Assistant) 모델이 완성됩니다.

---

## 독자적인 GPT 프로젝트 진행을 위한 제안

위 강의 내용을 기반으로 "나만의 GPT" 프로젝트를 진행하고자 하신다면, 다음과 같은 순서로 진행해 보시길 권장합니다.

1. **커스텀 데이터(Dataset) 준비:**
   모델 학습에 사용할 자신만의 텍스트 데이터를 준비합니다. 셰익스피어 데이터 외에도, 나무위키 덤프 텍스트, 코드 파일의 모음집, 또는 본인이 좋아하는 작가의 텍스트 등을 사용하여 나만의 특색 있는 데이터셋을 만들어 보세요.

2. **가장 단순한 토크나이저 구현 (Character-level):**
   강의처럼 초기에는 문자(Character) 단위 토크나이저로 구현하여 Vocabulary 사이즈를 최소한(약 60~100)으로 유지하세요. 추후 모델 구조에 익숙해지면 OpenAI의 `tiktoken` (BPE 방식) 등을 적용해보고 "생성되는 텍스트의 응집력"이 얼마나 달라지는지 비교해 보는 것이 좋습니다.

3. **PyTorch 기반 Bigram 베이스라인 작성:**
   전체 코드를 무작정 복사하기 전, PyTorch의 텐서 차원(Shape) 조작(`view`, `transpose` 등)과 모델의 기본 학습 루프 (Forward → Loss → Backward → Step)를 직접 손으로 타이핑하며 완벽하게 숙지하세요.

4. **한 겹씩 Transformer 구성 요소 쌓기:**
   카파시의 강의 흐름을 그대로 따라가세요.
   `Self-Attention 1개` $\rightarrow$ `Multi-head Attention으로 병렬화` $\rightarrow$ `Feed Forward 추가` $\rightarrow$ `Residual Connection 도입` $\rightarrow$ `Layer Norm 추가`.
   새로운 모듈을 하나 추가할 때마다 **Loss(손실값) 곡선이 이전보다 얼마나 더 안정적으로, 더 낮게 떨어지는지 확인**하는 경험이 매우 중요합니다.

5. **하이퍼파라미터 튜닝 (Hyperparameter Tuning):**
   마지막으로 다음 파라미터들을 조절해보며 모델 사이즈와 VRAM 메모리 용량 사이의 줄다리기를 경험해 보세요.
   - `block_size`: 모델이 한 번에 볼 수 있는 최대 문맥의 길이
   - `n_embd`: 단어 하나가 가지는 의미 차원의 크기
   - `n_head`: 동시에 문맥을 바라보는 관점의 개수 (단, `n_embd % n_head == 0` 이어야 함)
   - `n_layer`: 모델의 깊이 (블록 개수)
