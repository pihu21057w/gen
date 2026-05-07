# Getting Started Guide - Dataset Generation Pipeline

## 🎯 Overview

This guide will help you get started with the dataset generation pipeline in 10 minutes.

## ⏱️ 10-Minute Quick Start

### Step 1: Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/hpp.git
cd hpp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup Model Access (3 minutes)

```bash
# Login to Hugging Face (for Llama-2 access)
python setup_hf.py --login

# Follow the prompts to authenticate
# Visit https://huggingface.co/meta-llama/Llama-2-7b-hf to accept license
```

### Step 3: Add Your Data (2 minutes)

Place your documents in the `data/` folder:

```bash
# Copy your files
cp /path/to/document.pdf data/
cp /path/to/article.txt data/
cp /path/to/guide.md data/

# Or download a sample
wget https://example.com/sample.pdf -O data/sample.pdf
```

### Step 4: Generate Dataset (3 minutes)

```bash
# Show model recommendations
python main.py --recommendations

# Process documents
python main.py --source data/ --output outputs/dataset.jsonl

# Check progress
tail -f pipeline.log

# View results
python main.py --stats outputs/dataset.jsonl
```

---

## 🖥️ Google Colab Setup (Fastest!)

### Colab Notebook Steps

```python
# Cell 1: Clone and setup
!git clone https://github.com/yourusername/hpp.git
%cd hpp
exec(open('setup_colab.py').read())

# Cell 2: Setup environment
setup_colab_environment()

# Cell 3: Login to Hugging Face
exec(open('setup_hf.py').read())
authenticate()

# Cell 4: Upload document (or mount Drive)
from google.colab import files
uploaded = files.upload()
# Or mount Drive: drive.mount('/content/drive')

# Cell 5: Generate dataset
from src.pipeline import create_pipeline

pipeline = create_pipeline('configs/config.yaml')
pipeline.process_document('sample.pdf', num_conversations=10)

# Cell 6: Download results
from google.colab import files
files.download('generated_dataset.jsonl')
```

---

## 📊 Understanding the Output

### Dataset File Structure

```json
{
  "dataset_id": 0,
  "document_id": "my_pdf",
  "source": "data/document.pdf",
  "type": "multi_turn",
  "template": "explanation_follow_up",
  "system": "You are an expert educator.",
  "has_reasoning": true,
  "created_at": "2024-01-15T10:30:00",
  "conversations": [
    {"role": "user", "content": "Explain X"},
    {"role": "assistant", "content": "Let me think through this..."},
    {"role": "user", "content": "Can you provide an example?"},
    {"role": "assistant", "content": "Sure! For example..."}
  ]
}
```

### Interpreting Statistics

```
Total Entries: 1500         # Total conversation pairs
Multi-turn: 750              # Complex conversations (5-8 turns)
Single-turn: 750             # Simple Q&A pairs
With reasoning: 900 (60%)    # Reasoning enabled responses
```

---

## 🔧 Configuration Quick Reference

Edit `configs/config.yaml` for common changes:

```yaml
# Speed vs Quality Tradeoff
model:
  name: "meta-llama/Llama-2-3b-hf"    # Faster, lower quality
  # name: "meta-llama/Llama-2-7b-hf"  # Balanced (recommended)
  # name: "meta-llama/Llama-2-13b-hf" # Better quality, slower

# Conversation quantity
dataset:
  num_conversations_per_doc: 5        # More = larger dataset but slower

# Text cleaning
processing:
  remove_urls: true                   # Remove links
  remove_images: true                 # Remove image references
  keep_math: true                     # Keep math expressions

# Output format
conversation:
  types: ["multi_turn", "single_turn"]  # Conversation types
  include_reasoning: true              # Add reasoning to responses
```

---

## ❓ FAQ

### Q: How long does it take to process 1 document?

**A:** Depends on model and document length:
- Llama-2-3B: ~2-5 minutes per document (5 conversations)
- Llama-2-7B: ~5-10 minutes per document (5 conversations)
- On Colab T4: ~10-15 minutes typically

