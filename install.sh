#!/bin/bash

# Installation and Setup Script for Dataset Generation Pipeline

set -e  # Exit on error

echo "========================================"
echo "Dataset Generation Pipeline - Setup"
echo "========================================"
echo ""

# Detect OS
OS_TYPE=$(uname -s)
echo "Detected OS: $OS_TYPE"

# Check Python version
echo ""
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
if [ "$OS_TYPE" == "Darwin" ] || [ "$OS_TYPE" == "Linux" ]; then
    source venv/bin/activate
elif [ "$OS_TYPE" == "MINGW64_NT" ] || [ "$OS_TYPE" == "MSYS_NT" ]; then
    source venv/Scripts/activate
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel -q
echo "✓ pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Check CUDA availability
echo ""
echo "Checking GPU availability..."
python -c "
import torch
if torch.cuda.is_available():
    print(f'✓ GPU Found: {torch.cuda.get_device_name(0)}')
    print(f'  CUDA Version: {torch.version.cuda}')
    print(f'  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')
else:
    print('⚠ No GPU found. CPU mode will be slow.')
" || echo "⚠ Could not check GPU"

# Verify installation
echo ""
echo "Verifying installation..."
python -c "
import sys
sys.path.insert(0, 'src')
from pipeline import DatasetPipeline
from text_preprocessor import TextPreprocessor
from data_loaders import DataLoaderFactory
print('✓ All packages imported successfully')
" || echo "❌ Installation verification failed"

# Setup Hugging Face token
echo ""
echo "Setup Instructions:"
echo "1. Visit https://huggingface.co/settings/tokens"
echo "2. Create a new token with 'read' access"
echo "3. Accept license for meta-llama/Llama-2-7b-hf"
echo "4. Run: python setup_hf.py --login"
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data outputs logs
echo "✓ Directories created"

# Show next steps
echo ""
echo "========================================"
echo "Setup Complete! ✓"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
if [ "$OS_TYPE" == "Darwin" ] || [ "$OS_TYPE" == "Linux" ]; then
    echo "   source venv/bin/activate"
else
    echo "   venv\\Scripts\\activate"
fi
echo ""
echo "2. Setup Hugging Face token:"
echo "   python setup_hf.py --login"
echo ""
echo "3. Add your documents to the 'data' folder"
echo ""
echo "4. Start generating dataset:"
echo "   python main.py --recommendations"
echo "   python main.py --source data/ --output outputs/dataset.jsonl"
echo ""
echo "See GETTING_STARTED.md for more information."
echo ""
