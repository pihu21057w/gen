"""
Google Colab specific setup and execution script
"""

import subprocess
import sys
from typing import Optional


def install_dependencies():
    """Install required dependencies for Google Colab"""
    print("Installing dependencies...")
    
    packages = [
        'pyyaml',
        'transformers',
        'torch',
        'accelerate',
        'PyPDF2',
        'requests',
        'beautifulsoup4',
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
    
    print("Dependencies installed successfully!")


def setup_colab_environment():
    """Setup Google Colab environment"""
    print("\n" + "="*70)
    print("GOOGLE COLAB SETUP")
    print("="*70)
    
    print("\n1. Installing dependencies...")
    install_dependencies()
    
    print("\n2. Checking GPU availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA Version: {torch.version.cuda}")
            print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            print("✗ No GPU detected. CPU-only mode (slow)")
    except Exception as e:
        print(f"Error checking GPU: {str(e)}")
    
    print("\n3. Recommending model configuration...")
    import os
    if 'COLAB_RELEASE_TAG' in os.environ:
        # We're in Colab with T4 GPU (typically)
        print("Running on Google Colab T4 GPU")
        print("Recommended model: meta-llama/Llama-2-7b-hf")
        print("Dtype: float16")
        print("Batch size: 4")
        print("\nNote: You may need to accept license on Hugging Face")
        print("See: https://huggingface.co/meta-llama/Llama-2-7b-hf")
    
    print("\n" + "="*70)


def colab_quick_start():
    """Quick start code for Colab"""
    print("\n" + "="*70)
    print("QUICK START CODE FOR GOOGLE COLAB")
    print("="*70)
    
    code = '''
# 1. Mount Google Drive (optional, for input/output)
from google.colab import drive
drive.mount('/content/drive')

# 2. Clone or download the pipeline
import subprocess
subprocess.run(["git", "clone", "YOUR_REPO_URL", "pipeline"], check=True)
import os
os.chdir("pipeline")

# 3. Run setup
exec(open("setup_colab.py").read())
setup_colab_environment()

# 4. Process documents
from src.pipeline import create_pipeline

# Create pipeline with 7B model (recommended for T4)
pipeline = create_pipeline('configs/config.yaml')

# Process a document
pipeline.process_document(
    source='data/sample.pdf',
    document_id='doc1',
    num_conversations=5
)

# Check status
status = pipeline.get_status()
print(f"Generated {status['dataset_entries']} entries")

# Save to Drive
import shutil
shutil.copy('generated_dataset.jsonl', '/content/drive/My Drive/dataset.jsonl')
'''
    
    print(code)


def main():
    """Main setup function"""
    setup_colab_environment()
    colab_quick_start()


if __name__ == '__main__':
    main()