### Q: How much VRAM do I need?

**A:** 
- Llama-2-3B: 8GB (works on Colab T4)
- Llama-2-7B: 14GB (works on Colab T4 with float16)
- Llama-2-13B: 24GB (works on RTX 3090)

### Q: Can I process from a URL?

**A:** Yes! Just pass the URL:
```bash
python main.py --source "https://example.com/article" --output dataset.jsonl
```

### Q: How do I use the generated dataset?

**A:** Load and use with your training framework:
```python
from src.utils import JSONLHandler

dataset = JSONLHandler.read_jsonl('generated_dataset.jsonl')

# Use with Hugging Face Trainer, LLaMA Factory, Axolotl, etc.
# Example for Trainer:
# from transformers import Trainer
# trainer = Trainer(model=model, train_dataset=dataset)
```

### Q: What if generation fails?

**A:** Check the logs:
```bash
tail -f pipeline.log  # View logs
grep ERROR pipeline.log  # Find errors
```

### Q: How do I continue from where I left off?

**A:** The pipeline automatically appends to existing `generated_dataset.jsonl`:
```bash
# Just run again with more documents
python main.py --source data/more_documents/ --output outputs/dataset.jsonl
# It will append, not overwrite!
```

---

## 🚀 Next Steps

### 1. Explore Configuration Options

See full configuration documentation:
```bash
cat configs/config.yaml  # Read the configuration file
```

### 2. Try Different Models

```bash
# Try 3B model (faster)
python main.py --source data/ --model "meta-llama/Llama-2-3b-hf"

# Try Mistral (faster alternative)
python main.py --source data/ --model "mistralai/Mistral-7B-v0.1"
```

### 3. Validate Your Dataset

```bash
# Check dataset statistics
python main.py --stats outputs/dataset.jsonl

# Validate quality
python main.py --validate outputs/dataset.jsonl
```

### 4. Scale Up

```bash
# Process large batches
python main.py --source data/large_folder/ --batch --conversations 10
```

---

## 💡 Pro Tips

1. **Start Small**: Process 1-2 documents first to understand the output

2. **Monitor GPU**: While running:
   ```bash
   watch -n 1 nvidia-smi  # Linux/Mac
   ```

3. **Use Float16**: Saves 50% VRAM with minimal quality loss
   ```yaml
   model:
     dtype: "float16"
   ```

4. **Batch Multiple Documents**: Much more efficient than one at a time

5. **Check Logs Regularly**:
   ```bash
   tail -f pipeline.log
   ```

6. **Use Checkpoints**: Pipeline automatically saves checkpoints

---

## ⚠️ Common Issues

### "CUDA out of memory"

```bash
# Use smaller model
python main.py --source data/ --model "meta-llama/Llama-2-3b-hf"

# Or reduce batch size in config.yaml
```

### "Authentication failed"

```bash
# Relogin
python setup_hf.py --login

# Or set token
export HF_TOKEN=hf_xxxxx
```

### "No module named 'torch'"

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📖 Documentation

- **Full README**: [README.md](README.md)
- **Configuration**: [configs/config.yaml](configs/config.yaml)
- **Examples**: [examples.py](examples.py)
- **API Reference**: See docstrings in src/

---

## 🎓 Learning Resources

- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Llama-2 Models](https://huggingface.co/meta-llama)
- [JSONL Format](https://jsonlines.org/)
- [Fine-tuning Guide](https://huggingface.co/docs/transformers/training)

---

## 🆘 Getting Help

1. Check `pipeline.log` for detailed error messages
2. Run with `--verbose` flag: `python main.py --source data/ --verbose`
3. Review configuration in `configs/config.yaml`
4. See troubleshooting in [README.md](README.md)

---

**Ready to generate your first dataset? Run:**

```bash
python main.py --recommendations  # See model options
python main.py --source data/ --output outputs/dataset.jsonl  # Start generating!
```

Happy dataset generation! 🚀
