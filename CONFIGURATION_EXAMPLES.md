# Sample Configuration Files

This document shows various configuration examples for different scenarios.

## configs/config_colab_t4.yaml

For Google Colab with T4 GPU (recommended default):

```yaml
model:
  name: "meta-llama/Llama-2-7b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9

dataset:
  output_format: "jsonl"
  output_file: "colab_dataset.jsonl"
  batch_size: 4
  num_conversations_per_doc: 5

conversation:
  types: ["multi_turn", "single_turn"]
  include_reasoning: true
  reasoning_format: "chain_of_thought"

processing:
  remove_urls: true
  remove_emails: true
  remove_html_tags: true
  remove_images: true
  keep_math: true
  chunk_size: 2000
  chunk_overlap: 200
  min_text_length: 100

runtime:
  append_mode: true
  checkpoint_interval: 5
  max_workers: 4
  seed: 42

logging:
  level: "INFO"
  log_file: "pipeline.log"
  console_output: true
```

## configs/config_3b_fast.yaml

For fast generation with Llama-2-3B:

```yaml
model:
  name: "meta-llama/Llama-2-3b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 1024
  temperature: 0.7
  top_p: 0.9

dataset:
  output_format: "jsonl"
  output_file: "fast_dataset.jsonl"
  batch_size: 8
  num_conversations_per_doc: 10  # More since faster

conversation:
  types: ["single_turn", "multi_turn"]  # Prioritize single-turn
  include_reasoning: false  # Disable for speed
  reasoning_format: "chain_of_thought"

processing:
  remove_urls: true
  remove_emails: true
  remove_html_tags: true
  remove_images: true
  keep_math: false  # Disable for speed
  chunk_size: 1500
  chunk_overlap: 150
  min_text_length: 50  # Lower threshold

runtime:
  append_mode: true
  checkpoint_interval: 10
  max_workers: 4
  seed: 42

logging:
  level: "WARNING"  # Less logging for speed
  log_file: "pipeline.log"
  console_output: false
```

## configs/config_high_quality.yaml

For RTX 3090+ with focus on quality:

```yaml
model:
  name: "meta-llama/Llama-2-13b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.8
  top_p: 0.95

dataset:
  output_format: "jsonl"
  output_file: "high_quality_dataset.jsonl"
  batch_size: 8
  num_conversations_per_doc: 8  # More conversations

conversation:
  types: ["multi_turn", "single_turn"]
  include_reasoning: true
  reasoning_format: "step_by_step"

processing:
  remove_urls: true
  remove_emails: true
  remove_html_tags: true
  remove_images: true
  keep_math: true
  chunk_size: 2500  # Larger chunks for context
  chunk_overlap: 300
  min_text_length: 200  # Higher quality threshold

runtime:
  append_mode: true
  checkpoint_interval: 3
  max_workers: 6
  seed: 42

logging:
  level: "DEBUG"  # Full logging for quality checks
  log_file: "pipeline_hq.log"
  console_output: true
```

## configs/config_cpu.yaml

For CPU-only execution (very slow):

```yaml
model:
  name: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
  device: "cpu"
  dtype: "float32"
  max_tokens: 512
  temperature: 0.7
  top_p: 0.9

dataset:
  output_format: "jsonl"
  output_file: "cpu_dataset.jsonl"
  batch_size: 1  # CPU can only handle 1
  num_conversations_per_doc: 2  # Minimal

conversation:
  types: ["single_turn"]  # Only single-turn for speed
  include_reasoning: false
  reasoning_format: "chain_of_thought"

processing:
  remove_urls: true
  remove_emails: true
  remove_html_tags: true
  remove_images: true
  keep_math: false
  chunk_size: 1000
  chunk_overlap: 100
  min_text_length: 50

runtime:
  append_mode: true
  checkpoint_interval: 20
  max_workers: 1
  seed: 42

logging:
  level: "WARNING"
  log_file: "pipeline_cpu.log"
  console_output: true
```

## configs/config_web_scraping.yaml

Optimized for web content scraping:

