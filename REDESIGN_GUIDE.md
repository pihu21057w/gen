# Reasoning-Based Dataset Generation - Complete Redesign

## 🎯 What Changed & Why

The previous template-based approach had a fundamental flaw: it treated PDF/book text as questions to ask the model, when they're actually **answers/content to understand**.

### Old Approach ❌
```
Template: "Explain the following topic in simple terms:\n{text}"
Result: Model explains text (redundant - text already IS the explanation)
```

### New Approach ✅
```
Step 1: LLM reads the text (answer)
Step 2: LLM generates relevant questions about it
Step 3: LLM answers those questions with reasoning
Result: Q&A pair with chain-of-thought reasoning
```

---

## 🏗️ New Architecture

### Three-Layer Generation System

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Question Generation                                │
│ - LLM reads text content                                     │
│ - Generates 3-5 diverse questions (easy→hard)               │
│ - JSON output: [{question, difficulty, type}, ...]          │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Answer Generation (with Reasoning)                 │
│ - For each question, generate detailed answer               │
│ - Always include chain-of-thought (COT) reasoning           │
│ - Format: "Let me think step by step:..." → explanation     │
└─────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Multi-Turn Conversation Assembly                   │
│ - Group all Q&A pairs from same page into ONE conversation  │
│ - Result: Coherent learning experience                      │
│ - Metadata: chunk info, reasoning markers, difficulty       │
└─────────────────────────────────────────────────────────────┘
          ↓
         JSONL Output (each entry is complete conversation)
```

---

## 📋 Key Improvements

### 1. **Text as Answer (Not Question)**
- Text from PDF is treated as knowledge/content
- Questions are generated TO test understanding OF that content
- Mimics how humans learn: read content → answer questions about it

### 2. **Per-Page Multi-Turn Conversations**
- Each page/chunk → ONE multi-turn conversation
- All Q&A pairs from that page are together
- Creates coherent learning flow
- Example:
  ```
  Page 1 → Conversation 1 (3-4 Q&A pairs)
  Page 2 → Conversation 2 (3-4 Q&A pairs)
  Page 3 → Conversation 3 (3-4 Q&A pairs)
  ```

### 3. **Always Reasoning**
- Every answer includes chain-of-thought
- Format: "Let me think through this step by step: [reasoning] → answer"
- Improves model reasoning capability during fine-tuning
- ✅ 100% reasoning entries (no exception)

### 4. **Smart Format Decisions**
- Model dynamically chooses format:
  - **Q&A**: For conceptual content
  - **Problem-Solving**: For detected math/physics/chemistry problems
  - **Analysis**: For complex topics

### 5. **Proper Prompt File**
- `prompts.yaml` - centralized, maintainable
- Separate from config
- Easy to customize for domain-specific generation
- All templates in one place

---

## 📁 File Structure

```
hpp/
├── prompts.yaml                          ← NEW: All generation prompts
├── configs/config.yaml                   ← Updated: prompts_file reference
├── src/
│   ├── dataset_generator.py              ← REWRITTEN: AI-driven generation
│   ├── pipeline.py                       ← Updated: prompts file integration
│   ├── text_preprocessor.py              ← Unchanged: chunking still works
│   └── llm_interface.py                  ← Unchanged
└── data/
    └── *.pdf (your documents)
