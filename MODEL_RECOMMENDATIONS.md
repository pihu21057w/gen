# Model Recommendations and Selection Guide

## 🎯 Quick Recommendation

**For Google Colab T4 GPU (Most Common):**
```
USE: meta-llama/Llama-2-7b-hf
- Best quality-to-speed ratio
- ~14GB VRAM with float16
- ~2-3 conversations per minute
- Excellent for fine-tuning
```

---

## 📊 Detailed Comparison

### By Hardware

#### 1. Google Colab T4 GPU (15GB VRAM)

| Model | Size | Speed | Quality | VRAM | Recommended |
|-------|------|-------|---------|------|-------------|
| Llama-2-3B | 3B | ⚡⚡⚡⚡⚡ Fast | ⭐⭐⭐ | 8GB | ✓ For speed |
| Llama-2-7B | 7B | ⚡⚡⚡ Medium | ⭐⭐⭐⭐ | 14GB | **✓ RECOMMENDED** |
| Mistral-7B | 7B | ⚡⚡⚡⚡ Fast | ⭐⭐⭐⭐ | 14GB | ✓ Fast alternative |
| Llama-2-13B | 13B | ⚡⚡ Slow | ⭐⭐⭐⭐⭐ | 24GB | ✗ Too large |

#### 2. High-End GPU (RTX 3090 - 24GB VRAM)

| Model | Size | Speed | Quality | Recommended |
|-------|------|-------|---------|-------------|
| Llama-2-7B | 7B | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ✓ Good balance |
| Llama-2-13B | 13B | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | **✓ RECOMMENDED** |
| Llama-2-70B | 70B | ⚡ Very slow | ⭐⭐⭐⭐⭐⭐ | ⚠️ Possible with 8-bit |

#### 3. CPU-Only

| Model | Size | Speed | Quality | Recommended |
|-------|------|-------|---------|-------------|
| TinyLlama-1.1B | 1B | 🐢 Very slow | ⭐⭐ | ✓ Only option |
| Llama-2-3B | 3B | 🐢🐢 Slow | ⭐⭐⭐ | ✓ If patient |

---

## 🏆 Model Details

### Meta Llama-2 Models

#### Llama-2-3B (meta-llama/Llama-2-3b-hf)
- **Use Case**: Speed-focused, limited hardware
- **Pros**: 
  - Fastest inference
  - ~8GB VRAM requirement
  - Still decent quality for basic tasks
- **Cons**: 
  - Lower reasoning capability
  - Simpler responses
- **Best For**: Large-scale dataset generation on budget

#### Llama-2-7B (meta-llama/Llama-2-7b-hf) ⭐ RECOMMENDED
- **Use Case**: General purpose, best for most users
- **Pros**:
  - Great balance of speed and quality
  - ~14GB VRAM (fits on T4)
  - Good reasoning and instruction following
  - Widely supported
- **Cons**:
  - Slower than 3B (but still reasonable)
- **Best For**: Production dataset generation

#### Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
- **Use Case**: Instruction-following, conversational
- **Pros**:
  - Optimized for chat/conversations
  - Better instruction following
  - Natural dialogue
- **Cons**:
  - Slightly larger model
- **Best For**: Multi-turn conversations

#### Llama-2-13B (meta-llama/Llama-2-13b-hf)
- **Use Case**: High-quality generation
- **Pros**:
  - Better reasoning
  - More nuanced responses
  - Better for complex tasks
- **Cons**:
  - ~24GB VRAM needed
  - Slower inference
  - Won't fit on Colab T4
- **Best For**: High-quality datasets with good GPU

### Mistral Models

#### Mistral-7B (mistralai/Mistral-7B-v0.1)
- **Use Case**: Fast 7B alternative
- **Pros**:
  - Faster than Llama-2-7B
  - Good quality
  - Better inference speed
- **Cons**:
  - Less well-tested
  - Fewer resources online
- **Best For**: When speed is priority

### TinyLlama

#### TinyLlama-1.1B (TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- **Use Case**: CPU-only, minimal resources
- **Pros**:
  - ~1.1B parameters
  - Works on CPU
  - Low VRAM needs
- **Cons**:
  - Very slow (~5-10 tokens/sec)
  - Lower quality
- **Best For**: Testing on CPU, prototyping

---

## 💡 Selection Guide

### "What model should I use?"

**Ask yourself:**

1. **What hardware do I have?**
   - Colab T4 → Llama-2-7B (recommended)
   - RTX 3090+ → Llama-2-13B
   - CPU only → TinyLlama-1.1B

