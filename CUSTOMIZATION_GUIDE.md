# Customization Guide - Qwen3, Smart Chunking & Problem Detection

## 🎯 What's New

Your pipeline has been enhanced with powerful features for better dataset generation:

### 1. **Qwen2 Model Support (Better Reasoning)**
- Default model changed from Llama-2-7B to **Qwen/Qwen2-7B**
- Qwen excels at reasoning, problem-solving, and complex analysis
- Available variants:
  - `Qwen/Qwen2-1.5B` - Fast (1.5B)
  - `Qwen/Qwen2-7B` - Balanced (7B) ⭐ **Default**
  - `Qwen/Qwen2-14B` - Better (14B)
  - `Qwen/Qwen2-32B` - Best (32B)
  - `Qwen/Qwen2-72B` - Premium (72B)

### 2. **Smart Chunking for Large Documents**
- Intelligently splits long documents (e.g., 400+ page PDFs)
- Preserves concept boundaries (doesn't split mid-theory)
- Overlapping chunks for context continuity
- Detects and preserves multi-page theories

### 3. **Chain-of-Thought (COT) Integration**
- Automatic COT entry generation (at least 1 per document)
- Configurable COT percentage (default: 70%)
- Forces clear thinking process in responses
- Better reasoning quality

### 4. **Problem Detection & Solving**
- Auto-detects math, physics, chemistry, biology problems
- Extracts questions from documents
- Generates step-by-step solutions
- Solves problems with full working/reasoning

### 5. **Custom LLM Prompts**
- Define custom prompts for different conversation types
- Use via CLI or configuration
- Placeholders: `{text}` for content, `{question}` for queries

---

## 🔧 Configuration

### Updated `configs/config.yaml`

```yaml
# Model Configuration (NEW: Qwen)
model:
  name: "Qwen/Qwen2-7B"  # Changed to Qwen
  device: "cuda"
  dtype: "float16"
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9

# Custom Prompts (NEW)
llm_prompts:
  multi_turn_explanation: "Explain the following content in detail with examples:\n{text}\n\nProvide a clear explanation suitable for learning."
  problem_solving: "Solve this problem step by step with full working:\n{text}\n\nShow all intermediate steps and reasoning."
  cot_instruction: "Let me think through this step by step:\n"

# Smart Chunking (NEW)
processing:
  use_smart_chunking: true          # Enable intelligent chunking
  chunk_strategy: "semantic"         # semantic, fixed, or sentence-based
  chunk_size: 1500                   # Target chunk size
  chunk_overlap: 300                 # Overlap for context
  min_chunk_size: 200                # Minimum chunk size
  
  preserve_concept_boundaries: true  # Don't split mid-concept
  concept_keywords:
    - "theorem"
    - "definition"
    - "law"
    - "principle"
    - "formula"
  
  # Problem Detection (NEW)
  detect_problems: true
  problem_types:
    - "math"
    - "physics"
    - "chemistry"
    - "biology"
    - "exercise"
    - "question"

# Conversation Configuration (UPDATED)
conversation:
  types: ["multi_turn", "single_turn", "problem_solving"]  # NEW: problem_solving
  include_reasoning: true
  reasoning_format: "chain_of_thought"
  
  force_cot_entry: true              # NEW: Always add COT
  cot_percentage: 0.7                # NEW: 70% COT conversations
  solve_detected_problems: true       # NEW: Solve problems automatically
```

---

## 🚀 Usage Examples

### 1. **Use Qwen Model (Default)**
```bash
# Uses Qwen/Qwen2-7B by default
python main.py --source data/ --output dataset.jsonl
```

### 2. **Use Different Qwen Size**
```bash
# Use faster 1.5B
python main.py --source data/ --model "Qwen/Qwen2-1.5B" --output dataset.jsonl

# Use better 14B
python main.py --source data/ --model "Qwen/Qwen2-14B" --output dataset.jsonl
```

### 3. **Custom Prompt for Explanations**
```bash
python main.py --source data/ \
  --custom-prompt "Explain {text} in mathematical terms with formulas and proofs." \
  --output dataset.jsonl
```

### 4. **Generate Only COT Conversations**
```bash
# Force all conversations to have chain-of-thought
python main.py --source data/ --cot-only --output dataset.jsonl
```

### 5. **Process Large PDF (400+ pages)**
```bash
# Smart chunking automatically handles this
# Documents are split intelligently preserving concepts
python main.py --source large_book.pdf --conversations 10 --output dataset.jsonl
```

### 6. **Detect and Solve Math Problems**
```bash
# Automatically finds math problems and generates solutions
python main.py --source math_textbook.pdf --output dataset.jsonl
```

---

## 🐍 Python API Examples

### Basic Usage with Qwen
```python
from src.pipeline import create_pipeline

pipeline = create_pipeline('configs/config.yaml')

# Now uses Qwen/Qwen2-7B by default
pipeline.process_document('data/document.pdf', num_conversations=10)
```

### Custom Prompts
```python
# Override prompts
pipeline.config['llm_prompts']['multi_turn_explanation'] = \
    "Explain {text} focusing on practical applications and real-world examples."

# Re-initialize dataset generator to apply changes
pipeline.initialize_dataset_generator()

pipeline.process_document('data/document.pdf')
```

### Smart Chunking with Problem Detection
```python
from src.text_preprocessor import TextPreprocessor

preprocessor = TextPreprocessor(pipeline.config['processing'])

# Smart chunk with problem detection
chunks = preprocessor.smart_chunk_text(your_text, chunk_size=1500, overlap=300)

for chunk_data in chunks:
    content = chunk_data['content']
    problems = chunk_data['problems']  # Detected problems
    
    print(f"Chunk size: {len(content)}")
    print(f"Problems found: {len(problems)}")
    for problem in problems:
        print(f"  - {problem['type']}: {problem['content']}")
```

### Generate Problem Solutions
```python
conversation = pipeline.dataset_generator.conv_generator.generate_problem_solving_conversation(
    problem_text="Solve: x² + 5x + 6 = 0",
    problem_type="math"
)

# Output includes step-by-step solution
print(conversation['conversations'])
```

---

## 📊 Output Format (Updated)

JSONL entries now include new fields:

```json
{
  "dataset_id": 0,
  "document_id": "doc1",
  "chunk_index": 0,
  "total_chunks": 5,
  "source": "data/document.pdf",
  "type": "multi_turn",
  "template": "explanation_follow_up",
  "has_cot": true,
  "has_reasoning": true,
  "problem_info": [
    {
      "type": "math",
      "content": "Solve x² + 5x + 6 = 0",
      "requires_solving": true
    }
  ],
  "conversations": [
    {
      "role": "user",
      "content": "Explain this content..."
    },
    {
      "role": "assistant",
      "content": "Let me think through this step by step: First, I observe..."
    }
  ]
}
```

---

## 🎯 Key Features Explained

### Smart Chunking

**Problem**: Large documents (400 pages) can't fit in context window
**Solution**: Intelligent splitting that preserves meaning

```python
# Smart chunking preserves:
✓ Concept boundaries (don't split theorem mid-statement)
✓ Context with overlap (300 char overlap)
✓ Paragraph continuity (complete thoughts)
✗ Eliminates: too-small fragments (< 200 chars)
```

### Problem Detection

**Automatically detects**:
- Math: "Solve quadratic equation", "Find derivative"
- Physics: "velocity", "force", "Newton's laws"
- Chemistry: "molecular weight", "pH", "bonding"
- Biology: "photosynthesis", "DNA", "evolution"
- Generic: Any question mark detected

### Chain-of-Thought (COT)

**Forces model to**:
1. Think step-by-step
2. Show reasoning process
3. Arrive at conclusions
4. Improves reasoning capability

**Example Output**:
```
Let me think through this step by step:
First, I need to understand the problem...
Then, I'll identify the key concepts...
Next, I'll apply the relevant formulas...
Finally, I'll verify my answer...
```

### Custom Prompts

**Use cases**:
- Domain-specific language
- Different explanation styles
- Specialized problem-solving approaches
- Language preferences

---

## 📈 Performance Tips

### For Best Reasoning (Qwen-7B on T4)
```yaml
model:
  name: "Qwen/Qwen2-7B"
  temperature: 0.7  # Balanced
  
conversation:
  force_cot_entry: true    # Always COT
  cot_percentage: 0.8      # 80% COT
  include_reasoning: true
```

### For Speed (Qwen-1.5B on T4)
```yaml
model:
  name: "Qwen/Qwen2-1.5B"
  temperature: 0.6  # More deterministic
  
conversation:
  cot_percentage: 0.5      # 50% COT
  solve_detected_problems: false  # Skip complex solving
```

### For Quality (Qwen-32B on RTX 3090)
```yaml
model:
  name: "Qwen/Qwen2-32B"
  temperature: 0.8  # More creative
  
conversation:
  force_cot_entry: true
  cot_percentage: 1.0      # All COT
  solve_detected_problems: true
```

---

## 🔍 Detecting Problems

### Math Problems Detected
- Quadratic equations: `x² + 5x + 6 = 0`
- Calculus: `Find the derivative of...`
- Linear algebra: `Solve the system of equations...`
- Geometry: `Calculate the area...`

### Physics Problems Detected
- Kinematics: velocity, acceleration, force
- Dynamics: Newton's laws, momentum
- Energy: work, power, kinetic energy
- Waves: frequency, wavelength, resonance

### Chemistry Problems Detected
- Stoichiometry: molecular weight, moles
- Bonding: ionic, covalent, hydrogen bonds
- Reactions: oxidation-reduction, equilibrium
- Solutions: pH, concentration, buffers

---

## 📚 Configuration Files

### Create configs for different scenarios:

**configs/config_qwen_7b.yaml** (Balanced):
```yaml
model:
  name: "Qwen/Qwen2-7B"
```

**configs/config_qwen_14b.yaml** (Better):
```yaml
model:
  name: "Qwen/Qwen2-14B"
```

**configs/config_cot_focus.yaml** (Reasoning):
```yaml
conversation:
  force_cot_entry: true
  cot_percentage: 1.0
```

**configs/config_problem_solving.yaml** (Problems):
```yaml
conversation:
  solve_detected_problems: true
  types: ["problem_solving", "multi_turn"]
```

Then use:
```bash
python main.py --config configs/config_problem_solving.yaml --source data/
```

---

## 🎓 Learning Resources

- **Qwen Models**: https://huggingface.co/Qwen
- **Chain-of-Thought**: https://arxiv.org/abs/2201.11903
- **Problem Solving**: https://arxiv.org/abs/2205.14846

---

## ✅ Validation

### Check Generated Dataset

```bash
# View statistics including COT %
python main.py --stats outputs/dataset.jsonl

# Validate quality
python main.py --validate outputs/dataset.jsonl

# Look for problems detected
grep "problem_info" outputs/dataset.jsonl | head -5
```

### Expected Output
```
Total Entries: 500
With COT: 350 (70%)
Problem-solving: 75 (15%)
Average messages per conversation: 6.5
```

---

## 🚀 Next Steps

1. **Try Qwen**: Run with default config to experience better reasoning
2. **Test Smart Chunking**: Process a large PDF
3. **Custom Prompts**: Define domain-specific prompts
4. **Problem Solving**: Generate solutions for textbooks
5. **Mix Strategies**: Combine COT + problem solving

---

## 📞 Troubleshooting

### Model Download Issues
```bash
export HF_HOME=/path/to/large/drive
python main.py --source data/ --model "Qwen/Qwen2-7B"
```

### Out of Memory
```bash
# Use smaller Qwen
python main.py --model "Qwen/Qwen2-1.5B"
```

### Problems Not Detected
```yaml
# Check configuration
processing:
  detect_problems: true
  problem_types: ["math", "physics", "chemistry", "biology"]
```

---

**Version**: 2.0.0  
**Last Updated**: January 2024  
**Status**: ✅ Enhanced & Production Ready