```

---

## 🚀 How It Works

### Step 1: Load Document Page
```python
text = "Chapter 3: Quantum Mechanics. The Schrödinger equation describes..."
```

### Step 2: Generate Questions
```python
questions = generator.generate_questions_for_text(text)
# Returns:
[
  {
    "question": "What does the Schrödinger equation describe?",
    "difficulty": "easy",
    "type": "literal"
  },
  {
    "question": "How does this relate to wave-particle duality?",
    "difficulty": "hard",
    "type": "analytical"
  },
  ...
]
```

### Step 3: Generate Answers with Reasoning
```python
answer = generator.generate_answer_with_reasoning(question, text)
# Returns:
"""
Let me think through this step by step:

First, I need to understand what the Schrödinger equation is.
It's a fundamental equation in quantum mechanics that describes...

The key insight is that it relates the wave function to energy...

Therefore, the answer is: [complete answer with reasoning]
"""
```

### Step 4: Assemble Multi-Turn Conversation
```python
conversation = {
    "type": "multi_turn",
    "conversations": [
        {"role": "user", "content": "What does the Schrödinger equation describe?"},
        {"role": "assistant", "content": "Let me think through this... [reasoning] ..."},
        {"role": "user", "content": "How does this relate to wave-particle duality?"},
        {"role": "assistant", "content": "Let me analyze this systematically... [reasoning] ..."},
        ...
    ],
    "has_reasoning": true,  # ALWAYS true
    "format_decided": "multi_turn_qa"
}
```

### Step 5: Save to JSONL
```json
{
  "dataset_id": 0,
  "document_id": "quantum_book_ch3",
  "chunk_index": 2,
  "total_chunks": 15,
  "source": "data/quantum_mechanics.pdf",
  "type": "multi_turn",
  "has_reasoning": true,
  "format_decided": "multi_turn_qa",
  "num_turns": 3,
  "conversations": [...]
}
```

---

## 📊 Output Format

### Entry Structure
```json
{
  "dataset_id": 0,
  "document_id": "textbook_1",
  "chunk_index": 0,
  "total_chunks": 25,
  "source": "data/textbook.pdf",
  "type": "multi_turn",
  "system": "You are an expert educator showing clear reasoning.",
  "has_reasoning": true,
  "format_decided": "multi_turn_qa",
  "num_turns": 3,
  "conversations": [
    {
      "role": "user",
      "content": "What is the main concept here?"
    },
    {
      "role": "assistant",
      "content": "Let me think through this step by step:\n\nFirst, I need to identify the key concept...\n\nThe main points are:\n1. ...\n2. ...\n\nTherefore, the answer is: ...",
      "has_reasoning": true,
      "question_difficulty": "medium",
      "question_type": "literal"
    },
    ...
  ],
  "created_at": "2026-05-07T12:30:45"
}
```

---

## 🎓 Usage

### Basic Usage
```python
from src.pipeline import create_pipeline

# Create and run pipeline
pipeline = create_pipeline('configs/config.yaml')
pipeline.initialize_model()
pipeline.initialize_preprocessor()
pipeline.initialize_dataset_generator()

# Process a PDF
conversations = pipeline.process_document(
    'data/textbook.pdf',
    document_id='textbook_1',
    num_conversations=10  # Approx conversations per page
)
```

### Check Results
```bash
# View first entry
head -1 generated_dataset.jsonl | python -m json.tool

# Count entries
wc -l generated_dataset.jsonl

# Verify all have reasoning
grep -c '"has_reasoning": true' generated_dataset.jsonl
```

---

## 🔧 Customization

### Modify Prompts

Edit `prompts.yaml`:

```yaml
question_generation:
  prompt_qa: |
    Analyze this TEXT and generate QUESTIONS for finetuning a model.
    
    TEXT:
    {text}
    
    Create questions that test deep understanding (not surface facts).
    Vary difficulty from beginner to expert.
    
    Format: JSON array
    [
      {"question": "...", "difficulty": "easy|medium|hard", "type": "literal|inferential|analytical"},
      ...
    ]
```

### Custom Answer Format

```yaml
answer_generation:
  prompt_with_reasoning: |
    QUESTION: {question}
    CONTEXT: {text}
    
    Provide a detailed educational answer.
    ALWAYS use this format:
    
    Let me think through this step by step:
    1. First step of reasoning
    2. Second step
    3. Final conclusion
    
    Therefore, the answer is: [complete answer]
```

---

## 💡 Why This Works Better

### For Fine-Tuning
- ✅ Model learns to generate questions from content
- ✅ Model learns to provide reasoned answers
- ✅ Complete reasoning chain in every response
- ✅ Coherent conversations (not random templates)

### For Quality
- ✅ Questions match content difficulty
- ✅ Answers reference actual text
- ✅ No template repetition
- ✅ Reasoning markers consistent

### For Scale
- ✅ Works with 1-page excerpts
- ✅ Works with 400+ page books (auto-chunked)
- ✅ Each page becomes learning module
- ✅ Preserves semantic coherence

---

## 🔄 Comparison: Old vs New

| Aspect | Old (Template) | New (AI-Driven) |
|--------|---|---|
| **Text Role** | Prompt for explanation | Content to understand |
| **Questions** | From templates | AI-generated, diverse |
| **Answers** | May lack reasoning | Always with reasoning |
| **Conversation** | Random template choice | One coherent multi-turn per page |
| **Problem Detection** | Optional extra | Integrated decision making |
| **Customization** | Hardcoded templates | prompts.yaml config |
| **Quality** | Repetitive | Organic, adaptive |

---

## ⚙️ Configuration

### In `configs/config.yaml`

```yaml
dataset:
  output_file: "generated_dataset.jsonl"
  prompts_file: "prompts.yaml"  # ← Prompts configuration
  num_conversations_per_doc: 5   # Questions per page
