"""
Example: Complete Qwen + Smart Chunking + Problem Detection Pipeline
====================================================================

This example demonstrates:
1. Using Qwen/Qwen2-7B for better reasoning
2. Smart chunking for large documents (e.g., 400+ page PDFs)
3. Automatic problem detection and solving
4. Chain-of-Thought (COT) forcing
5. Custom prompt integration

Run this with: python examples_qwen_advanced.py
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from pipeline import create_pipeline
from text_preprocessor import TextPreprocessor
from llm_interface import ModelRecommendations


def example_1_basic_qwen_setup():
    """Example 1: Basic setup with Qwen model"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Qwen Setup")
    print("="*70)
    
    # Create pipeline with default Qwen
    pipeline = create_pipeline('configs/config.yaml')
    
    print(f"✓ Model: {pipeline.config['model']['name']}")
    print(f"✓ Device: {pipeline.config['model']['device']}")
    print(f"✓ Dtype: {pipeline.config['model']['dtype']}")
    print(f"✓ Max tokens: {pipeline.config['model']['max_tokens']}")
    
    # Show model recommendations
    print("\nAvailable Qwen Models:")
    for hw, rec in ModelRecommendations.RECOMMENDATIONS.items():
        print(f"  - {hw}: {rec['model']} ({rec['description']})")


def example_2_smart_chunking():
    """Example 2: Smart chunking for large documents"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Smart Chunking")
    print("="*70)
    
    config_path = 'configs/config.yaml'
    pipeline = create_pipeline(config_path)
    
    # Sample long text (simulating 400-page PDF)
    long_text = """
    Chapter 1: Introduction to Quantum Mechanics
    
    The Schrödinger equation is the fundamental equation of quantum mechanics. 
    It describes how the quantum state of a physical system changes over time.
    
    The time-dependent Schrödinger equation is:
    iℏ ∂ψ/∂t = Ĥψ
    
    where ψ is the wave function, Ĥ is the Hamiltonian operator, ℏ is the 
    reduced Planck constant, and i is the imaginary unit.
    
    The Hamiltonian represents the total energy of the system:
    Ĥ = T̂ + V̂
    
    where T̂ is the kinetic energy operator and V̂ is the potential energy operator.
    
    Important concepts:
    - Wave-particle duality
    - Uncertainty principle (Δx·Δp ≥ ℏ/2)
    - Superposition principle
    - Measurement and collapse
    
    Chapter 2: The Harmonic Oscillator
    
    The quantum harmonic oscillator is one of the most important solved problems 
    in quantum mechanics. The potential is:
    
    V(x) = (1/2)mω²x²
    
    The energy levels are:
    En = ℏω(n + 1/2), where n = 0, 1, 2, ...
    
    The ground state energy is E₀ = (1/2)ℏω, which is never zero due to 
    zero-point energy.
    """ * 10  # Simulate very long text
    
    # Use smart chunking
    chunking_config = pipeline.config['processing']
    preprocessor = TextPreprocessor(chunking_config)
    
    chunks = preprocessor.smart_chunk_text(
        long_text,
        chunk_size=1500,
        overlap=300
    )
    
    print(f"Original text length: {len(long_text)} characters")
    print(f"Number of chunks: {len(chunks)}")
    print(f"\nChunk details:")
    
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        content = chunk['content']
        problems = chunk['problems']
        print(f"\n  Chunk {i+1}:")
        print(f"    - Size: {len(content)} characters")
        print(f"    - Problems detected: {len(problems)}")
        if problems:
            for p in problems:
                print(f"      • {p['type']}: {p['content'][:50]}...")


def example_3_problem_detection():
    """Example 3: Automatic problem detection"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Problem Detection")
    print("="*70)
    
    config_path = 'configs/config.yaml'
    pipeline = create_pipeline(config_path)
    preprocessor = TextPreprocessor(pipeline.config['processing'])
    
    # Sample text with various problems
    sample_text = """
    Math Problem 1: Solve the quadratic equation x² + 5x + 6 = 0
    
    Physics Problem: A ball is thrown vertically with initial velocity 20 m/s. 
    Calculate the maximum height reached (g = 10 m/s²).
    
    Chemistry Problem: What is the pH of a 0.1M HCl solution?
    
    Biology Exercise: Describe the process of photosynthesis in plant cells.
    
    Question: What is the difference between DNA and RNA?
    """
    
    problems = preprocessor.detect_problems_in_text(sample_text)
    
    print(f"Text length: {len(sample_text)} characters")
    print(f"Problems detected: {len(problems)}\n")
    
    for i, problem in enumerate(problems, 1):
        print(f"{i}. Type: {problem['type'].upper()}")
        print(f"   Content: {problem['content']}")
        print(f"   Requires solving: {problem['requires_solving']}\n")


