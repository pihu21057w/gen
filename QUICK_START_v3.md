# Quick Start: Reasoning-Based Generation

## 🎯 Core Concept

```
📖 PDF Text (Answer)
    ↓
❓ AI Generates Questions
    ↓
📝 AI Answers with Reasoning
    ↓
💾 Multi-turn Conversation per Page
```

## ⚡ 5-Minute Setup

### 1. Check Prompts File Exists
```bash
ls -la prompts.yaml
# Should exist with all generation templates
```

### 2. Configure Dataset
```yaml
# configs/config.yaml
dataset:
  prompts_file: "prompts.yaml"  # ← Must point to prompts file
  num_conversations_per_doc: 5   # Questions per page
```

### 3. Run Pipeline
```python
from src.pipeline import create_pipeline

pipeline = create_pipeline('configs/config.yaml')
pipeline.initialize_model()
pipeline.initialize_preprocessor()
pipeline.initialize_dataset_generator()

# Process PDF
pipeline.process_document(
    'data/textbook.pdf',
    num_conversations=5
)
```

### 4. Check Output
```bash
# View first conversation
head -1 generated_dataset.jsonl | python -m json.tool

# Count conversations
wc -l generated_dataset.jsonl

# Verify all have reasoning
grep '"has_reasoning": true' generated_dataset.jsonl | wc -l
```

---

## 📊 What Gets Generated

### For Each Page:
- **1 Multi-Turn Conversation** (all Q&A from that page)
- **3-5 Q&A Pairs** (questions AI generates, answers AI provides)
- **100% Reasoning** (every answer includes chain-of-thought)

### Example Entry:
```json
{
  "type": "multi_turn",
  "has_reasoning": true,
  "num_turns": 3,
  "conversations": [
    {
      "role": "user",
      "content": "What is the main concept?"
    },
    {
      "role": "assistant",
      "content": "Let me think through this step by step: [reasoning] → answer",
      "has_reasoning": true
    },
    ...
  ]
}
```

---

## 🔧 Customize Prompts

Edit `prompts.yaml`:

```yaml
# Make questions more specific to your domain
question_generation:
  prompt_qa: |
    Generate questions about this medical TEXT:
    {text}
    
    Questions should test clinical reasoning, not just facts.
    [return JSON array of questions]
```

---

## 📈 Expected Results

**400-page PDF** →
- ~25 chunks (pages)
- ~5 conversations per page
- = **~125 conversations**
- = **~400-500 Q&A pairs with reasoning**

---

## ❌ Common Issues

| Issue | Solution |
|-------|----------|
| `No module named prompts` | prompts.yaml must be in root directory |
| `has_reasoning: false` | Check cot_markers in prompts.yaml |
| Questions too generic | Modify question_generation prompt |
| JSON parsing error | Check LLM output format |

---

## ✅ Verification Checklist

- [ ] prompts.yaml exists and is valid YAML
- [ ] config.yaml has `prompts_file: "prompts.yaml"`
- [ ] First run generates conversations
- [ ] `head -1 dataset.jsonl | grep has_reasoning: true` works
- [ ] All conversations have "conversations" array with Q&A pairs
- [ ] All assistant messages have reasoning included

---

## 🚀 Next: Process Your Data

```bash
# Option 1: Single document
python main.py --source data/book.pdf --output dataset.jsonl

# Option 2: Batch processing
python main.py --source data/ --output dataset.jsonl

# Option 3: Check stats
python main.py --stats dataset.jsonl
```

---

## 💡 Key Differences from Old Version

| Old | New |
|-----|-----|
| Templates used | AI generates questions |
| Random format | Per-page multi-turn |
| Optional reasoning | Always reasoning |
| Separate prompts in config | Unified prompts.yaml |

---

**That's it!** You now have a reasoning-based dataset generator. 🎉
