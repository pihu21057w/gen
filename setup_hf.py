"""
HF Token configuration for accessing gated models like Llama-2
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def setup_hf_token():
    """Setup Hugging Face token for accessing gated models"""
    print("\n" + "="*70)
    print("HUGGING FACE TOKEN SETUP")
    print("="*70)
    
    print("""
To use Llama-2 or other gated models, you need:

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with 'read' access
3. Accept the license for the model (e.g., meta-llama/Llama-2-7b-hf)

Then run:
    huggingface-cli login
    
Or set environment variable:
    export HF_TOKEN=your_token_here
""")
    
    import os
    token = os.environ.get('HF_TOKEN')
    if token:
        print(f"✓ HF_TOKEN is set: {token[:10]}...")
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            user_info = api.get_current_user_info(token=token)
            print(f"✓ Authenticated as: {user_info.name}")
        except Exception as e:
            print(f"✗ Error authenticating: {str(e)}")
    else:
        print("✗ HF_TOKEN not set")


def authenticate():
    """Authenticate with Hugging Face"""
    try:
        from huggingface_hub import login
        print("\nLogging in to Hugging Face...")
        login()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Hugging Face authentication')
    parser.add_argument('--login', action='store_true', help='Login to Hugging Face')
    parser.add_argument('--check', action='store_true', help='Check current authentication')
    
    args = parser.parse_args()
    
    if args.login:
        authenticate()
    else:
        setup_hf_token()
        if not args.check:
            print("\nRun: python setup_hf.py --login")