def example_4_custom_prompts():
    """Example 4: Using custom prompts"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Prompts for Domain-Specific Responses")
    print("="*70)
    
    config_path = 'configs/config.yaml'
    pipeline = create_pipeline(config_path)
    
    # Show current prompts
    print("Default prompts in config:")
    for key, prompt in pipeline.config['llm_prompts'].items():
        if isinstance(prompt, str) and len(prompt) < 100:
            print(f"\n  {key}:")
            print(f"    {prompt}")
    
    # Example of custom prompt override
    custom_prompts = {
        'math_focused': "Solve this mathematical problem with full derivations and formulas:\n{text}",
        'physics_focused': "Explain this physics concept with real-world applications:\n{text}",
        'coding_focused': "Explain this code and provide best practices:\n{text}",
    }
    
    print("\n\nCustom prompts you can use:")
    for name, prompt in custom_prompts.items():
        print(f"\n  {name}:")
        print(f"    {prompt}")


def example_5_cot_forcing():
    """Example 5: Chain-of-Thought forcing"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Chain-of-Thought (COT) Forcing")
    print("="*70)
    
    config_path = 'configs/config.yaml'
    pipeline = create_pipeline(config_path)
    
    cot_config = pipeline.config['conversation']
    
    print(f"COT Configuration:")
    print(f"  - Force COT entry: {cot_config['force_cot_entry']}")
    print(f"  - COT percentage: {cot_config['cot_percentage']*100}%")
    print(f"  - Solve detected problems: {cot_config['solve_detected_problems']}")
    
    print(f"\nCOT Instruction Template:")
    print(f"  '{pipeline.config['llm_prompts']['cot_instruction']}'")
    
    print(f"\nExample output WITH COT:")
    print("""
    Let me think through this step by step:
    1. First, I need to understand what's being asked
    2. Then, I'll identify the key information
    3. Next, I'll apply relevant concepts
    4. Finally, I'll derive the answer
    
    Therefore, the answer is...
    """)


def example_6_integration():
    """Example 6: Full integration example"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Full Integration")
    print("="*70)
    
    config_path = 'configs/config.yaml'
    pipeline = create_pipeline(config_path)
    
    # Sample text
    sample_document = """
    Linear Algebra: Systems of Equations
    
    Problem: Solve the system of linear equations:
    2x + 3y = 8
    4x - y = 2
    
    Solution approach:
    Using substitution or elimination method...
    
    Key concepts covered:
    - Matrix representation
    - Gaussian elimination
    - Back substitution
    - Solution verification
    
    Related physics problems:
    Calculate the velocity and acceleration of an object in motion.
    
    Chemistry: Calculate molar mass
    """
    
    print(f"Processing document with:")
    print(f"  ✓ Model: {pipeline.config['model']['name']}")
    print(f"  ✓ Smart chunking: {pipeline.config['processing']['use_smart_chunking']}")
    print(f"  ✓ Problem detection: {pipeline.config['processing']['detect_problems']}")
    print(f"  ✓ COT forcing: {pipeline.config['conversation']['force_cot_entry']}")
    
    # Simulate processing (without actually calling LLM)
    preprocessor = TextPreprocessor(pipeline.config['processing'])
    chunks = preprocessor.smart_chunk_text(sample_document)
    
    print(f"\nResults:")
    print(f"  - Document chunks: {len(chunks)}")
    
    total_problems = sum(len(c['problems']) for c in chunks)
    print(f"  - Total problems detected: {total_problems}")
    
    problem_types = {}
    for chunk in chunks:
        for problem in chunk['problems']:
            ptype = problem['type']
            problem_types[ptype] = problem_types.get(ptype, 0) + 1
    
    if problem_types:
        print(f"  - Problem breakdown:")
        for ptype, count in problem_types.items():
            print(f"      • {ptype}: {count}")


def show_usage_commands():
    """Show CLI usage commands"""
    print("\n" + "="*70)
    print("CLI USAGE COMMANDS")
    print("="*70)
    
    commands = [
        ("Basic with Qwen", "python main.py --source data/ --output dataset.jsonl"),
        ("Custom prompt", "python main.py --source data/ --custom-prompt 'Explain {text} mathematically' --output dataset.jsonl"),
        ("COT only", "python main.py --source data/ --cot-only --output dataset.jsonl"),
        ("Different model", "python main.py --source data/ --model 'Qwen/Qwen2-14B' --output dataset.jsonl"),
        ("Large PDF", "python main.py --source large_book.pdf --conversations 20 --output dataset.jsonl"),
        ("With recommendations", "python main.py --recommendations"),
    ]
    
    for desc, cmd in commands:
        print(f"\n{desc}:")
        print(f"  $ {cmd}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "QWEN + SMART CHUNKING + PROBLEM DETECTION" + " "*8 + "║")
    print("║" + " "*25 + "Complete Example Suite" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        example_1_basic_qwen_setup()
        example_2_smart_chunking()
        example_3_problem_detection()
        example_4_custom_prompts()
        example_5_cot_forcing()
        example_6_integration()
        show_usage_commands()
        
        print("\n" + "="*70)
        print("✓ All examples completed successfully!")
        print("="*70)
        
        print("\n📚 Next Steps:")
        print("1. Review CUSTOMIZATION_GUIDE.md for detailed documentation")
        print("2. Try: python main.py --recommendations")
        print("3. Process your first document with Qwen")
        print("4. Inspect generated dataset.jsonl for quality")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