```

### In `prompts.yaml`

- **question_generation**: How to generate questions
- **answer_generation**: How to generate answers
- **multi_turn_generation**: How to build conversations
- **system_instructions**: Educator guidelines
- **cot_markers**: Reasoning format markers
- **keywords**: Pattern matching for reasoning

---

## 📈 Expected Output

### Per 400-Page PDF
- ~25-30 chunks (with smart chunking)
- ~5 conversations per chunk
- = ~125-150 multi-turn conversations
- = ~500-600 Q&A pairs with reasoning
- Each pair includes full chain-of-thought

### Dataset Statistics
```
Total entries: 150
Reasoning entries: 150 (100%)
Multi-turn entries: 150 (100%)
Average Q&A pairs per entry: 3-4
Total file size: ~50-100 MB
Average tokens per answer: 300-500
```

---

## 🚀 Best Practices

### 1. Question Generation
- Let LLM generate diverse difficulty levels
- Mix literal and analytical questions
- Don't force specific question types

### 2. Answer Generation
- Always require reasoning prefix
- Check for COT markers in output
- Fallback if reasoning missing

### 3. Multi-Turn Assembly
- Keep Q&A pairs from same page together
- Maintain conversation flow
- Don't shuffle pairs across pages

### 4. Chunking
- Use smart semantic chunking
- Preserve concept boundaries
- Maintain 300-char overlap

---

## 🐛 Troubleshooting

### Issue: Questions are generic
**Solution**: Adjust prompts.yaml question generation prompt for domain-specific questions

### Issue: Reasoning missing
**Solution**: Check has_reasoning field, review cot_markers in prompts.yaml

### Issue: Answers too long
**Solution**: Reduce max_tokens in llm_interface or adjust answer prompt

### Issue: JSON parsing fails
**Solution**: Check LLM output format, update _parse_json_response error handling

---

## 📝 Example: Complete Workflow

```python
# 1. Load pipeline
from src.pipeline import create_pipeline
pipeline = create_pipeline('configs/config.yaml')

# 2. Initialize components
pipeline.initialize_model()
pipeline.initialize_preprocessor()
pipeline.initialize_dataset_generator()

# 3. Process document
conversations = pipeline.process_document(
    'data/quantum_mechanics.pdf',
    document_id='quantum_1',
    num_conversations=5  # per page
)

# 4. Check stats
stats = pipeline.dataset_generator.get_dataset_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Reasoning entries: {stats['reasoning_entries']}")
print(f"File size: {stats['file_size_mb']:.2f} MB")

# 5. Inspect first entry
import json
with open('generated_dataset.jsonl') as f:
    first_entry = json.loads(f.readline())
    print(f"Entry type: {first_entry['type']}")
    print(f"Has reasoning: {first_entry['has_reasoning']}")
    print(f"Num turns: {first_entry['num_turns']}")
```

---

## ✨ Key Features Summary

✅ **AI-Generated Questions** - Not templates
✅ **Always Reasoning** - Every response has COT
✅ **Per-Page Conversations** - Coherent learning modules
✅ **Proper Prompt File** - `prompts.yaml` management
✅ **Smart Format Decisions** - Q&A or problem-solving
✅ **Error Handling** - Graceful fallbacks
✅ **Statistics Tracking** - Reasoning percentage monitoring
✅ **Flexible Configuration** - Easy customization

---

**Version**: 3.0.0 (Redesigned)  
**Status**: ✅ Production Ready  
**Last Updated**: May 2026  
**Architecture**: AI-Driven Reasoning Generation
