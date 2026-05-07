@echo off
REM Installation and Setup Script for Windows

echo ========================================
echo Dataset Generation Pipeline - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+
    exit /b 1
)

echo Detected OS: Windows
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel -q
echo pip upgraded

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt -q
echo Dependencies installed

REM Check CUDA
echo.
echo Checking GPU availability...
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}') if torch.cuda.is_available() else print('No GPU detected - CPU mode')"

REM Create directories
echo.
echo Creating directories...
if not exist "data" mkdir data
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
echo Directories created

REM Show next steps
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Setup Hugging Face token:
echo    python setup_hf.py --login
echo.
echo 3. Add your documents to the 'data' folder
echo.
echo 4. Start generating dataset:
echo    python main.py --recommendations
echo    python main.py --source data/ --output outputs/dataset.jsonl
echo.
echo See GETTING_STARTED.md for more information.
echo.