```yaml
model:
  name: "meta-llama/Llama-2-7b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9

dataset:
  output_format: "jsonl"
  output_file: "web_dataset.jsonl"
  batch_size: 4
  num_conversations_per_doc: 5

conversation:
  types: ["multi_turn", "single_turn"]
  include_reasoning: true
  reasoning_format: "chain_of_thought"

processing:
  remove_urls: false  # Keep URLs from web content
  remove_emails: false  # Keep contact info
  remove_html_tags: true
  remove_images: true
  keep_math: true
  chunk_size: 2000
  chunk_overlap: 200
  min_text_length: 100

data_sources:
  web:
    timeout: 60  # Longer timeout for slow websites
    retry_attempts: 5
    headers:
      User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    content_selectors:
      - "main"
      - "article"
      - ".content"
      - ".post-content"
      - ".page-content"
    exclude_selectors:
      - "nav"
      - "footer"
      - ".ads"
      - ".sidebar"
      - ".comments"

runtime:
  append_mode: true
  checkpoint_interval: 5
  max_workers: 2  # Limited for web requests
  seed: 42

logging:
  level: "INFO"
  log_file: "web_scraping.log"
  console_output: true
```

## configs/config_academic.yaml

For academic/research papers and technical documents:

```yaml
model:
  name: "meta-llama/Llama-2-7b-hf"
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.5  # Lower temp for precision
  top_p: 0.9

dataset:
  output_format: "jsonl"
  output_file: "academic_dataset.jsonl"
  batch_size: 4
  num_conversations_per_doc: 8

conversation:
  types: ["multi_turn"]  # Focus on complex discussions
  include_reasoning: true
  reasoning_format: "step_by_step"

processing:
  remove_urls: false
  remove_emails: false
  remove_html_tags: true
  remove_images: false  # Keep scientific figures
  keep_math: true  # CRITICAL: Keep equations
  chunk_size: 2500  # Larger chunks for context
  chunk_overlap: 300
  min_text_length: 300

pdf:
  extract_images: true  # Extract for context
  extract_tables: true  # Tables are important
  use_ocr: true  # Handle scanned papers

runtime:
  append_mode: true
  checkpoint_interval: 3
  max_workers: 2
  seed: 42

logging:
  level: "DEBUG"
  log_file: "academic_pipeline.log"
  console_output: true
```

## configs/config_minimal.yaml

Bare minimum configuration (uses all defaults):

```yaml
model:
  name: "meta-llama/Llama-2-7b-hf"
  device: "cuda"
  dtype: "float16"

dataset:
  output_file: "dataset.jsonl"
  num_conversations_per_doc: 5

processing:
  min_text_length: 100

logging:
  level: "INFO"
```

---

## Usage

```bash
# Use specific configuration
python main.py --config configs/config_colab_t4.yaml --source data/ --output outputs/dataset.jsonl

# Use 3B for fast generation
python main.py --config configs/config_3b_fast.yaml --source data/ --output outputs/fast.jsonl

# Use 13B for high quality (if you have 3090+)
python main.py --config configs/config_high_quality.yaml --source data/ --output outputs/hq.jsonl

# Use CPU configuration
python main.py --config configs/config_cpu.yaml --source data/ --output outputs/cpu.jsonl

# Use web scraping config
python main.py --config configs/config_web_scraping.yaml --source "https://example.com"

# Academic papers
python main.py --config configs/config_academic.yaml --source data/papers/
```

---

## Configuration Comparison

| Config | Model | Speed | Quality | VRAM | Best For |
|--------|-------|-------|---------|------|----------|
| colab_t4 | 7B | Medium | High | 14GB | General use (DEFAULT) |
| 3b_fast | 3B | Very Fast | Medium | 8GB | Large datasets |
| high_quality | 13B | Slow | Very High | 24GB | Premium quality |
| cpu | 1B | Very Slow | Low | 2GB | Testing only |
| web_scraping | 7B | Medium | High | 14GB | Web content |
| academic | 7B | Medium | Very High | 14GB | Research papers |
| minimal | 7B | Medium | High | 14GB | Simplicity |

---

## Tips for Configuration

1. **Start with defaults**: `config.yaml` works for most cases

2. **Modify by scenario**: Choose a configuration matching your use case

3. **Test first**: Generate 1-2 documents before full batch

4. **Monitor logs**: Check `pipeline.log` during generation

5. **Adjust temperature**: 
   - Lower (0.3-0.5): More deterministic
   - Higher (0.7-0.9): More creative

6. **Adjust conversations**:
   - More = larger dataset but slower
   - Fewer = faster but less data

7. **Memory issues**: Use 3B model or float32

---

Last Updated: January 2024
