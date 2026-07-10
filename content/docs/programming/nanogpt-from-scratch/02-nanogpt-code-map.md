---
title: "강의 타임라인 × nanoGPT 코드 매핑"
date: 2026-05-14T08:14:17+09:00
draft: false
tags: ["Deep Learning", "LLM", "GPT", "PyTorch", "Transformer", "nanoGPT"]
categories: ["programming"]
description: "Karpathy 강의의 각 타임라인이 nanoGPT 레포의 어떤 파일, 어떤 라인에 해당하는지 직접 매핑합니다."
---

## 강의 타임라인 × nanoGPT 코드 매핑

강의에서 한 단계씩 쌓아 올린 개념들이 [nanoGPT](https://github.com/karpathy/nanoGPT) 레포의 실제 코드 어디에 녹아 있는지 정리합니다. 강의를 보며 직접 구현할 때 "최종 버전은 어떻게 생겼지?"를 빠르게 확인하는 용도로 활용하세요.

---

## 1. 데이터 전처리 (00:00:00 - 00:22:10)

### `data/shakespeare_char/prepare.py`

| 강의 내용 | 파일 | 라인 | 설명 |
|-----------|------|------|------|
| Tiny Shakespeare 데이터 로드 | `prepare.py` | 12–17 | URL에서 `input.txt` 다운로드 |
| Character-level 어휘 구성 | `prepare.py` | 19–27 | `sorted(set(text))`로 vocab 65개 생성 |
| `stoi` / `itos` 딕셔너리 | `prepare.py` | 29–35 | `encode` / `decode` 함수 |
| Train / Val Split (90/10) | `prepare.py` | 37–46 | `train.bin` / `val.bin` 저장 |
| 메타 정보 저장 | `prepare.py` | 54–61 | `meta.pkl`에 vocab_size, stoi, itos 저장 |

강의에서는 `stoi`/`itos`를 노트북 안에 직접 만들지만, nanoGPT에서는 `meta.pkl`로 직렬화하여 학습 시 `train.py`가 불러와 `vocab_size`를 자동으로 설정합니다 (`train.py` 133–144).

### `train.py` — `get_batch`

```python
# train.py L114–131
def get_batch(split):
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy((data[i+1:i+block_size+1]).astype(np.int64)) for i in ix])
    x, y = x.to(device), y.to(device)
    return x, y
```

강의의 `get_batch`와 구조는 동일하지만, nanoGPT는 `np.memmap`으로 대용량 데이터를 메모리 효율적으로 읽습니다.

---

## 2. Bigram 모델 (00:22:11 - 00:42:12)

nanoGPT 레포에 Bigram 모델 자체는 없습니다. 강의에서 Bigram은 GPT 구조로 가기 위한 **디딤돌** 역할이며, 최종 nanoGPT는 처음부터 Transformer 기반입니다.

Bigram 모델의 핵심인 `nn.Embedding` + Cross Entropy Loss 패턴은 nanoGPT의 GPT 클래스 안에서 그대로 이어집니다.

| 강의 내용 | 파일 | 라인 | 설명 |
|-----------|------|------|------|
| Token Embedding (`nn.Embedding`) | `model.py` | 127 | `wte = nn.Embedding(vocab_size, n_embd)` |
| Cross Entropy Loss 계산 | `model.py` | 170–193 | `GPT.forward()` 내 `F.cross_entropy` |
| AdamW 옵티마이저 | `model.py` | 263–287 | `configure_optimizers()` |

---

## 3. Self-Attention (00:42:13 - 01:11:37)

### `model.py` — `CausalSelfAttention` (L29–76)

강의에서 v1(for loop) → v2(tril) → v3(softmax) → v4(Q, K, V) 순으로 점진적으로 발전시킨 Attention이 이 클래스에 최종 형태로 담겨 있습니다.

| 강의 내용 | 파일 | 라인 | 설명 |
|-----------|------|------|------|
| Q, K, V 프로젝션 | `model.py` | 35, 56–59 | `c_attn` 하나로 Q/K/V를 한 번에 계산 후 `.split()` |
| Scaled Dot-Product | `model.py` | 67 | `(q @ k.transpose(-2,-1)) * (1.0 / math.sqrt(k.size(-1)))` |
| Causal Masking (`tril`) | `model.py` | 49–50, 68 | `register_buffer("bias", torch.tril(...))` + `masked_fill` |
| Softmax | `model.py` | 69 | `F.softmax(att, dim=-1)` |
| Attention Dropout | `model.py` | 39, 70 | `attn_dropout` |
| Output 프로젝션 | `model.py` | 37, 75 | `c_proj` + `resid_dropout` |

**강의와 nanoGPT의 주요 차이점:**

1. **Q/K/V 계산 방식:** 강의에서는 `nn.Linear`를 3개 따로 만들지만, nanoGPT는 `nn.Linear(n_embd, 3 * n_embd)` 하나로 합쳐 `.split()`으로 나눕니다. 연산 효율을 위한 선택입니다.
2. **Flash Attention:** nanoGPT는 PyTorch 2.0 이상에서 `F.scaled_dot_product_attention`을 사용합니다 (L62–64). 강의의 수동 구현 대비 훨씬 빠릅니다.
3. **Multi-head 처리:** 강의에서는 `Head` 클래스를 여러 개 만들어 `MultiHeadAttention`으로 합치지만, nanoGPT는 `CausalSelfAttention` 하나 안에서 `view` + `transpose`로 배치 차원을 활용해 모든 헤드를 한 번에 계산합니다.

```python
# nanoGPT의 멀티헤드: view로 헤드 차원 분리 후 병렬 계산
k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)  # (B, nh, T, hs)
q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
```

### Positional Encoding

| 강의 내용 | 파일 | 라인 | 설명 |
|-----------|------|------|------|
| Position Embedding | `model.py` | 128, 170–175 | `wpe = nn.Embedding(block_size, n_embd)`, forward에서 `pos_emb` 더하기 |

---

## 4. Attention 6가지 노트 (01:11:38 - 01:19:10)

코드로 직접 나타나는 항목만 매핑합니다.

| 노트 | 파일 | 라인 | 설명 |
|------|------|------|------|
| Decoder (Causal Masking) | `model.py` | 49–50 | `torch.tril`로 미래 토큰 차단 |
| No cross-batch communication | `train.py` | 114–131 | `get_batch`에서 각 시퀀스가 독립적으로 샘플링됨 |
| Scaled Dot-Product | `model.py` | 67 | `* (1.0 / math.sqrt(k.size(-1)))` |

---

## 5. Transformer Architecture 완성 (01:19:11 - 01:37:37)

### `model.py` — `Block` (L94–106)

```python
class Block(nn.Module):
    def __init__(self, config):
        self.ln_1 = LayerNorm(config.n_embd, bias=config.bias)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = LayerNorm(config.n_embd, bias=config.bias)
        self.mlp = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))   # Residual + Pre-Norm
        x = x + self.mlp(self.ln_2(x))    # Residual + Pre-Norm
        return x
```

| 강의 내용 | 파일 | 라인 | 설명 |
|-----------|------|------|------|
| Multi-head Attention | `model.py` | 29–76 | `CausalSelfAttention` (헤드 분리를 view로 처리) |
| Feedforward (MLP) | `model.py` | 78–92 | `MLP` 클래스, GELU 활성화, 4배 확장 후 축소 |
| Residual Connection | `model.py` | 104–105 | `x = x + self.attn(...)` / `x = x + self.mlp(...)` |
| Layer Normalization (Pre-Norm) | `model.py` | 18–27, 98–100 | `LayerNorm` 클래스, Attention/MLP 이전에 적용 |
| Dropout | `model.py` | 39–40, 85, 129 | Attention, MLP, Embedding 각각에 적용 |

### `model.py` — `GPTConfig` (L108–116)

강의에서 `Scaling Up` 단계에서 직접 조절하는 하이퍼파라미터들이 이 dataclass에 모여 있습니다.

```python
@dataclass
class GPTConfig:
    block_size: int = 1024   # 강의: context_length
    vocab_size: int = 50304
    n_layer: int = 12        # 강의: Scaling Up
    n_head: int = 12         # 강의: Multi-head
    n_embd: int = 768        # 강의: Scaling Up
    dropout: float = 0.0
    bias: bool = True
```

---

## 6. 학습 루프 (train.py)

강의에서 `AdamW`로 학습하는 부분이 `train.py`에 프로덕션 수준으로 구현되어 있습니다.

| 강의 내용 | 파일 | 라인 | 설명 |
|-----------|------|------|------|
| AdamW 옵티마이저 설정 | `model.py` | 263–287 | weight decay 그룹 분리 (`configure_optimizers`) |
| 학습/검증 Loss 평가 | `train.py` | 215–228 | `estimate_loss()` — no-grad eval 루프 |
| 학습률 스케줄링 | `train.py` | 230–242 | Linear warmup + Cosine decay (`get_lr`) |
| 메인 학습 루프 | `train.py` | 249–333 | forward → backward → grad clip → step |
| 텍스트 생성 (`generate`) | `model.py` | 305–330 | top-k 샘플링, temperature 지원 |

---

## 전체 요약 매핑 테이블

| 강의 타임라인 | nanoGPT 파일 | 핵심 클래스 / 함수 |
|---------------|-------------|-------------------|
| 데이터 로드 & 토크나이저 | `data/shakespeare_char/prepare.py` | `encode`, `decode`, `meta.pkl` |
| Data Loader (get_batch) | `train.py` L114–131 | `get_batch()` |
| Bigram → Token Embedding | `model.py` L127 | `GPT.transformer.wte` |
| Q, K, V Attention | `model.py` L29–76 | `CausalSelfAttention` |
| Causal Masking (tril) | `model.py` L49–50, 68 | `register_buffer("bias", ...)` |
| Positional Encoding | `model.py` L128, 170–175 | `GPT.transformer.wpe` |
| Multi-head Attention | `model.py` L52–72 | `CausalSelfAttention.forward` |
| Feedforward (MLP) | `model.py` L78–92 | `MLP` |
| Residual Connection | `model.py` L104–105 | `Block.forward` |
| Layer Normalization | `model.py` L18–27, 98–100 | `LayerNorm`, `Block` |
| Dropout | `model.py` L39–40, 85, 129 | 각 모듈 내 `nn.Dropout` |
| 하이퍼파라미터 | `model.py` L108–116 | `GPTConfig` |
| AdamW & 학습 루프 | `train.py` L249–333 | `configure_optimizers`, 메인 루프 |
| 텍스트 생성 | `model.py` L305–330 | `GPT.generate` |