2. **What's my priority?**
   - Speed → Mistral-7B or Llama-2-3B
   - Quality → Llama-2-13B or Llama-2-7B
   - Balance → Llama-2-7B ✓

3. **How much data do I need?**
   - Small dataset (<10K) → Any model
   - Medium (10K-100K) → Llama-2-7B
   - Large (100K+) → Llama-2-3B (faster)

4. **What's the use case?**
   - General fine-tuning → Llama-2-7B
   - Specific domain → Llama-2-13B (if you have GPU)
   - Chat assistant → Llama-2-7B-Chat

---

## 🚀 Configuration Examples

### Setup for Colab T4

```yaml
model:
  name: "meta-llama/Llama-2-7b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.7

dataset:
  batch_size: 4
  num_conversations_per_doc: 5
```

### Setup for RTX 3090

```yaml
model:
  name: "meta-llama/Llama-2-13b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.7

dataset:
  batch_size: 8
  num_conversations_per_doc: 10
```

### Setup for 3B Fast Generation

```yaml
model:
  name: "meta-llama/Llama-2-3b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.7

dataset:
  batch_size: 8
  num_conversations_per_doc: 10  # Can do more since faster
```

### Setup for CPU

```yaml
model:
  name: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
  device: "cpu"
  dtype: "float32"
  max_tokens: 512
  temperature: 0.7

dataset:
  batch_size: 1
  num_conversations_per_doc: 2
```

---

## 📈 Performance Metrics

### Generation Speed (tokens/second)

| Model | T4 GPU | 3090 GPU | CPU |
|-------|--------|----------|-----|
| 3B | 50-80 | 150-200 | 2-5 |
| 7B | 30-50 | 80-150 | 1-3 |
| 13B | N/A | 40-80 | N/A |

### Memory Usage

| Model | float32 | float16 | int8 |
|-------|---------|---------|------|
| 3B | 12GB | 6GB | 3GB |
| 7B | 28GB | 14GB | 7GB |
| 13B | 52GB | 26GB | 13GB |

### Dataset Generation Time

Generating 100 conversations (with 5 conversations per document):

| Model | Hardware | Time | Quality |
|-------|----------|------|---------|
| 3B | T4 | ~2-3 hours | Good |
| 7B | T4 | ~3-5 hours | Better |
| 13B | 3090 | ~2-3 hours | Best |

---

## ⚠️ Special Considerations

### Model Licensing

- **Llama-2**: Meta license (free for research/commercial with <700M monthly active users)
- **Mistral**: Apache 2.0 (fully open, no restrictions)
- **TinyLlama**: MIT (fully open)

### Download Size

| Model | Size (float16) |
|-------|---|
| 3B | 6GB |
| 7B | 14GB |
| 13B | 26GB |

Make sure you have enough disk space!

### VRAM Requirements

**Rule of thumb**: 2x model size for inference

- 3B model → 6GB VRAM minimum
- 7B model → 14GB VRAM minimum
- 13B model → 26GB VRAM minimum

---

## 🔄 Switching Models

Easy to switch - just edit config or command line:

```bash
# Via config
# Edit configs/config.yaml and set model name

# Via command line
python main.py --source data/ --model "meta-llama/Llama-2-3b-hf" --output out.jsonl

# Multiple configs approach
cp configs/config.yaml configs/config_3b.yaml
# Edit config_3b.yaml
python main.py --config configs/config_3b.yaml --source data/
```

---

## 🎓 When to Use Each Model

### Use Llama-2-7B When:
- ✓ You have T4 GPU (Colab)
- ✓ You want good quality
- ✓ You want reasonable speed
- ✓ You're unsure (this is the safest choice)

### Use Llama-2-3B When:
- ✓ VRAM is limited (<10GB)
- ✓ You need maximum speed
- ✓ You're generating massive datasets
- ✓ Quality is less critical

### Use Llama-2-13B When:
- ✓ You have RTX 3090+ or high-end GPU
- ✓ You need top-tier quality
- ✓ You have plenty of VRAM (24GB+)
- ✓ You're willing to wait longer

### Use Mistral-7B When:
- ✓ You want 7B quality but need more speed
- ✓ You prefer Apache 2.0 license
- ✓ You want an alternative to Llama-2

### Use TinyLlama When:
- ✓ You only have CPU
- ✓ You're testing/prototyping
- ✓ You want minimal resource usage

---

## 📞 Still Unsure?

**For 95% of users: Use `meta-llama/Llama-2-7b-hf`**

It just works well for most scenarios with Colab T4!

---

Last Updated: January 2024
